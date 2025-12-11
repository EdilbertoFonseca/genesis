# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 21/11/2024.
"""

import os
import shutil
import sys
import threading

import addonHandler
import ui
import wx
from logHandler import log

from .addonUtils import create_addon_structure, fill_template
from .repo import create_repo_from_github_template
from .varsConfig import addonPath, get_allow_github_publish

# Add the lib/ folder to sys.path
libPath = os.path.join(addonPath, "lib")
if libPath not in sys.path:
	sys.path.insert(0, libPath)

try:
	import git
	from git import Repo
except ImportError as e:
	log.error("Error importing git module: {}".format(str(e)))
	raise ImportError("The required library gitpython is missing.")

# Initialize translation support
addonHandler.initTranslation()


class CloneNVDARepoThread(threading.Thread):
	"""
	THREAD: Clone official NVDA repository
	"""

	def __init__(self, parent, repo_url, target_folder, progress_dialog):
		super().__init__()
		self.parent = parent
		self.repo_url = repo_url
		self.target_folder = target_folder
		self.progress_dialog = progress_dialog

	def run(self):
		repo_nvda_path = os.path.join(self.target_folder, "NVDA")

		try:
			wx.CallAfter(self.progress_dialog.status.SetLabel, _("Checking destination folder..."))
			wx.CallAfter(self.progress_dialog.progress.Pulse)

			if os.path.exists(repo_nvda_path):
				wx.CallAfter(self.progress_dialog.status.SetLabel, _("Removing existing folder..."))
				shutil.rmtree(repo_nvda_path)

			if self.progress_dialog.cancelled:
				wx.CallAfter(ui.message, _("Clone operation canceled."))
				return

			wx.CallAfter(self.progress_dialog.status.SetLabel, _("Cloning NVDA repository..."))
			wx.CallAfter(self.progress_dialog.progress.Pulse)

			git.Repo.clone_from(self.repo_url, repo_nvda_path)

			if self.progress_dialog.cancelled:
				shutil.rmtree(repo_nvda_path)
				wx.CallAfter(ui.message, _("Operation canceled and folder removed."))
				return

			wx.CallAfter(self.progress_dialog.status.SetLabel, _("Finalizing..."))
			wx.CallAfter(self.progress_dialog.progress.SetValue, 100)
			wx.CallAfter(ui.message, _("Clone completed successfully!"))

		except Exception as e:
			msg = _("Error while cloning the repository: {}").format(e)
			log.error(msg)
			wx.CallAfter(ui.message, msg)

		finally:
			wx.CallAfter(self.progress_dialog.Destroy)


class AddonCreationThread(threading.Thread):
	"""
	THREAD: Create Add-on Structure
	"""

	def __init__(self, parent, base_folder, repo_name, description, owner, token,
				 private, template_path, variables):
		super().__init__()
		self.parent = parent
		self.base_folder = base_folder
		self.repo_name = repo_name
		self.description = description
		self.owner = owner
		self.token = token
		self.private = private
		self.template_path = template_path
		self.variables = variables

		# User repository URL (only if publishing is enabled)
		self.user_repo_url = f"https://github.com/{self.owner}/{self.repo_name}.git" if owner else None

		# URL of the official NVDA template
		self.official_template_url = "https://github.com/nvaccess/addonTemplate.git"

	def run(self):
		total_steps = 100
		step = 0
		increment = total_steps // 4  # integer

		try:
			publish_enabled = get_allow_github_publish() and self.token and self.owner

			# STEP 1 - Optional GitHub repository creation
			if publish_enabled:
				wx.CallAfter(self._update_progress, step, _("Creating GitHub repository..."))
				ok, message = create_repo_from_github_template(
					self.repo_name,
					self.description,
					self.private,
					self.token,
					self.owner
				)
				if not ok:
					wx.CallAfter(self.parent.show_message, message, _("GitHub Error"), wx.OK | wx.ICON_ERROR)
					wx.CallAfter(self.parent.progress_dialog.Destroy)
					return
			else:
				wx.CallAfter(self._update_progress, step, _("Skipping GitHub repository creation..."))

			step += increment

			# STEP 2 - Clone template according to the publish option
			wx.CallAfter(self._update_progress, step, _("Cloning template repository..."))
			self._clone_template_repo()
			step += increment

			# STEP 3 - Create add-on folder structure
			wx.CallAfter(self._update_progress, step, _("Generating add-on structure..."))
			create_addon_structure(
				self.base_folder,
				self.variables["module"],
				doc=self.parent.addon_doc.IsChecked(),
				locale=self.parent.addon_locale.IsChecked()
			)
			step += increment

			# STEP 4 - Fill in template files
			wx.CallAfter(self._update_progress, step, _("Finalizing add-on..."))
			fill_template(self.template_path, self.base_folder, self.variables)

			wx.CallAfter(
				self.parent.show_message,
				_("The necessary structure for the development of the add-on was successfully created!")
			)
			wx.CallAfter(self.parent.progress_dialog.Destroy)

		except Exception as e:
			log.exception(f"Unexpected error during add-on creation: {e}")
			wx.CallAfter(self.parent.show_message, _("An error occurred during the creation of the add-on."))
			wx.CallAfter(self.parent.progress_dialog.Destroy)

	# Updates progress in the dialog
	def _update_progress(self, value, message):
		try:
			value = int(value)
			self.parent.progress_dialog.progress.SetValue(value)
			self.parent.progress_dialog.status.SetLabel(message)
			wx.CallAfter(self.parent.progress_dialog.Refresh)
		except Exception as e:
			log.error(f"Failed to update progress dialog: {e}")

	# Function to clone template
	def _clone_template_repo(self):
		if not os.path.exists(self.base_folder):
			os.makedirs(self.base_folder)

		if self.user_repo_url:  # publicar == True
			wx.CallAfter(log.info, f"Cloning your GitHub repository: {self.user_repo_url}")
			Repo.clone_from(self.user_repo_url, self.base_folder)
			wx.CallAfter(log.info, f"Repository cloned successfully from your account: {self.user_repo_url}")

		else:  # publicar == False
			wx.CallAfter(log.info, f"Cloning official template: {self.official_template_url}")
			Repo.clone_from(self.official_template_url, self.base_folder)
			wx.CallAfter(log.info, "Template cloned successfully")

			# Remove original .git (to avoid commits pointing to addonTemplate)
			git_dir = os.path.join(self.base_folder, ".git")
			if os.path.exists(git_dir):
				def remove_readonly(func, path, excinfo):
					import stat
					if not os.access(path, os.W_OK):
						os.chmod(path, stat.S_IWRITE)
						func(path)
					else:
						raise
				shutil.rmtree(git_dir, onerror=remove_readonly)
				wx.CallAfter(log.info, "Removed original .git from template")

			# Initialize new repo
			repo = Repo.init(self.base_folder)
			wx.CallAfter(log.info, "Initialized new Git repository")

			# Add remote based on user and repository name
			if self.owner and self.repo_name:
				new_url = f"https://github.com/{self.owner}/{self.repo_name}.git"
				repo.create_remote("origin", new_url)
				wx.CallAfter(log.info, f"Added remote origin: {new_url}")
			else:
				wx.CallAfter(log.warning, "Owner or repo_name not defined; remote not added")

		return
