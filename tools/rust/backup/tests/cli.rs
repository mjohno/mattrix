use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::time::{Duration, SystemTime};

use filetime::{set_file_mtime, FileTime};
use serde_json::{json, Value};
use tempfile::TempDir;

fn binary() -> &'static str {
    env!("CARGO_BIN_EXE_mattrix-backup")
}

fn run(args: &[&str]) -> Output {
    Command::new(binary())
        .args(args)
        .output()
        .expect("run mattrix-backup")
}

fn run_fake_upload(args: &[&str]) -> Output {
    Command::new(binary())
        .args(args)
        .env("MATTRIX_BACKUP_FAKE_UPLOAD", "1")
        .output()
        .expect("run mattrix-backup")
}

fn payload(output: &Output) -> Value {
    serde_json::from_slice(&output.stdout).expect("json stdout")
}

struct Fixture {
    tmp: TempDir,
    target: PathBuf,
    staging: PathBuf,
    service_account: PathBuf,
    config: PathBuf,
}

impl Fixture {
    fn new(delete_archive_after_upload: bool) -> Self {
        let tmp = tempfile::tempdir().expect("tempdir");
        let target = tmp.path().join("target");
        let staging = tmp.path().join("staging");
        let service_account = tmp.path().join("service-account.json");
        let config = tmp.path().join("backup.json");
        fs::create_dir(&target).expect("target");
        fs::write(target.join("root.txt"), "root").expect("root");
        fs::create_dir(target.join("nested")).expect("nested dir");
        fs::write(target.join("nested/child.txt"), "child").expect("child");
        fs::create_dir(target.join("empty")).expect("empty dir");
        fs::write(&service_account, "{}").expect("service account");
        write_config(
            &config,
            &target,
            &staging,
            &service_account,
            delete_archive_after_upload,
        );
        Self {
            tmp,
            target,
            staging,
            service_account,
            config,
        }
    }
}

fn write_config(
    config: &Path,
    target: &Path,
    staging: &Path,
    service_account: &Path,
    delete_archive_after_upload: bool,
) {
    let value = json!({
        "target_directory": target,
        "drive_folder_id": "drive-folder",
        "service_account_file": service_account,
        "archive_prefix": "test-backup",
        "staging_directory": staging,
        "delete_archive_after_upload": delete_archive_after_upload,
    });
    fs::write(config, serde_json::to_vec(&value).expect("config json")).expect("write config");
}

#[test]
fn dry_run_zips_and_skips_upload() {
    let fixture = Fixture::new(true);
    let output = run(&["--dry-run", "--config", fixture.config.to_str().unwrap()]);

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let payload = payload(&output);
    assert_eq!(payload["status"], "dry_run");
    assert_eq!(payload["upload"]["skipped"], true);
    let archive_path = PathBuf::from(payload["archive"]["path"].as_str().unwrap());
    assert!(archive_path.is_file());
    assert_eq!(payload["archive"]["present_after_cleanup"], true);
    assert_eq!(payload["archive"]["sha256"].as_str().unwrap().len(), 64);

    let file = fs::File::open(archive_path).expect("archive");
    let mut archive = zip::ZipArchive::new(file).expect("zip");
    let mut entries = Vec::new();
    for index in 0..archive.len() {
        entries.push(archive.by_index(index).expect("entry").name().to_owned());
    }
    entries.sort();
    assert!(entries.contains(&"root.txt".to_owned()));
    assert!(entries.contains(&"nested/child.txt".to_owned()));
    assert!(entries.contains(&"empty/".to_owned()));
    assert!(entries.iter().all(|entry| !entry.starts_with('/')));
    assert!(entries
        .iter()
        .all(|entry| !entry.contains(fixture.target.to_str().unwrap())));
}

#[test]
fn backup_fake_upload_deletes_archive_by_default() {
    let fixture = Fixture::new(true);
    let output = run_fake_upload(&["--config", fixture.config.to_str().unwrap()]);

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let payload = payload(&output);
    assert_eq!(payload["status"], "uploaded");
    assert_eq!(payload["upload"]["file_id"], "fake-file-id");
    let archive_path = PathBuf::from(payload["archive"]["path"].as_str().unwrap());
    assert!(!archive_path.exists());
    assert_eq!(payload["archive"]["present_after_cleanup"], false);
}

#[test]
fn keep_archive_preserves_uploaded_archive() {
    let fixture = Fixture::new(true);
    let output = run_fake_upload(&[
        "--config",
        fixture.config.to_str().unwrap(),
        "--keep-archive",
    ]);

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let payload = payload(&output);
    let archive_path = PathBuf::from(payload["archive"]["path"].as_str().unwrap());
    assert!(archive_path.is_file());
    assert_eq!(payload["archive"]["present_after_cleanup"], true);
}

#[test]
fn positional_target_overrides_config_target() {
    let fixture = Fixture::new(true);
    let override_target = fixture.tmp.path().join("override-target");
    fs::create_dir(&override_target).expect("override dir");
    fs::write(override_target.join("override.txt"), "override").expect("override file");

    let output = run(&[
        "--dry-run",
        "--config",
        fixture.config.to_str().unwrap(),
        override_target.to_str().unwrap(),
    ]);

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let payload = payload(&output);
    assert_eq!(
        payload["target_directory"],
        override_target.to_str().unwrap()
    );
}

#[test]
fn reports_missing_config() {
    let tmp = tempfile::tempdir().expect("tempdir");
    let missing = tmp.path().join("missing.json");
    let output = run(&["--config", missing.to_str().unwrap()]);

    assert!(!output.status.success());
    let payload = payload(&output);
    assert_eq!(payload["status"], "error");
    assert_eq!(payload["error"]["type"], "FileNotFoundError");
    assert!(payload["error"]["message"]
        .as_str()
        .unwrap()
        .contains("Config file not found"));
}

#[test]
fn reports_missing_target() {
    let fixture = Fixture::new(true);
    let missing_target = fixture.tmp.path().join("missing");
    write_config(
        &fixture.config,
        &missing_target,
        &fixture.staging,
        &fixture.service_account,
        true,
    );

    let output = run(&["--config", fixture.config.to_str().unwrap()]);

    assert!(!output.status.success());
    let payload = payload(&output);
    assert_eq!(payload["error"]["type"], "FileNotFoundError");
    assert!(payload["error"]["message"]
        .as_str()
        .unwrap()
        .contains("Target directory does not exist"));
}

#[test]
fn reports_missing_service_account_for_backup() {
    let fixture = Fixture::new(true);
    fs::remove_file(&fixture.service_account).expect("remove service account");

    let output = run(&["--config", fixture.config.to_str().unwrap()]);

    assert!(!output.status.success());
    let payload = payload(&output);
    assert_eq!(payload["error"]["type"], "FileNotFoundError");
    assert!(payload["error"]["message"]
        .as_str()
        .unwrap()
        .contains("Google service-account file not found"));
}

#[test]
fn cleanup_dry_run_reports_without_deleting() {
    let fixture = Fixture::new(true);
    let archive = staged_archive(&fixture.staging, "test-backup-old.zip", 3);

    let output = run(&[
        "cleanup",
        "--dry-run",
        "--config",
        fixture.config.to_str().unwrap(),
    ]);

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let payload = payload(&output);
    assert_eq!(payload["status"], "dry_run");
    assert_eq!(payload["matched_count"], 1);
    assert_eq!(payload["would_delete_count"], 1);
    assert!(archive.exists());
}

#[test]
fn cleanup_deletes_eligible_archives_and_keeps_latest() {
    let fixture = Fixture::new(true);
    let newest = staged_archive(&fixture.staging, "test-backup-newest.zip", 0);
    let old = staged_archive(&fixture.staging, "test-backup-old.zip", 5);
    let other = staged_archive(&fixture.staging, "other-prefix-old.zip", 5);

    let output = run(&[
        "cleanup",
        "--config",
        fixture.config.to_str().unwrap(),
        "--keep-latest",
        "1",
    ]);

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let payload = payload(&output);
    assert_eq!(payload["status"], "cleaned");
    assert_eq!(payload["matched_count"], 2);
    assert_eq!(payload["deleted_count"], 1);
    assert!(newest.exists());
    assert!(!old.exists());
    assert!(other.exists());
}

#[test]
fn cleanup_older_than_days_only_deletes_old_matches() {
    let fixture = Fixture::new(true);
    let recent = staged_archive(&fixture.staging, "test-backup-recent.zip", 1);
    let old = staged_archive(&fixture.staging, "test-backup-old.zip", 10);

    let output = run(&[
        "cleanup",
        "--config",
        fixture.config.to_str().unwrap(),
        "--older-than-days",
        "7",
    ]);

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let payload = payload(&output);
    assert_eq!(payload["deleted_count"], 1);
    assert!(recent.exists());
    assert!(!old.exists());
}

#[test]
fn cleanup_rejects_negative_options() {
    let fixture = Fixture::new(true);
    let output = run(&[
        "cleanup",
        "--config",
        fixture.config.to_str().unwrap(),
        "--older-than-days",
        "-1",
    ]);

    assert!(!output.status.success());
    let payload = payload(&output);
    assert_eq!(payload["error"]["type"], "ValueError");
    assert!(payload["error"]["message"]
        .as_str()
        .unwrap()
        .contains("--older-than-days must be greater than or equal to zero"));
}

fn staged_archive(staging: &Path, name: &str, age_days: u64) -> PathBuf {
    fs::create_dir_all(staging).expect("staging");
    let path = staging.join(name);
    fs::write(&path, "archive").expect("archive");
    let modified = SystemTime::now() - Duration::from_secs(age_days * 24 * 60 * 60);
    set_file_mtime(&path, FileTime::from_system_time(modified)).expect("mtime");
    path
}
