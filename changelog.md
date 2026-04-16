# Changelog

This commit introduces a large refactor and maintenance update across the repository, focusing on modernizing tooling, improving robustness, and streamlining CI/build steps.

Key changes include:
CI:

- `buildaddon.yml` now skips running on the template repo.
- Installs and uses the 'uv' runner for dependencies.
- Runs `pre-commit` and `scons` via `uv`.
- Improves artifact upload/download settings.

Pre-commit:

- Replaced/expanded hooks with a comprehensive configuration (e.g., `ruff`, `add-trailing-comma`, - `no-commit-to-branch`, `pyright` local hook).
- Added sensible excludes and defaults.

Genesis plugin:


- Numerous API/style refactors:
- Renamed several functions/variables to `camelCase`.
- Integrated `gettext` for internationalization.
- Cleaner menu/menu-item binding.
- Improved dialog lifecycle handling.
- Enhanced settings panel wiring.
- Improved error/message handling and logging.
- Added small UX fixes.
- Safer resource cleanup in `terminate()`.

Utilities & templates:

- Rewritten/renamed functions in `fileUtils` and `addonUtils`.
- Improved error handling and logging in utilities.
- Extended `buildVars.tpl` with `speechDictionaries`.

Docs & metadata:

- Updated Portuguese README (formatting/wording).
- Added AI disclosure comments in some modules.
- Removed obsolete `installTasks`.
- Added `checkoutCode.txt`.
