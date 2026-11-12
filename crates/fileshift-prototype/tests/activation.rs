use std::{fs, process::Command};

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
