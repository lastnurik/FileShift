//! Desktop-independent activation prototype. No conversion routes are advertised.

use std::path::PathBuf;

/// A selection adapter supplies an owned snapshot, never a live view.
#[derive(Clone, Debug)]
pub enum Selection {
    LocalPaths(Vec<PathBuf>),
    Unsupported,
}

#[derive(Debug, PartialEq, Eq)]
pub enum PopupModel {
    Selection(Vec<PathBuf>),
    Status(ActivationStatus),
}

#[derive(Debug, PartialEq, Eq)]
pub enum ActivationStatus {
    NoLocalFiles,
    UnsupportedContext,
}

pub struct Activation;

impl Activation {
    pub fn snapshot(selection: Selection) -> PopupModel {
        match selection {
            Selection::LocalPaths(paths) if paths.is_empty() => {
                PopupModel::Status(ActivationStatus::NoLocalFiles)
            }
            Selection::LocalPaths(paths) => PopupModel::Selection(paths),
            Selection::Unsupported => PopupModel::Status(ActivationStatus::UnsupportedContext),
        }
    }
}
