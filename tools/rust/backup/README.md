# Mattrix Backup

The Mattrix local backup utility creates a ZIP archive of a local directory and uploads it to Google Drive.

## Run

From the repository root:

```bash
cargo run --manifest-path tools/rust/Cargo.toml -p mattrix-backup --bin mattrix-backup -- --help
cargo run --manifest-path tools/rust/Cargo.toml -p mattrix-backup --bin mattrix-backup -- --dry-run --config cfg/backup.json
```

The config format is compatible with the former Python implementation:

```json
{
  "target_directory": "~/backup",
  "drive_folder_id": "google-drive-folder-id",
  "service_account_file": "../.secrets/localbackup.json",
  "archive_prefix": "mattrix-backup",
  "staging_directory": "/tmp/mattrix-backups",
  "delete_archive_after_upload": true
}
```

## Commands

Back up the configured target directory:

```bash
cargo run --manifest-path tools/rust/Cargo.toml -p mattrix-backup --bin mattrix-backup -- --config cfg/backup.json
```

Override the target directory:

```bash
cargo run --manifest-path tools/rust/Cargo.toml -p mattrix-backup --bin mattrix-backup -- --config cfg/backup.json /path/to/target
```

Create and validate the archive without uploading:

```bash
cargo run --manifest-path tools/rust/Cargo.toml -p mattrix-backup --bin mattrix-backup -- --dry-run --config cfg/backup.json
```

Keep the generated local archive after upload:

```bash
cargo run --manifest-path tools/rust/Cargo.toml -p mattrix-backup --bin mattrix-backup -- --config cfg/backup.json --keep-archive
```

Preview cleanup:

```bash
cargo run --manifest-path tools/rust/Cargo.toml -p mattrix-backup --bin mattrix-backup -- cleanup --dry-run --config cfg/backup.json
```

Delete staged archives matching the configured archive prefix:

```bash
cargo run --manifest-path tools/rust/Cargo.toml -p mattrix-backup --bin mattrix-backup -- cleanup --config cfg/backup.json
```

## Checks

```bash
cargo fmt --manifest-path tools/rust/Cargo.toml --check
cargo clippy --manifest-path tools/rust/Cargo.toml -p mattrix-backup --all-targets -- -D warnings
cargo test --manifest-path tools/rust/Cargo.toml -p mattrix-backup
```
