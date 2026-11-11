# Rust core with platform adapters

Use Rust for the shared application core and separate OS adapters, allowing small native integration components and packaged document-conversion dependencies where necessary. This replaces the original Python proposal: native distribution and controlled idle resource use matter for an always-available desktop utility, and there is no existing implementation to migrate.

Rust does not establish native integration feasibility or codec safety by itself. Choose libraries and integration mechanisms from current documentation and prototype evidence. Cargo is the build foundation; a source-build option accompanies native packages.
