use std::fs::{self, File};
use std::io::{self, Read};
use std::path::{Path, PathBuf};

use serde::Serialize;
use sha2::{Digest, Sha256};
use time::{format_description::FormatItem, macros::format_description, OffsetDateTime};
use uuid::Uuid;
use zip::write::SimpleFileOptions;
use zip::{CompressionMethod, ZipWriter};

use crate::error::Result;

#[derive(Debug, Clone, Serialize)]
pub struct ArchiveResult {
    pub path: PathBuf,
    pub filename: String,
    pub byte_size: u64,
    pub sha256: String,
}

pub fn build_archive_filename(prefix: &str, now: Option<OffsetDateTime>) -> String {
    let mut safe_prefix = prefix
        .split_whitespace()
        .collect::<Vec<_>>()
        .join("-")
        .replace('/', "-");
    if safe_prefix.is_empty() {
        "backup".clone_into(&mut safe_prefix);
    }
    let timestamp = format_timestamp(now.unwrap_or_else(OffsetDateTime::now_utc));
    let id = Uuid::new_v4().simple().to_string();
    format!("{safe_prefix}-{timestamp}-{}.zip", &id[..12])
}

fn format_timestamp(now: OffsetDateTime) -> String {
    static FORMAT: &[FormatItem<'_>] =
        format_description!("[year][month][day]T[hour][minute][second]Z");
    now.format(FORMAT)
        .unwrap_or_else(|_| "19700101T000000Z".to_owned())
}

pub fn create_archive(source_directory: &Path, archive_path: &Path) -> Result<ArchiveResult> {
    let file = File::create(archive_path)?;
    let mut archive = ZipWriter::new(file);
    let options = SimpleFileOptions::default()
        .compression_method(CompressionMethod::Deflated)
        .compression_level(Some(9));

    for relative_path in iter_archive_entries(source_directory)? {
        let absolute_path = source_directory.join(&relative_path);
        let mut name = relative_path.to_string_lossy().replace('\\', "/");
        if absolute_path.is_dir() {
            if !name.ends_with('/') {
                name.push('/');
            }
            archive.add_directory(name, options)?;
        } else {
            archive.start_file(name, options)?;
            let mut input = File::open(absolute_path)?;
            io::copy(&mut input, &mut archive)?;
        }
    }
    archive.finish()?;

    Ok(ArchiveResult {
        path: archive_path.to_path_buf(),
        filename: archive_path
            .file_name()
            .map_or_else(String::new, |value| value.to_string_lossy().into_owned()),
        byte_size: archive_path.metadata()?.len(),
        sha256: sha256_hex(archive_path)?,
    })
}

pub fn iter_archive_entries(source_directory: &Path) -> Result<Vec<PathBuf>> {
    let mut entries = Vec::new();
    collect_entries(source_directory, source_directory, &mut entries)?;
    entries.sort();
    Ok(entries)
}

fn collect_entries(root: &Path, current: &Path, entries: &mut Vec<PathBuf>) -> Result<()> {
    let mut children = fs::read_dir(current)?.collect::<std::result::Result<Vec<_>, _>>()?;
    children.sort_by_key(std::fs::DirEntry::path);

    if children.is_empty() && current != root {
        entries.push(current.strip_prefix(root).unwrap_or(current).to_path_buf());
        return Ok(());
    }

    for child in children {
        let path = child.path();
        if path.is_dir() {
            collect_entries(root, &path, entries)?;
        } else if path.is_file() {
            entries.push(path.strip_prefix(root).unwrap_or(&path).to_path_buf());
        }
    }
    Ok(())
}

pub fn sha256_hex(path: &Path) -> Result<String> {
    let mut digest = Sha256::new();
    let mut file = File::open(path)?;
    let mut buffer = vec![0_u8; 1024 * 1024];
    loop {
        let count = file.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        digest.update(&buffer[..count]);
    }
    Ok(format!("{:x}", digest.finalize()))
}
