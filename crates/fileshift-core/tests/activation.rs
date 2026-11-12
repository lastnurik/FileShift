use fileshift_core::{Activation, ActivationStatus, PopupModel, Selection};
use std::path::PathBuf;

#[test]
fn popup_keeps_the_invoked_selection_after_provider_changes() {
    let mut selection = Selection::LocalPaths(vec![
        PathBuf::from("first.png"),
        PathBuf::from("second.png"),
    ]);
    let popup = Activation::snapshot(selection.clone());
    selection = Selection::LocalPaths(vec![PathBuf::from("later.png")]);
    assert_eq!(
        popup,
        PopupModel::Selection(vec![
            PathBuf::from("first.png"),
            PathBuf::from("second.png")
        ])
    );
    assert_ne!(popup, Activation::snapshot(selection));
}

#[test]
fn empty_or_unsupported_context_produces_actionable_status() {
    assert_eq!(
        Activation::snapshot(Selection::LocalPaths(vec![])),
        PopupModel::Status(ActivationStatus::NoLocalFiles)
    );
    assert_eq!(
        Activation::snapshot(Selection::Unsupported),
        PopupModel::Status(ActivationStatus::UnsupportedContext)
    );
}
