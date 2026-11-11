# Installation manages runtime dependencies

V1 provides a native installer or package for each supported OS and manages required conversion dependencies through installation. Users must not need a terminal, compiler, Python environment, or separately installed conversion tools; initial permission prompts and shortcut setup are acceptable, while everyday use requires no technical setup.

This prioritizes a built-in-tool experience over the smaller distribution and simpler release process that relying on user-installed runtimes or converters could provide. Specific package formats, dependency distribution mechanisms, update behavior, and uninstall behavior remain to be decided.

The repository will be public and also support building from source. Document the toolchain, native development dependencies, and reproducible build/test/install steps; source builds supplement the native packages. The repository license remains to be selected before public release.

Source license selection was subsequently resolved by [ADR 0006](0006-mit-source-license.md); third-party redistribution review remains required.
