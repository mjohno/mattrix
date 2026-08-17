use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use serde::Deserialize;

use crate::error::{BackupError, Result};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BackupConfig {
    pub target_directory: PathBuf,
    pub drive_folder_id: String,
    pub service_account_file: PathBuf,
    pub archive_prefix: String,
    pub staging_directory: PathBuf,
    pub delete_archive_after_upload: bool,
}

#[derive(Debug, Deserialize)]
struct RawConfig {
    target_directory: Option<String>,
    drive_folder_id: Option<String>,
    service_account_file: Option<String>,
    archive_prefix: Option<String>,
    staging_directory: Option<String>,
    delete_archive_after_upload: Option<bool>,
}

pub fn load_config(path: &Path) -> Result<BackupConfig> {
    let config_path = resolve_loose(path)?;
    if !config_path.is_file() {
        return Err(BackupError::Io(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            format!("Config file not found: {}", config_path.display()),
        )));
    }

    let text = fs::read_to_string(&config_path)?;
    let raw: RawConfig = serde_json::from_str(&text)?;
    let base = config_path.parent().unwrap_or_else(|| Path::new("."));

    Ok(BackupConfig {
        target_directory: resolve_config_path(
            base,
            &required_str(raw.target_directory.as_ref(), "target_directory")?,
        )?,
        drive_folder_id: required_str(raw.drive_folder_id.as_ref(), "drive_folder_id")?,
        service_account_file: resolve_config_path(
            base,
            &required_str(raw.service_account_file.as_ref(), "service_account_file")?,
        )?,
        archive_prefix: required_str(raw.archive_prefix.as_ref(), "archive_prefix")?,
        staging_directory: resolve_config_path(
            base,
            &required_str(raw.staging_directory.as_ref(), "staging_directory")?,
        )?,
        delete_archive_after_upload: raw.delete_archive_after_upload.unwrap_or(true),
    })
}

fn required_str(value: Option<&String>, key: &str) -> Result<String> {
    let Some(value) = value else {
        return Err(BackupError::Config(format!(
            "Config field '{key}' must be a non-empty string"
        )));
    };
    let trimmed = value.trim();
    if trimmed.is_empty() {
        return Err(BackupError::Config(format!(
            "Config field '{key}' must be a non-empty string"
        )));
    }
    Ok(trimmed.to_owned())
}

pub fn resolve_config_path(base: &Path, value: &str) -> Result<PathBuf> {
    let expanded = expand_tilde(value)?;
    let candidate = PathBuf::from(expanded);
    if candidate.is_absolute() {
        resolve_loose(&candidate)
    } else {
        resolve_loose(&base.join(candidate))
    }
}

fn expand_tilde(value: &str) -> Result<String> {
    if value == "~" {
        return home_dir().map(|home| home.to_string_lossy().into_owned());
    }
    if let Some(rest) = value.strip_prefix("~/") {
        return home_dir().map(|home| home.join(rest).to_string_lossy().into_owned());
    }
    Ok(value.to_owned())
}

fn home_dir() -> Result<PathBuf> {
    env::var_os("HOME")
        .map(PathBuf::from)
        .ok_or_else(|| BackupError::Config("Cannot expand '~' because HOME is not set".to_owned()))
}

pub fn resolve_loose(path: &Path) -> Result<PathBuf> {
    if path.exists() {
        return Ok(path.canonicalize()?);
    }
    if path.is_absolute() {
        Ok(path.to_path_buf())
    } else {
        Ok(env::current_dir()?.join(path))
    }
}

pub fn validate_target_directory(path: &Path) -> Result<()> {
    if !path.exists() {
        return Err(BackupError::Io(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            format!("Target directory does not exist: {}", path.display()),
        )));
    }
    if !path.is_dir() {
        return Err(BackupError::Validation(format!(
            "Target path is not a directory: {}",
            path.display()
        )));
    }
    Ok(())
}

pub fn validate_service_account_file(path: &Path) -> Result<()> {
    if !path.is_file() {
        return Err(BackupError::Io(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            format!("Google service-account file not found: {}", path.display()),
        )));
    }
    Ok(())
}
