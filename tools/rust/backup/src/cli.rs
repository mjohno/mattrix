use std::env;
use std::fs;
use std::path::PathBuf;

use serde_json::{json, Value};

use crate::archive::{build_archive_filename, create_archive};
use crate::cleanup::{filter_cleanup_candidates, matching_staged_archives};
use crate::config::{
    load_config, resolve_loose, validate_service_account_file, validate_target_directory,
    BackupConfig,
};
use crate::drive::{GoogleDriveUploader, Uploader};
use crate::error::{BackupError, Result};
use crate::output::{structured_error, ArchiveOutput, DryRunUploadOutput, UploadOutput};

#[derive(Debug, Clone)]
pub enum Command {
    Backup(BackupArgs),
    Cleanup(CleanupArgs),
}

impl Command {
    #[must_use]
    pub const fn name(&self) -> &'static str {
        match self {
            Self::Backup(_) => "backup",
            Self::Cleanup(_) => "cleanup",
        }
    }
}

#[derive(Debug, Clone)]
pub struct BackupArgs {
    pub config: PathBuf,
    pub log_level: String,
    pub target_directory: Option<PathBuf>,
    pub dry_run: bool,
    pub keep_archive: bool,
}

#[derive(Debug, Clone)]
pub struct CleanupArgs {
    pub config: PathBuf,
    pub log_level: String,
    pub dry_run: bool,
    pub older_than_days: u64,
    pub keep_latest: usize,
}

#[must_use]
pub fn main_result() -> i32 {
    let args = env::args().skip(1).collect::<Vec<_>>();
    if args.iter().any(|arg| arg == "--help" || arg == "-h") {
        println!("{}", help_text());
        return 0;
    }
    match parse_args(&args) {
        Ok(command) => {
            let uploader = GoogleDriveUploader;
            let (code, payload) = run(&command, &uploader);
            print_json(&payload);
            code
        }
        Err(error) => {
            let payload = structured_error("backup", &error);
            print_json(&payload);
            1
        }
    }
}

fn print_json<T: serde::Serialize>(payload: &T) {
    let text = serde_json::to_string_pretty(payload).unwrap_or_else(|_| "{}".to_owned());
    println!("{text}");
}

pub fn run(command: &Command, uploader: &dyn Uploader) -> (i32, Value) {
    match run_inner(command, uploader) {
        Ok(payload) => (0, payload),
        Err(error) => (1, json!(structured_error(command.name(), &error))),
    }
}

fn run_inner(command: &Command, uploader: &dyn Uploader) -> Result<Value> {
    match command {
        Command::Backup(args) => run_backup(args, uploader),
        Command::Cleanup(args) => run_cleanup(args),
    }
}

pub fn parse_args(tokens: &[String]) -> Result<Command> {
    if tokens.first().is_some_and(|token| token == "cleanup") {
        parse_cleanup_args(&tokens[1..])
    } else {
        parse_backup_args(tokens)
    }
}

fn parse_backup_args(tokens: &[String]) -> Result<Command> {
    let mut config = PathBuf::from("cfg/backup.json");
    let mut log_level = "WARNING".to_owned();
    let mut dry_run = false;
    let mut keep_archive = false;
    let mut target_directory = None;
    let mut index = 0;

    while index < tokens.len() {
        match tokens[index].as_str() {
            "--help" | "-h" => return Err(BackupError::Args(help_text())),
            "--dry-run" => dry_run = true,
            "--keep-archive" => keep_archive = true,
            "--config" => {
                index += 1;
                config = PathBuf::from(required_arg(tokens, index, "--config")?);
            }
            "--log-level" => {
                index += 1;
                required_arg(tokens, index, "--log-level")?.clone_into(&mut log_level);
                validate_log_level(&log_level)?;
            }
            token if token.starts_with('-') => {
                return Err(BackupError::Args(format!("unrecognized argument: {token}")));
            }
            token => {
                if target_directory.is_some() {
                    return Err(BackupError::Args(format!("unrecognized argument: {token}")));
                }
                target_directory = Some(PathBuf::from(token));
            }
        }
        index += 1;
    }

    Ok(Command::Backup(BackupArgs {
        config,
        log_level,
        target_directory,
        dry_run,
        keep_archive,
    }))
}

fn parse_cleanup_args(tokens: &[String]) -> Result<Command> {
    let mut config = PathBuf::from("cfg/backup.json");
    let mut log_level = "WARNING".to_owned();
    let mut dry_run = false;
    let mut older_than_days = 0_u64;
    let mut keep_latest = 0_usize;
    let mut index = 0;

    while index < tokens.len() {
        match tokens[index].as_str() {
            "--help" | "-h" => return Err(BackupError::Args(help_text())),
            "--dry-run" => dry_run = true,
            "--config" => {
                index += 1;
                config = PathBuf::from(required_arg(tokens, index, "--config")?);
            }
            "--log-level" => {
                index += 1;
                required_arg(tokens, index, "--log-level")?.clone_into(&mut log_level);
                validate_log_level(&log_level)?;
            }
            "--older-than-days" => {
                index += 1;
                older_than_days = parse_non_negative_u64(
                    required_arg(tokens, index, "--older-than-days")?,
                    "--older-than-days",
                )?;
            }
            "--keep-latest" => {
                index += 1;
                keep_latest = parse_non_negative_usize(
                    required_arg(tokens, index, "--keep-latest")?,
                    "--keep-latest",
                )?;
            }
            token => return Err(BackupError::Args(format!("unrecognized argument: {token}"))),
        }
        index += 1;
    }

    Ok(Command::Cleanup(CleanupArgs {
        config,
        log_level,
        dry_run,
        older_than_days,
        keep_latest,
    }))
}

fn required_arg<'a>(tokens: &'a [String], index: usize, flag: &str) -> Result<&'a str> {
    tokens
        .get(index)
        .map(String::as_str)
        .ok_or_else(|| BackupError::Args(format!("{flag} requires a value")))
}

fn parse_non_negative_u64(value: &str, flag: &str) -> Result<u64> {
    if value.starts_with('-') {
        return Err(BackupError::Validation(format!(
            "{flag} must be greater than or equal to zero"
        )));
    }
    value
        .parse::<u64>()
        .map_err(|_| BackupError::Validation(format!("{flag} must be an integer")))
}

fn parse_non_negative_usize(value: &str, flag: &str) -> Result<usize> {
    let parsed = parse_non_negative_u64(value, flag)?;
    usize::try_from(parsed).map_err(|_| BackupError::Validation(format!("{flag} is too large")))
}

fn validate_log_level(value: &str) -> Result<()> {
    match value {
        "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL" => Ok(()),
        _ => Err(BackupError::Args(format!("invalid log level: {value}"))),
    }
}

fn run_backup(args: &BackupArgs, uploader: &dyn Uploader) -> Result<Value> {
    let mut config = load_config(&args.config)?;
    if let Some(target_directory) = &args.target_directory {
        config = BackupConfig {
            target_directory: resolve_loose(target_directory)?,
            drive_folder_id: config.drive_folder_id,
            service_account_file: config.service_account_file,
            archive_prefix: config.archive_prefix,
            staging_directory: config.staging_directory,
            delete_archive_after_upload: config.delete_archive_after_upload,
        };
    }

    validate_target_directory(&config.target_directory)?;
    if !args.dry_run {
        validate_service_account_file(&config.service_account_file)?;
    }

    fs::create_dir_all(&config.staging_directory)?;
    let archive_filename = build_archive_filename(&config.archive_prefix, None);
    let archive_path = config.staging_directory.join(archive_filename);
    let archive = create_archive(&config.target_directory, &archive_path)?;

    if args.dry_run {
        return Ok(json!({
            "status": "dry_run",
            "target_directory": config.target_directory.display().to_string(),
            "archive": ArchiveOutput::from_result(&archive, archive.path.exists()),
            "upload": DryRunUploadOutput {
                skipped: true,
                drive_folder_id: config.drive_folder_id,
            },
        }));
    }

    let upload = uploader.upload(&archive, &config)?;
    let delete_after_upload = config.delete_archive_after_upload && !args.keep_archive;
    let mut archive_present_after_cleanup = archive.path.exists();
    if delete_after_upload && archive.path.exists() {
        fs::remove_file(&archive.path)?;
        archive_present_after_cleanup = archive.path.exists();
    }

    Ok(json!({
        "status": "uploaded",
        "target_directory": config.target_directory.display().to_string(),
        "archive": ArchiveOutput::from_result(&archive, archive_present_after_cleanup),
        "upload": UploadOutput::from_result(upload, config.drive_folder_id),
    }))
}

fn run_cleanup(args: &CleanupArgs) -> Result<Value> {
    let config = load_config(&args.config)?;
    let candidates = matching_staged_archives(&config.staging_directory, &config.archive_prefix)?;
    let eligible = filter_cleanup_candidates(&candidates, args.older_than_days, args.keep_latest)?;

    let mut paths = Vec::new();
    for path in &eligible {
        if !args.dry_run {
            fs::remove_file(path)?;
        }
        paths.push(path.display().to_string());
    }

    Ok(json!({
        "status": if args.dry_run { "dry_run" } else { "cleaned" },
        "staging_directory": config.staging_directory.display().to_string(),
        "archive_prefix": config.archive_prefix,
        "matched_count": candidates.len(),
        "deleted_count": if args.dry_run { 0 } else { paths.len() },
        "would_delete_count": if args.dry_run { paths.len() } else { 0 },
        "paths": paths,
    }))
}

fn help_text() -> String {
    "Zip a directory and upload it to Google Drive.\n\nUsage:\n  mattrix-backup [--config PATH] [--dry-run] [--keep-archive] [--log-level LEVEL] [TARGET_DIRECTORY]\n  mattrix-backup cleanup [--config PATH] [--dry-run] [--older-than-days DAYS] [--keep-latest N] [--log-level LEVEL]".to_owned()
}
