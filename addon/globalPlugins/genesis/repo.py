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

Created on: 30/06/2025
"""

import addonHandler
import requests
from logHandler import log

from .varsConfig import (
	getAllowGithubPublish,
	getRepoDescription,
	getRepoOwner,
	getRepoPrivate,
)

# Initialize translation support
addonHandler.initTranslation()


def createRepoFromGithubTemplate(repositoryName, description, private, token, owner):
	"""
	Creates a new repository on GitHub using the official NVAccess addonTemplate as a template.

	Data Priority:
	1. Prefer user-defined values in the add-on settings.
	2. If none exist, use values passed by the interface (Genesis dialog).
	"""

	# 1 - Check if publishing is allowed
	if not getAllowGithubPublish():
		# translators: Error message shown when repository creation is disabled.
		return False, _("Repository creation is disabled in the add-on settings.")

	# 2 - Apply configuration overrides (only if they exist)
	owner = getRepoOwner() or owner
	description = getRepoDescription() or description
	private = getRepoPrivate()

	if not token:
		# translators: Error message shown when repository creation is disabled.
		return False, _("Missing GitHub access token.")

	if not owner:
		# translators: Error message shown when repository creation is disabled.
		return False, _("GitHub owner/organization was not provided.")

	templateOwner = "nvaccess"
	templateRepo = "addonTemplate"
	url = f"https://api.github.com/repos/{templateOwner}/{templateRepo}/generate"

	headers = {
		"Authorization": f"Bearer {token.strip()}",
		"Accept": "application/vnd.github.v3+json",
	}

	payload = {
		"owner": owner.strip(),
		"name": repositoryName.strip(),
		"description": description.strip(),
		"private": bool(private),
		"include_all_branches": False,
	}

	try:
		response = requests.post(url, headers=headers, json=payload)

		# If success
		if response.status_code == 201:
			# translators: Status message shown when the repository is created successfully.
			return True, _("Repository created successfully!")

		# Unauthorized
		if response.status_code == 401:
			# translators: Error message shown when repository creation is disabled.
			return False, _("Invalid token or insufficient permissions.")

		# Other error - assemble detailed message
		try:
			error_data = response.json()
		except Exception:
			# translators: Error message shown when repository creation is disabled.
			return False, _("Unknown error: {}").format(response.text)

		message = error_data.get("message", _("Unknown error."))

		# Extra error details
		errors = error_data.get("errors", [])
		if isinstance(errors, list) and errors:
			details = "\n".join(
				f"- {e.get('message', str(e))}" if isinstance(e, dict) else f"- {str(e)}" for e in errors
			)
			message = f"{message}\n{_('Details:')}\n{details}"

		return False, f"Erro ({response.status_code}): {message}"

	except requests.exceptions.RequestException as e:
		log.error(f"GitHub connection error: {e}")
		# translators: Error message shown when there is a connection error.
		return False, _("Connection error: {}").format(e)


def validateToken(token):
	"""
	Validates a GitHub personal access token.
	Returns True if token is valid, False otherwise.
	"""
	try:
		resp = requests.get(
			"https://api.github.com/user",
			headers={"Authorization": f"Bearer {token.strip()}"},
		)
		return resp.status_code == 200
	except Exception as e:
		log.error(f"Token validation error: {e}")
		return False
