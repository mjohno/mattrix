use serde::Serialize;

use crate::archive::ArchiveResult;
use crate::drive::UploadResult;
use crate::error::BackupError;

#[derive(Debug, Serialize)]
pub struct ArchiveOutput {
    pub path: String,
    pub filename: String,
    pub byte_size: u64,
    pub sha256: String,
    pub present_after_cleanup: bool,
}

impl ArchiveOutput {
    #[must_use]
    pub fn from_result(archive: &ArchiveResult, present_after_cleanup: bool) -> Self {
        Self {
            path: archive.path.display().to_string(),
            filename: archive.filename.clone(),
            byte_size: archive.byte_size,
            sha256: archive.sha256.clone(),
            present_after_cleanup,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct DryRunUploadOutput {
    pub skipped: bool,
    pub drive_folder_id: String,
}

#[derive(Debug, Serialize)]
pub struct UploadOutput {
    pub file_id: String,
    pub filename: String,
    pub created_time: Option<String>,
    pub drive_folder_id: String,
}

impl UploadOutput {
    #[must_use]
    pub fn from_result(upload: UploadResult, drive_folder_id: String) -> Self {
        Self {
            file_id: upload.file_id,
            filename: upload.filename,
            created_time: upload.created_time,
            drive_folder_id,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct ErrorPayload<'a> {
    pub status: &'static str,
    pub command: &'a str,
    pub error: ErrorBody,
}

#[derive(Debug, Serialize)]
pub struct ErrorBody {
    #[serde(rename = "type")]
    pub type_name: String,
    pub message: String,
}

#[must_use]
pub fn structured_error<'a>(command: &'a str, error: &BackupError) -> ErrorPayload<'a> {
    ErrorPayload {
        status: "error",
        command,
        error: ErrorBody {
            type_name: error.type_name().to_owned(),
            message: error.to_string(),
        },
    }
}
