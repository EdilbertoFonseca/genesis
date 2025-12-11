# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 05/06/2025
"""

import os

import addonHandler
import config
from logHandler import log

# Section in configuration file
SECTION = "genesis"

# Get the path to the root of the current add-on
addonPath = os.path.dirname(__file__)

# Define the path to the template repository
template_repo_url = "https://github.com/nvaccess/addonTemplate.git"
TEMPLATE_PATH = os.path.join(addonPath, "buildVars.py.tpl")

# Get the add-on summary contained in the manifest.
ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]

def git_conf():
	"""
	Configures environment variables required for Git operations.
	This function sets the following environment variables:
	- GIT_SSL_CAINFO: Specifies the path to the CA bundle for SSL certificate verification.
	- GIT_PYTHON_GIT_EXECUTABLE: Specifies the full path to the Git executable.
	These settings ensure that Git commands invoked from Python use the correct SSL certificates and Git binary.
	Returns:
		None
	"""
	
	os.environ["GIT_SSL_CAINFO"] = r"F:\PortableApps\CommonFiles/Git/mingw64/ssl/certs/ca-bundle.crt"
	# Define the full path to the Git executable
	os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = r"F:\PortableApps\CommonFiles\Git\bin\git.exe"
	return

def initConfiguration():
	"""
	Initializes the configuration schema for the Genesis add-on.
	Using config.conf.spec, as recommended by NVDA.	
	"""
	try:
		addon = addonHandler.getCodeAddon()

		confspec = {
			"allowGithubPublish": "boolean(default=True)",
			"repoPrivate": "boolean(default=True)",
			"repoOwner": 'string(default="")',
			"projectDir": "string(default=\"\")",
		}

		config.conf.spec[addon.name] = confspec

	except Exception as e:
		log.error(f"Error initializing Genesis configuration: {e}")

def _get_config_section():
	addon = addonHandler.getCodeAddon()
	return config.conf[addon.name]


# GETTERS e SETTERS
def get_allow_github_publish():
	return _get_config_section().get("allowGithubPublish", True)

def set_allow_github_publish(v: bool):
	_get_config_section()["allowGithubPublish"] = v

def get_repo_private():
	return _get_config_section().get("repoPrivate", True)

def set_repo_private(v: bool):
	_get_config_section()["repoPrivate"] = v

def get_repo_owner():
	return _get_config_section().get("repoOwner", "")

def set_repo_owner(v: str):
	_get_config_section()["repoOwner"] = v

def get_repo_description():
	return _get_config_section().get("repoDescription", "")

def set_repo_description(v: str):
	_get_config_section()["repoDescription"] = v
def get_project_dir():
    return config.conf["genesis"].get("projectDir", "")

def set_project_dir(path: str):
    config.conf["genesis"]["projectDir"] = path
