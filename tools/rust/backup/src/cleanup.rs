use std::fs;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use crate::error::{BackupError, Result};

#[allow(clippy::case_sensitive_file_extension_comparisons)]
pub fn matching_staged_archives(
    staging_directory: &Path,
    archive_prefix: &str,
) -> Result<Vec<PathBuf>> {
    if !staging_directory.exists() {
        return Ok(Vec::new());
    }
    if !staging_directory.is_dir() {
        return Err(BackupError::Validation(format!(
            "Staging path is not a directory: {}",
            staging_directory.display()
        )));
    }

    let prefix = format!("{archive_prefix}-");
    let mut matches = Vec::new();
    for entry in fs::read_dir(staging_directory)? {
        let path = entry?.path();
        if !path.is_file() {
            continue;
        }
        let Some(name) = path.file_name().and_then(|value| value.to_str()) else {
            continue;
        };
        if name.starts_with(&prefix) && name.ends_with(".zip") {
            matches.push(path);
        }
    }

    matches.sort_by(|left, right| {
        let left_meta = left.metadata();
        let right_meta = right.metadata();
        let left_time = left_meta
            .and_then(|meta| meta.modified())
            .unwrap_or(SystemTime::UNIX_EPOCH);
        let right_time = right_meta
            .and_then(|meta| meta.modified())
            .unwrap_or(SystemTime::UNIX_EPOCH);
        right_time
            .cmp(&left_time)
            .then_with(|| right.file_name().cmp(&left.file_name()))
    });
    Ok(matches)
}

pub fn filter_cleanup_candidates(
    candidates: &[PathBuf],
    older_than_days: u64,
    keep_latest: usize,
) -> Result<Vec<PathBuf>> {
    let cutoff = SystemTime::now()
        .checked_sub(Duration::from_secs(
            older_than_days.saturating_mul(24 * 60 * 60),
        ))
        .unwrap_or(SystemTime::UNIX_EPOCH);
    let mut eligible = Vec::new();
    for (index, path) in candidates.iter().enumerate() {
        if index < keep_latest {
            continue;
        }
        let modified = path.metadata()?.modified()?;
        if modified <= cutoff {
            eligible.push(path.clone());
        }
    }
    Ok(eligible)
}
