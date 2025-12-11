# Genesis - NVDA Add-on Project Generator

* **Author:** Edilberto Fonseca <edilberto.fonseca@outlook.com>  
* **License:** [GPL 2](https://www.gnu.org/licenses/gpl-2.0.html)  
* **Version:** 2025.1.0  

## Description

Genesis is an NVDA add-on designed to simplify the creation of new add-on projects.  
It provides an accessible interface for defining the initial metadata and automatically generates the entire project structure. When enabled, it can also create the project repository on your GitHub account.

The project structure is generated based on the **official NVDA community template**:  
https://github.com/nvaccess/addonTemplate

## Main Features

* Intuitive and accessible graphical interface.
* Automatic project structure generation using the official NVDA add-on template.
* Automatic filling of metadata such as name, version, author, and description.
* Option to include documentation (`doc`) and localization (`locale`) folders.
* Ability to clone the official NVDA repository.
* **Optional GitHub integration** for creating a remote repository automatically.
* Add-on-specific settings available in the NVDA configuration panel.

## Target Audience

This add-on is ideal for:

* **Beginners** who want an easy introduction to NVDA add-on development.  
* **Experienced developers** who want to accelerate project setup.

## Requirements

### To use Genesis
No external requirements — the add-on works out of the box inside NVDA.

### To develop your generated add-on
Install the following:

* **Python 3.11 (32-bit recommended)** – https://www.python.org/downloads/windows/  
* **Git** – https://git-scm.com/  
* **Scons 4.5.2 or newer** – install via `pip install scons`  
* **GNU Gettext** – needed for translation support  
  * Windows: https://gnuwin32.sourceforge.net/downlinks/gettext.php  
* **Markdown 3.3.0+** – optional, for converting documentation  
  * Install via: `pip install markdown`

### To publish to GitHub (optional)

* A GitHub account  
* A Personal Access Token (PAT) with **repo** permission  

Publication only happens when enabled in:  
**NVDA > Preferences > Settings > Genesis**

## GitHub Authentication

When the option **“Allow publishing repository on GitHub”** is enabled in Genesis settings, you will be prompted for your GitHub token.

If the option is disabled:

✔ No authentication dialog appears  
✔ Nothing is sent to GitHub  
✔ The project is generated locally only  

### Creating a GitHub Token

1. Visit: https://github.com/settings/tokens  
2. Select **“Tokens (classic)” → “Generate new token (classic)”**  
3. Name the token (e.g., *Genesis NVDA*)  
4. Choose an expiration date  
5. Grant the required permission:  
   * `repo`  
6. Generate the token and store it safely

### Notes

* Your token is **never saved** by Genesis.  
* It is validated directly with GitHub.  
* You may revoke it at any time.

## Installation

### Through the Add-on Store

1. NVDA menu → **Tools** → **Add-on Store**  
2. Open the **Available add-ons** tab  
3. Search for **Genesis**  
4. Click **Install**  
5. Restart NVDA

### Manual Installation

1. Download the `genesis.nvda-addon` package  
2. NVDA menu → Tools → **Manage add-ons**  
3. Click **Install** and select the file  
4. Restart NVDA  

## Features

* Uses the **official NVDA add-on template** as the project base  
* Fully compatible with the NVDA add-on build system  
* Remote repository creation is **optional**  
* Metadata is applied automatically to all necessary files

## Keyboard Shortcuts

| Shortcut        | Action                                         |
|----------------|------------------------------------------------|
| `NVDA+Shift+G` | Opens Genesis                                  |
| `Alt+G`        | Generates the new project                       |
| `Alt+L`        | Clears all fields                               |
| `Alt+T`        | Clones the official NVDA repository             |
| `Alt+S`        | Closes Genesis                                  |

## Translators

* **Portuguese (Brazil):** Edilberto Fonseca
