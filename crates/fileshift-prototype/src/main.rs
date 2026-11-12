#[cfg(target_os = "linux")]
use fileshift_core::{Activation, ActivationStatus, PopupModel, Selection};
use std::process::ExitCode;
#[cfg(target_os = "linux")]
use std::{
    ffi::OsStr,
    process::{Command, Stdio},
};

#[cfg(target_os = "linux")]
#[path = "../../../platform/linux/selection.rs"]
mod selection;

#[cfg(target_os = "linux")]
fn run() -> Result<(), &'static str> {
    let mut args = std::env::args_os().skip(1).peekable();
    let check = args.peek().is_some_and(|a| a == "--check");
    if check {
        args.next();
    }
    let source = args.next();
    if source.as_deref() == Some(OsStr::new("--help")) {
        println!(
            "FileShift development prototype (no conversion).\nUsage: fileshift-prototype [--check] --nautilus-script -- [paths...]"
        );
        return Ok(());
    }
    if source.as_deref() != Some(OsStr::new("--nautilus-script"))
        || args.next().as_deref() != Some(OsStr::new("--"))
    {
        return Err(
            "Invoke the installed FileShift Prototype script in GNOME Files. See --help for developer usage.",
        );
    }
    let mut paths = Vec::new();
    let mut rejected = 0;
    for arg in args {
        match selection::snapshot(std::path::Path::new(&arg)) {
            Ok(path) => paths.push(path),
            Err(_) => rejected += 1,
        }
    }
    let model = Activation::snapshot(Selection::LocalPaths(paths));
    let text = match model {
        PopupModel::Selection(paths) => format!(
            "prototype selection: {} accepted; {rejected} rejected",
            paths.len()
        ),
        PopupModel::Status(status) => {
            let message = match status {
                ActivationStatus::NoLocalFiles => {
                    "Select regular local files in GNOME Files and try again. Empty or nonlocal selections cannot be distinguished by this prototype."
                }
                ActivationStatus::UnsupportedContext => "Invoke FileShift from GNOME Files.",
            };
            format!("{message}\n{rejected} rejected")
        }
    };
    if check {
        println!("{text}");
        return Ok(());
    }
    let status = Command::new("/usr/bin/zenity")
        .args(["--info", "--no-markup", "--title=FileShift Prototype", "--ok-label=Close", "--width=420"])
        .arg(format!("--text={text}\n\nSelection inspection only. No conversion routes are installed.\nRejected items are not regular readable local files or changed during validation."))
        .stdin(Stdio::null()).stdout(Stdio::null()).stderr(Stdio::null())
        .status().map_err(|_| "Popup unavailable. Install the Ubuntu zenity package and retry in a graphical session.")?;
    match status.code() {
        Some(0 | 1) => Ok(()),
        _ => Err("Popup failed. Check the graphical session and Zenity installation."),
    }
}

#[cfg(not(target_os = "linux"))]
fn run() -> Result<(), &'static str> {
    Err("This prototype currently requires Linux. Windows and macOS acceptance remains open.")
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(message) => {
            eprintln!("{message}");
            ExitCode::FAILURE
        }
    }
}
