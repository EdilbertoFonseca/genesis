# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 30/06/2025
"""

import addonHandler
import requests

from .varsConfig import (
	get_allow_github_publish,
	get_repo_description,
	get_repo_owner,
	get_repo_private,
)

# Initialize translation support
addonHandler.initTranslation()

def create_repo_from_github_template(repository_name, description, private, token, owner):
	# 1 - Check permission in the panel
	if not get_allow_github_publish():
		return False, _("Repository creation is disabled in the add-on settings.")

	# 2 - Apply settings
	private = get_repo_private()
	owner = get_repo_owner() or owner
	description = get_repo_description() or description

	template_owner = "nvaccess"
	template_repo = "addonTemplate"
	url = f"https://api.github.com/repos/{template_owner}/{template_repo}/generate"

	headers = {
		"Authorization": f"token {token.strip()}",
		"Accept": "application/vnd.github.v3+json"
	}

	payload = {
		"owner": owner.strip(),
		"name": repository_name.strip(),
		"description": description.strip(),
		"private": private,
		"include_all_branches": False
	}

	try:
		response = requests.post(url, headers=headers, json=payload)

		if response.status_code == 201:
			return True, _("Repository created successfully!")
		elif response.status_code == 401:
			return False, _("Invalid token or insufficient permissions.")
		else:
			try:
				error_data = response.json()
				message = error_data.get(_("message"), _("Unknown error."))
				errors = error_data.get("errors", [])
				if isinstance(errors, list):
					details = "\n".join(
						f"- {e.get('message', str(e))}" if isinstance(e, dict) else f"- {str(e)}"
						for e in errors
					)
					message += f"\nDetalhes:\n{details}"
			except Exception:
				message = response.text
			return False, f"Erro ({response.status_code}): {message}"

	except requests.exceptions.RequestException as e:
		return False, _(f"Connection error or request: {e}")


def validate_token(token):
	headers = {"Authorization": f"token {token}"}
	resp = requests.get("https://api.github.com/user", headers=headers)
	return resp.status_code == 200
