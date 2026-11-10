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
)

# Initialize translation support
addonHandler.initTranslation()


GITHUB_API_URL = "https://api.github.com"
GITHUB_TEMPLATE_OWNER = "nvaccess"
GITHUB_TEMPLATE_REPO = "addonTemplate"

REQUEST_TIMEOUT = 30
TOKEN_VALIDATION_TIMEOUT = 15


def createRepoFromGithubTemplate(repositoryName, description, private, token, owner):
	"""
	Create a new GitHub repository using the official NVDA add-on template.

	Configuration values take precedence over interface values when available.

	Args:
		repositoryName: Name of the repository to create.
		description: Repository description.
		private: Whether the repository should be private.
		token: GitHub personal access token.
		owner: GitHub user or organization that will own the repository.

	Returns:
		A tuple containing the operation status and a message.
	"""

	# Check whether GitHub publishing is enabled.
	if not getAllowGithubPublish():
		# translators: Error message shown when repository creation is disabled.
		return False, _("Repository creation is disabled in the add-on settings.")

	# Apply configuration overrides when available.
	owner = (getRepoOwner() or owner or "").strip()
	description = (getRepoDescription() or description or "").strip()

	repositoryName = (repositoryName or "").strip()
	token = (token or "").strip()

	if not token:
		# translators: Error message shown when the GitHub access token is missing.
		return False, _("Missing GitHub access token.")

	if not owner:
		# translators: Error message shown when the GitHub owner or organization is missing.
		return False, _("GitHub owner/organization was not provided.")

	if not repositoryName:
		# translators: Error message shown when the repository name is missing.
		return False, _("Repository name was not provided.")

	url = f"{GITHUB_API_URL}/repos/{GITHUB_TEMPLATE_OWNER}/{GITHUB_TEMPLATE_REPO}/generate"

	headers = {
		"Authorization": f"Bearer {token}",
		"Accept": "application/vnd.github+json",
		"X-GitHub-Api-Version": "2022-11-28",
	}

	payload = {
		"owner": owner,
		"name": repositoryName,
		"description": description,
		"private": bool(private),
		"include_all_branches": False,
	}

	try:
		response = requests.post(
			url,
			headers=headers,
			json=payload,
			timeout=REQUEST_TIMEOUT,
		)

	except requests.exceptions.RequestException as e:
		log.error(f"GitHub connection error: {e}")
		# translators: Error message shown when the connection to GitHub fails.
		return False, _("Connection error: {}").format(e)

	# comentado para teste
	# if response.status_code == 201:
	# translators: Status message shown when the repository is created successfully.
	# return True, _("Repository created successfully!")

	if response.status_code == 201:
		repositoryData = response.json()

		defaultBranch = repositoryData.get("default_branch")
		repositoryURL = repositoryData.get("html_url")

		log.info(
			f"GitHub repository created successfully. URL: {repositoryURL}. Default branch: {defaultBranch}",
		)

		if defaultBranch != "master":
			log.warning(
				"Expected default branch 'master', but GitHub "
				+ f"created the repository with '{defaultBranch}'.",
			)

	return True, _("Repository created successfully!")
	if response.status_code == 401:
		# translators: Error message shown when the GitHub token is invalid.
		return False, _("Invalid token or insufficient permissions.")

	errorData = {}

	try:
		result = response.json()
		if isinstance(result, dict):
			errorData = result
	except ValueError:
		pass

	message = errorData.get("message")

	if not message:
		message = response.text.strip()

	if not message:
		# translators: Generic error message returned when GitHub provides no details.
		message = _("Unknown error.")

	errors = errorData.get("errors", [])

	if isinstance(errors, list) and errors:
		details = []

		for error in errors:
			if isinstance(error, dict):
				details.append(error.get("message", str(error)))
			else:
				details.append(str(error))

		# translators: Label preceding additional error details returned by GitHub.
		message = f"{message}\n{_('Details:')}\n" + "\n".join(f"- {detail}" for detail in details)

	log.error(
		f"GitHub repository creation failed. HTTP status: {response.status_code}. Message: {message}",
	)

	# translators: Error message containing the HTTP status returned by GitHub.
	return False, _("Error ({}): {}").format(response.status_code, message)


def validateToken(token):
	"""
	Validate a GitHub personal access token.

	Args:
		token: GitHub personal access token.

	Returns:
		True if the token is valid, False otherwise.
	"""

	token = (token or "").strip()

	if not token:
		return False

	try:
		response = requests.get(
			f"{GITHUB_API_URL}/user",
			headers={
				"Authorization": f"Bearer {token}",
				"Accept": "application/vnd.github+json",
				"X-GitHub-Api-Version": "2022-11-28",
			},
			timeout=TOKEN_VALIDATION_TIMEOUT,
		)

		return response.status_code == 200

	except requests.exceptions.RequestException as e:
		log.error(f"Token validation error: {e}")
		return False
