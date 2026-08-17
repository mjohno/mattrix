use std::fmt::{Display, Formatter};
use std::io;

#[derive(Debug)]
pub enum BackupError {
    Io(io::Error),
    Json(serde_json::Error),
    Zip(zip::result::ZipError),
    Config(String),
    Validation(String),
    Upload(String),
    Args(String),
}

impl BackupError {
    #[must_use]
    pub fn type_name(&self) -> &'static str {
        match self {
            Self::Io(error) => match error.kind() {
                io::ErrorKind::NotFound => "FileNotFoundError",
                io::ErrorKind::PermissionDenied => "PermissionError",
                _ => "OSError",
            },
            Self::Json(_) => "JSONDecodeError",
            Self::Zip(_) => "ZipError",
            Self::Config(_) | Self::Validation(_) | Self::Args(_) => "ValueError",
            Self::Upload(_) => "RuntimeError",
        }
    }
}

impl Display for BackupError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Io(error) => Display::fmt(error, f),
            Self::Json(error) => Display::fmt(error, f),
            Self::Zip(error) => Display::fmt(error, f),
            Self::Config(message)
            | Self::Validation(message)
            | Self::Upload(message)
            | Self::Args(message) => f.write_str(message),
        }
    }
}

impl std::error::Error for BackupError {}

impl From<io::Error> for BackupError {
    fn from(value: io::Error) -> Self {
        Self::Io(value)
    }
}

impl From<serde_json::Error> for BackupError {
    fn from(value: serde_json::Error) -> Self {
        Self::Json(value)
    }
}

impl From<zip::result::ZipError> for BackupError {
    fn from(value: zip::result::ZipError) -> Self {
        Self::Zip(value)
    }
}

pub type Result<T> = std::result::Result<T, BackupError>;
