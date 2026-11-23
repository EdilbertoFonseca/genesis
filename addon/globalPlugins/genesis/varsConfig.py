# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 - 2026 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

-------------------------------------------------------------------------
AI DISCLOSURE / NOTA DE IA:
This project utilizes AI for code refactoring and logic suggestions.
All AI-generated code was manually reviewed and tested by the author.
-------------------------------------------------------------------------

Created on: 05/06/2025
"""

import os
from typing import Any, Dict, cast

import addonHandler
import config
from logHandler import log

# Initialize translation
addonHandler.initTranslation()

# Add-on path
ADDON_PATH = os.path.dirname(__file__)

# buildVars template path
TEMPLATE_PATH_BUILD_VARS = os.path.join(ADDON_PATH, "buildVars.py.tpl")

# pyproject template path
TEMPLATE_PATH_PY_PROJECT = os.path.join(ADDON_PATH, "pyproject.toml.tpl")

# Summary of the add-on (manifest)
ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]


def gitConf():
	"""
	(Disabled - optional use)

	Configures Git global environment variables.
	This function should NOT be enabled for regular users,
	as Git's location varies from machine to machine
	and modifying global variables is not recommended in NVDA add-ons.

	Use only if you really need to,
	and adjust paths according to your local installation.
	"""

	# EXAMPLE - edit as needed
	# os.environ["GIT_SSL_CAINFO"] = r"C:\Path\to\Git\ssl\certs\ca-bundle.crt"
	# os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = r"C:\Path\to\Git\bin\git.exe"
	return


def initConfiguration():
	"""
	Initializes the configuration schema in NVDA.
	Uses config.conf.spec, as recommended by NVAccess.
	"""
	try:
		addon = addonHandler.getCodeAddon()

		config.conf.spec[addon.name] = {
			"repoOwner": 'string(default="")',
			"allowGithubPublish": "boolean(default=True)",
			"repoPrivate": "boolean(default=True)",
			"projectDir": 'string(default="")',
			"repoDescription": 'string(default="")',
			"addonCreator": 'string(default="")',
			"emailAddress": 'string(default="")',
		}

	except Exception as e:
		log.error(f"Error initializing Genesis configuration: {e}")


def _getSection() -> Dict[str, Any]:
	"""Return the configuration section corresponding to the add-on."""
	addon = addonHandler.getCodeAddon()
	return cast(Dict[str, Any], config.conf[addon.name])


#  GETTERS


def getAllowGithubPublish():
	"""Return the allowGithubPublish setting from the Genesis configuration."""
	return _getSection().get("allowGithubPublish", True)


def getRepoPrivate():
	"""Return the repository privacy setting from the Genesis configuration."""
	return _getSection().get("repoPrivate", True)


def getRepoOwner():
	"""Return the repository owner from the Genesis configuration."""
	return _getSection().get("repoOwner", "")


def getRepoDescription():
	"""Return the repository description from the Genesis configuration."""
	return _getSection().get("repoDescription", "")


def getProjectDir():
	"""Return the project directory path from the Genesis configuration."""
	return _getSection().get("projectDir", "")


def getAddonCreator():
	"""Return the add-on creator's name from the Genesis configuration."""
	return _getSection().get("addonCreator", "")


def getEmailAddress():
	"""Return the email address from the Genesis configuration."""
	return _getSection().get("emailAddress", "")


#  SETTERS


def setAllowGithubPublish(val: bool):
	"""Sets the allowGithubPublish setting in the Genesis configuration."""
	_getSection()["allowGithubPublish"] = bool(val)


def setRepoPrivate(val: bool):
	"""Sets the repository privacy setting in the Genesis configuration."""
	_getSection()["repoPrivate"] = bool(val)


def setRepoOwner(val: str):
	"""Sets the repository owner in the Genesis configuration."""
	_getSection()["repoOwner"] = val or ""


def setRepoDescription(val: str):
	"""Sets the repository description in the Genesis configuration."""
	_getSection()["repoDescription"] = val or ""


def setProjectDir(path: str):
	"""Sets the project directory path in the Genesis configuration."""
	_getSection()["projectDir"] = path or ""


def setAddonCreator(val: str):
	"""Sets the add-on creator's name in the Genesis configuration."""
	_getSection()["addonCreator"] = val or ""


def setEmailAddress(val: str):
	"""Sets the email address in the Genesis configuration."""
	_getSection()["emailAddress"] = val or ""
