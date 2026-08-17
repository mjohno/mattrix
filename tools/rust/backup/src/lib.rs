//! Mattrix local backup utility.

#![allow(clippy::missing_errors_doc)]

pub mod archive;
pub mod cleanup;
pub mod cli;
pub mod config;
pub mod drive;
pub mod error;
pub mod output;

pub use cli::{main_result, run};
