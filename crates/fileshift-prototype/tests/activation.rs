#![cfg(target_os = "linux")]

use std::{
    ffi::OsString,
    fs,
    os::unix::ffi::OsStringExt,
    os::unix::fs::{PermissionsExt, symlink},
    process::{Command, Stdio},
    thread,
    time::{Duration, Instant},
};

#[test]
fn diagnostic_activation_rejects_directories_and_keeps_regular_files() {
    let root = std::env::temp_dir().join(format!("fileshift-activation-{}", std::process::id()));
    fs::create_dir_all(&root).unwrap();
    fs::write(root.join("two words.png"), b"prototype fixture").unwrap();
    let output = Command::new(env!("CARGO_BIN_EXE_fileshift-prototype"))
        .args(["--check", "--nautilus-script", "--"])
        .arg(root.join("two words.png"))
        .arg(&root)
        .output()
        .unwrap();
    fs::remove_dir_all(root).unwrap();
    assert!(output.status.success());
    assert_eq!(
        String::from_utf8(output.stdout).unwrap(),
        "prototype selection: 1 accepted; 1 rejected\n"
    );
}

#[test]
fn diagnostic_activation_rejects_a_fifo_without_waiting_for_a_writer() {
    let root = std::env::temp_dir().join(format!("fileshift-fifo-{}", std::process::id()));
    fs::create_dir(&root).unwrap();
    let fifo = root.join("pipe.png");
    // Ubuntu's coreutils supplies mkfifo; no writer is started for this fixture.
    assert!(
        Command::new("mkfifo")
            .arg(&fifo)
            .status()
            .unwrap()
            .success()
    );
    fs::write(root.join("regular.png"), b"fixture").unwrap();
    let mut child = Command::new(env!("CARGO_BIN_EXE_fileshift-prototype"))
        .args(["--check", "--nautilus-script", "--"])
        .arg(&fifo)
        .arg(root.join("regular.png"))
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    let deadline = Instant::now() + Duration::from_secs(5);
    let mut timed_out = false;
    while child.try_wait().unwrap().is_none() {
        if Instant::now() >= deadline {
            child.kill().unwrap();
            timed_out = true;
            break;
        }
        thread::sleep(Duration::from_millis(10));
    }
    let output = child.wait_with_output().unwrap();
    fs::remove_dir_all(root).unwrap();
    assert!(!timed_out, "FIFO validation waited for a writer");
    assert!(output.status.success());
    assert_eq!(
        output.stdout,
        b"prototype selection: 1 accepted; 1 rejected\n"
    );
    assert!(output.stderr.is_empty());
}

#[test]
fn diagnostic_activation_preserves_native_filenames_relative_to_invocation_directory() {
    let root = std::env::temp_dir().join(format!("fileshift-filenames-{}", std::process::id()));
    fs::create_dir(&root).unwrap();
    let names = [
        OsString::from("two words.png"),
        OsString::from("雪.png"),
        OsString::from("quote'\".png"),
        OsString::from("$(touch PWNED).png"),
        OsString::from("-option.png"),
        OsString::from("line\nbreak.png"),
        OsString::from_vec(b"raw-\xff.png".to_vec()),
    ];
    for name in &names {
        fs::write(root.join(name), b"fixture").unwrap();
    }
    let output = Command::new(env!("CARGO_BIN_EXE_fileshift-prototype"))
        .args(["--check", "--nautilus-script", "--"])
        .args(&names)
        .current_dir(&root)
        .output()
        .unwrap();
    let shell_marker_exists = root.join("PWNED").exists();
    fs::remove_dir_all(root).unwrap();
    assert!(output.status.success());
    assert_eq!(
        output.stdout,
        b"prototype selection: 7 accepted; 0 rejected\n"
    );
    assert!(
        output.stderr.is_empty(),
        "Diagnostics must not expose private filenames"
    );
    assert!(!shell_marker_exists);
}

#[test]
fn diagnostic_activation_rejects_symlinks_deleted_and_unreadable_files() {
    let root = std::env::temp_dir().join(format!("fileshift-rejections-{}", std::process::id()));
    fs::create_dir(&root).unwrap();
    let readable = root.join("readable.png");
    let unreadable = root.join("unreadable.png");
    let deleted = root.join("deleted.png");
    fs::write(&readable, b"fixture").unwrap();
    fs::write(&unreadable, b"fixture").unwrap();
    fs::set_permissions(&unreadable, fs::Permissions::from_mode(0o000)).unwrap();
    fs::write(&deleted, b"fixture").unwrap();
    fs::remove_file(&deleted).unwrap();
    symlink(&readable, root.join("link.png")).unwrap();
    symlink(&deleted, root.join("dangling.png")).unwrap();
    // This is an unreadable-file check only when the test user lacks read access.
    // Root can bypass mode bits and must not report this fixture as unreadable.
    let cannot_read = fs::File::open(&unreadable).is_err();
    let output = Command::new(env!("CARGO_BIN_EXE_fileshift-prototype"))
        .args(["--check", "--nautilus-script", "--"])
        .arg(&readable)
        .arg(root.join("link.png"))
        .arg(root.join("dangling.png"))
        .arg(&deleted)
        .arg(&unreadable)
        .output()
        .unwrap();
    fs::remove_dir_all(root).unwrap();
    assert!(
        cannot_read,
        "Run this acceptance check as an unprivileged user"
    );
    assert!(output.status.success());
    assert_eq!(
        output.stdout,
        b"prototype selection: 1 accepted; 4 rejected\n"
    );
    assert!(output.stderr.is_empty());
}
