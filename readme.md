# Genesis - NVDA Add-on Project Generator

- **Author:** Edilberto Fonseca <edilberto.fonseca@outlook.com>
- **License:** [GPL 2](https://www.gnu.org/licenses/gpl-2.0.html)
- **Version:** 2025.1.0

## Description

Genesis is an NVDA add-on designed to simplify the creation of add-on projects.
It provides a fully accessible interface to define initial metadata and automatically generate the project structure.

Optionally, Genesis can create the remote repository on GitHub using the official template.

The generated structure is based on the official NVDA community template:
[https://github.com/nvaccess/addonTemplate](https://github.com/nvaccess/addonTemplate)

## Main features

- Intuitive and accessible graphical interface
- Automatic generation of the add-on’s initial structure
- Filling in essential metadata
- Option to include documentation and localization folders
- Option to clone the official NVDA repository
- Optional GitHub integration
- Dedicated settings panel in NVDA

## Target audience

The add-on is intended for:

- Beginners who want to create their first add-on
- Experienced developers who want to speed up the start of new projects

## Requirements

### To use Genesis

No external requirements. The add-on works directly in NVDA.

### To develop the generated add-on

Install:

- Python 3.13 (64-bit recommended)
  [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
- Git
  [https://git-scm.com/](https://git-scm.com/)
- Scons 4.5.2 or higher
  `pip install scons`
- GNU Gettext
  Required to compile translation files
  [https://gnuwin32.sourceforge.net/downlinks/gettext.php](https://gnuwin32.sourceforge.net/downlinks/gettext.php)
- Markdown 3.3.0+ (optional)
  `pip install markdown`

### To publish on GitHub (optional)

- GitHub account
- Access token (PAT) with `repo` permission

Remote publishing only occurs when enabled in:
NVDA > Preferences > Settings > Genesis

## GitHub Authentication

If the option “Allow publishing repository on GitHub” is enabled, Genesis will request your access token.

When disabled:

- No authentication will be requested
- Nothing will be sent to GitHub
- The project will be created locally only

### How to generate a token on GitHub

1. Go to [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Navigate to "Tokens (classic)" → "Generate new token (classic)"
3. Set a name
4. Choose the expiration
5. Select the `repo` permission
6. Generate the token and store it securely

### Notes

- The token is not stored by the add-on
- It is validated directly by the GitHub API
- It can be revoked at any time

## Installation

### Via Add-on Store

1. NVDA > Tools > Add-on Store
2. “Available” tab
3. Search for “Genesis”
4. Click “Install”
5. Restart NVDA

### Manual installation

1. Download the file [`genesis.nvda-addon`](https://github.com/EdilbertoFonseca/genesis/)
2. Press Enter on the downloaded file
3. Follow the instructions to install the add-on
4. Restart NVDA

## Technical characteristics

- Uses the official NVDA template as a base
- Compatible with the official build system
- Remote publishing is optional
- Metadata automatically applied to the `buildVars.py` file

## Keyboard shortcuts

| Shortcut   | Action                              |
| ---------- | ----------------------------------- |
| NVDA+Alt+G | Opens Genesis                       |
| Alt+G      | Generates a new project             |
| Alt+L      | Clears all fields                   |
| Alt+T      | Clones the official NVDA repository |
| Alt+S      | Closes Genesis                      |

## Translators

- Portuguese (Brazil), pt_BR - Edilberto Fonseca
