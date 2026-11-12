//! Linux prototype selection validation. No file content is parsed.
use std::os::unix::fs::{MetadataExt, OpenOptionsExt};
use std::{
    fs, io,
    path::{Path, PathBuf},
};

pub fn snapshot(path: &Path) -> io::Result<PathBuf> {
    let before = fs::symlink_metadata(path)?;
    if !before.is_file() {
        return Err(io::Error::other("not a regular file"));
    }
    let absolute = fs::canonicalize(path)?;
    // Linux asm-generic/fcntl.h: O_NOFOLLOW | O_NONBLOCK. Never block on a
    // substituted FIFO or follow a substituted final symlink during the check.
    let opened = fs::OpenOptions::new()
        .read(true)
        .custom_flags(0x20000 | 0x800)
        .open(&absolute)?;
    let after = opened.metadata()?;
    if !after.is_file() || before.dev() != after.dev() || before.ino() != after.ino() {
        return Err(io::Error::other("selection changed"));
    }
    Ok(absolute)
}
