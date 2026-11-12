# Genesis – NVDA Add-on Project Generator

* **Author:** Edilberto Fonseca <edilberto.fonseca@outlook.com>
* **License:** [GPL 2](https://www.gnu.org/licenses/gpl-2.0.html)
* **Version:** 2026.1.0

## Description

Genesis is an NVDA add-on designed to simplify the creation of NVDA add-on projects.

It provides a fully accessible graphical interface that allows developers to define the initial project metadata and automatically generate the structure required to start developing a new add-on.

Optionally, Genesis can create a remote GitHub repository using the official NVDA community template. When this option is enabled, the project can also be automatically published to the newly created repository.

The generated project structure is based on the official NVDA community add-on template:

[https://github.com/nvaccess/addonTemplate](https://github.com/nvaccess/addonTemplate)

## Main Features

* Intuitive and accessible graphical interface.
* Automatic generation of the initial add-on project structure.
* Automatic population of essential project metadata.
* Option to include documentation and localization folders.
* Option to clone the official NVDA add-on template repository.
* Optional GitHub integration for repository creation and publishing.
* Dedicated settings panel in NVDA.
* Secure storage of GitHub access tokens through Windows Credential Manager.

## Target Audience

Genesis is intended for:

* Beginners who want to create their first NVDA add-on.
* Experienced developers who want to speed up the initial setup of new projects.

## Requirements

### To Use Genesis

No external software or tools are required. The add-on runs directly within NVDA.

### To Develop the Generated Add-on

The following tools are recommended:

* **Python 3.13:** 64-bit version recommended.
  [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

* **Git:** Required for repository operations.
  [https://git-scm.com/](https://git-scm.com/)

* **SCons 4.5.2 or later:** Build automation tool.

  ```bash
  pip install scons
  ```

* **GNU Gettext:** Required to compile translation files.
  [https://gnuwin32.sourceforge.net/downlinks/gettext.php](https://gnuwin32.sourceforge.net/downlinks/gettext.php)

* **Markdown 3.3.0 or later:** Optional dependency for documentation-related features.

  ```bash
  pip install markdown
  ```

## GitHub Integration

GitHub integration is optional. When enabled, Genesis can:

* Create a new remote repository using the official NVDA add-on template.
* Clone the newly created repository into the selected destination folder.
* Generate the add-on project structure.
* Populate configuration files and project metadata.
* Commit and push the generated changes to the remote repository.

Remote publishing depends on the settings configured under:

**`NVDA > Preferences > Settings > Genesis`**

This section allows you to enable or disable GitHub publishing and configure the repository owner, which can be either a GitHub user or an organization.

You can also configure the repository visibility by choosing whether the repository should be public or private.

When GitHub publishing is disabled:

* No authentication is requested.
* No repository is created or modified on GitHub.
* The project is generated locally only.

## GitHub Authentication

To create and publish repositories on GitHub, Genesis uses a Personal Access Token (PAT).

When **Allow publishing repositories on GitHub** is enabled, Genesis checks whether a token is already stored in Windows Credential Manager.

If no token is registered, an authentication dialog is displayed so that you can enter and validate your credentials before continuing with project creation.

After successful validation, the token is stored in **Windows Credential Manager**. It is not saved in NVDA settings or included in the generated project files.

If a token is already stored, Genesis automatically retrieves it during the creation and publishing process without requesting authentication again.

### How to Generate a GitHub Token

1. Open the GitHub token settings page:
   [https://github.com/settings/tokens](https://github.com/settings/tokens)

2. Choose the appropriate token type:
   * **Fine-grained personal access tokens:** Allow you to configure specific permissions and restrict access to selected repositories.
   * **Tokens (classic):** Use a broader permission model.

3. Enter a name to identify the token.
4. Configure the desired expiration period.
5. Grant the permissions required to create and publish repositories.
6. Generate the token and copy its value.
7. Enter the token in the authentication dialog displayed by Genesis.

**Important:** The required permissions depend on the token type and the operations being performed. The token must allow repository creation and the publishing of files to GitHub.

### Token Security

* The token is stored in Windows Credential Manager.
* Genesis does not save the token in NVDA settings.
* The token is not included in generated project files.
* The token is retrieved by the add-on only when needed for GitHub operations.
* The token can be revoked at any time through your GitHub account settings.

## Installation

### Via the Add-on Store

1. Open NVDA.
2. Go to **Tools > Add-on Store**.
3. Open the **Available** tab.
4. Search for **Genesis**.
5. Select the add-on and choose **Install**.
6. Restart NVDA if requested.

### Manual Installation

1. Visit the official Genesis repository:
   [https://github.com/EdilbertoFonseca/genesis](https://github.com/EdilbertoFonseca/genesis)

2. Download the `genesis.nvda-addon` file from the *Releases* section.

3. Locate the downloaded file and press Enter to start the installation.

4. Follow the instructions provided by NVDA.

5. Restart NVDA if necessary.

## Technical Features

* Uses the official NVDA add-on template as its foundation.
* Generates projects compatible with the official build system.
* Supports local project creation without requiring authentication.
* Provides optional GitHub integration.
* Automatically applies project metadata to the `buildVars.py` file.
* Uses Windows Credential Manager to securely store GitHub access tokens.
* Organizes the project structure according to the official template conventions.

## Keyboard Shortcuts

| Shortcut | Action |
| --- | --- |
| NVDA+Alt+G | Opens Genesis. |
| Alt+G | Generates a new project. |
| Alt+L | Clears all fields. |
| Alt+T | Clones the official NVDA repository. |
| Alt+S | Closes Genesis. |

## Translation

Translations for this add-on are managed through the [NVDA Add-ons project on Crowdin](https://crowdin.com/project/nvdaaddons).

To contribute a translation:

1. Create a Crowdin account.
2. Join the team for the appropriate language, if necessary.
3. Translate the available interface and documentation strings directly on Crowdin.

You can also use Poedit to work locally with `.po` and `.xliff` files.

Completed translations are synchronized with the add-on repository through the localization workflow.

For questions or assistance, join the [NVDA translations mailing list](https://groups.io/g/nvda-translations).
