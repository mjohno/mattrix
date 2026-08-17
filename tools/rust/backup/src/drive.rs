use std::fs::File as FsFile;
use std::path::Path;

use crate::archive::ArchiveResult;
use crate::config::BackupConfig;
use crate::error::{BackupError, Result};

#[derive(Debug, Clone)]
pub struct UploadResult {
    pub file_id: String,
    pub filename: String,
    pub created_time: Option<String>,
}

pub trait Uploader {
    fn upload(&self, archive: &ArchiveResult, config: &BackupConfig) -> Result<UploadResult>;
}

#[derive(Debug, Default)]
pub struct GoogleDriveUploader;

impl Uploader for GoogleDriveUploader {
    fn upload(&self, archive: &ArchiveResult, config: &BackupConfig) -> Result<UploadResult> {
        if std::env::var_os("MATTRIX_BACKUP_FAKE_UPLOAD").is_some() {
            return Ok(UploadResult {
                file_id: "fake-file-id".to_owned(),
                filename: archive.filename.clone(),
                created_time: Some("1970-01-01T00:00:00Z".to_owned()),
            });
        }

        let runtime = tokio::runtime::Runtime::new().map_err(|error| {
            BackupError::Upload(format!(
                "Google Drive async runtime initialization failed: {error}"
            ))
        })?;
        runtime.block_on(upload_archive_to_google_drive(
            &archive.path,
            &archive.filename,
            &config.drive_folder_id,
            &config.service_account_file,
        ))
    }
}

async fn upload_archive_to_google_drive(
    archive_path: &Path,
    archive_filename: &str,
    drive_folder_id: &str,
    service_account_file: &Path,
) -> Result<UploadResult> {
    use google_drive3::api::File;
    use google_drive3::{hyper_rustls, hyper_util, yup_oauth2, DriveHub};

    let service_account_key = yup_oauth2::read_service_account_key(service_account_file)
        .await
        .map_err(|error| {
            BackupError::Upload(format!(
                "Google Drive authentication failed while reading service-account credentials from '{}': {error}",
                service_account_file.display()
            ))
        })?;
    let auth = yup_oauth2::ServiceAccountAuthenticator::builder(service_account_key)
        .build()
        .await
        .map_err(|error| {
            BackupError::Upload(format!("Google Drive authentication failed: {error}"))
        })?;

    let connector = hyper_rustls::HttpsConnectorBuilder::new()
        .with_native_roots()
        .map_err(|error| {
            BackupError::Upload(format!("Google Drive TLS initialization failed: {error}"))
        })?
        .https_or_http()
        .enable_http2()
        .build();
    let client = hyper_util::client::legacy::Client::builder(hyper_util::rt::TokioExecutor::new())
        .build(connector);
    let hub = DriveHub::new(client, auth);

    let request = File {
        name: Some(archive_filename.to_owned()),
        parents: Some(vec![drive_folder_id.to_owned()]),
        ..File::default()
    };
    let mime_type = "application/zip".parse().map_err(|error| {
        BackupError::Upload(format!(
            "Google Drive upload MIME type initialization failed: {error}"
        ))
    })?;
    let file = FsFile::open(archive_path)?;
    let (_response, uploaded) = hub
        .files()
        .create(request)
        .supports_all_drives(true)
        .param("fields", "id,name,createdTime")
        .upload(file, mime_type)
        .await
        .map_err(|error| {
            BackupError::Upload(format!(
                "Google Drive upload failed for folder '{drive_folder_id}' and archive '{archive_filename}': {error}"
            ))
        })?;

    let file_id = uploaded.id.unwrap_or_default().trim().to_owned();
    if file_id.is_empty() {
        return Err(BackupError::Upload(
            "Google Drive upload response did not include a file id".to_owned(),
        ));
    }
    Ok(UploadResult {
        file_id,
        filename: uploaded
            .name
            .unwrap_or_else(|| archive_filename.to_owned())
            .trim()
            .to_owned(),
        created_time: uploaded.created_time.map(|value| value.to_rfc3339()),
    })
}
