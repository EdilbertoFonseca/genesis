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
TEMPLATE_PATH = os.path.join(ADDON_PATH, "buildVars.py.tpl")

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
			"allowGithubPublish": "boolean(default=True)",
			"repoPrivate": "boolean(default=True)",
			"repoOwner": 'string(default="")',
			"repoDescription": 'string(default="")',
			"projectDir": 'string(default="")',
		}

	except Exception as e:
		log.error(f"Error initializing Genesis configuration: {e}")


def _getSection() -> Dict[str, Any]:
	"""Return the configuration section corresponding to the add-on."""
	addon = addonHandler.getCodeAddon()
	return cast(Dict[str, Any], config.conf[addon.name])


#  GETTERS


def getAllowGithubPublish():
	return _getSection().get("allowGithubPublish", True)


def getRepoPrivate():
	return _getSection().get("repoPrivate", True)


def getRepoOwner():
	return _getSection().get("repoOwner", "")


def getRepoDescription():
	return _getSection().get("repoDescription", "")


def getProjectDir():
	return _getSection().get("projectDir", "")


#  SETTERS


def setAllowGithubPublish(val: bool):
	_getSection()["allowGithubPublish"] = bool(val)


def setRepoPrivate(val: bool):
	_getSection()["repoPrivate"] = bool(val)


def setRepoOwner(val: str):
	_getSection()["repoOwner"] = val or ""


def setRepoDescription(val: str):
	_getSection()["repoDescription"] = val or ""


def setProjectDir(path: str):
	_getSection()["projectDir"] = path or ""
