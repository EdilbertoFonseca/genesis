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

Created on: 21/11/2024.
"""

import os
import shutil
import stat
import subprocess
import sys
import threading
import time

import addonHandler
import ui
import wx
from logHandler import log

from .addonUtils import createAddonStructure, fillTemplate
from .repo import createRepoFromGithubTemplate
from .varsConfig import ADDON_PATH, getAllowGithubPublish, getRepoOwner

libPath = os.path.join(ADDON_PATH, "lib")
if libPath not in sys.path:
	sys.path.insert(0, libPath)

# GitPython import
try:
	from git import Repo
except ImportError:
	log.error("GitPython is not installed. Install: pip install gitpython")
	raise

# Initialize translation support
addonHandler.initTranslation()


class CloneNVDARepoThread(threading.Thread):
	def __init__(self, parent, repoURL, targetFolder, progressDialog):
		super().__init__(daemon=True)
		self.parent = parent
		self.repoURL = repoURL
		self.targetFolder = targetFolder
		self.progressDialog = progressDialog
		self._currentProc = None

	def run(self):
		repoPath = os.path.join(self.targetFolder, "NVDA")

		try:
			# translators: Initial status message shown in the progress dialog when an operation starts.
			wx.CallAfter(self.progressDialog.status.SetLabel, _("Checking destination folder..."))
			wx.CallAfter(self.progressDialog.progress.Pulse)

			if os.path.exists(repoPath):
				# translators: Status message shown in the progress dialog when an existing folder is removed.
				wx.CallAfter(self.progressDialog.status.SetLabel, _("Removing existing folder..."))
				shutil.rmtree(repoPath)

			if self.progressDialog.cancelled:
				# translators: Status message shown in the progress dialog when the clone operation is canceled.
				wx.CallAfter(ui.message, _("Clone operation canceled."))
				return

			# translators: Status message shown in the progress dialog when the NVDA repository is being cloned.
			wx.CallAfter(self.progressDialog.status.SetLabel, _("Cloning NVDA repository..."))

			success, msg = self._cloneGit(repoPath)

			if not success:
				# translators: Status message shown in the progress dialog when the cloning fails.
				wx.CallAfter(ui.message, msg)
				return

			if self.progressDialog.cancelled:
				shutil.rmtree(repoPath)
				# translators: Status message shown in the progress dialog when the operation is canceled.
				wx.CallAfter(ui.message, _("Operation canceled and folder removed."))
				return

			# translators: Status message shown in the progress dialog when the finalizing step begins.
			wx.CallAfter(self.progressDialog.status.SetLabel, _("Finalizing..."))
			wx.CallAfter(self.progressDialog.progress.SetValue, 100)
			# translators: Status message shown in the progress dialog when the cloning is successful.
			wx.CallAfter(ui.message, _("Clone completed successfully!"))

		except Exception as e:
			# translators: Status message shown in the progress dialog when an error occurs.
			wx.CallAfter(self.progressDialog.status.SetLabel, _("Error occurred."))
			msg = _("Error while cloning the repository: {}").format(e)
			log.error(msg)
			wx.CallAfter(ui.message, msg)

		finally:
			wx.CallAfter(self.progressDialog.Destroy)

	def _cloneGit(self, target):
		"""
		Try to clone with GitPython.
		If it fails, try to clone with a subprocess (git.exe).
		Allows cancellation.
		"""

		try:
			Repo.clone_from(self.repoURL, target)
			# translators: Status message shown in the progress dialog when the cloning is successful.
			return True, _("Repository cloned successfully.")
		except Exception as e:
			log.warning(f"GitPython clone failed, will try subprocess: {e}")

		# Fallback subprocess
		args = ["git", "clone", "--depth=1", self.repoURL, target]

		with subprocess.Popen(
			args,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
			shell=False,
		) as proc:
			self._currentProc = proc

			while proc.poll() is None:
				if self.progressDialog.cancelled:
					proc.terminate()
					self._currentProc = None
					# translators: Status message shown in the progress dialog when the clone operation is canceled.
					return False, _("Clone operation canceled.")
				wx.CallAfter(self.progressDialog.progress.Pulse)
				time.sleep(0.2)

			self._currentProc = None

			if proc.returncode == 0:
				return True, _("Repository cloned successfully.")

			err = proc.stderr.read()
			return False, _("Error cloning repository: {}").format(err)


class AddonCreationThread(threading.Thread):
	def __init__(
		self,
		parent,
		baseFolder,
		repoName,
		description,
		owner,
		token,
		private,
		templatePath,
		variables,
	):
		super().__init__(daemon=True)
		self.parent = parent
		self.baseFolder = baseFolder
		self.repoName = repoName
		self.description = description
		self.owner = owner
		self.token = token
		self.private = private
		self.templatePath = templatePath
		self.variables = variables

		self.userRepoURL = f"https://github.com/{owner}/{repoName}.git" if owner else None
		self.officialTemplateURL = "https://github.com/nvaccess/addonTemplate.git"

	def run(self):
		try:
			step = 0
			step_inc = 25

			# STEP 1 - Create GitHub repository
			if getAllowGithubPublish() and self.owner and self.token:
				wx.CallAfter(self._progress, step, _("Creating GitHub repository..."))
				ok, msg = createRepoFromGithubTemplate(
					self.repoName,
					self.description,
					self.private,
					self.token,
					self.owner,
				)
				if not ok:
					# translators: Status message shown in the progress dialog when the GitHub repository creation fails.
					wx.CallAfter(self.parent.showMessage, msg, _("GitHub Error"))
					wx.CallAfter(self.parent.progress_dialog.Destroy)
					return
			else:
				# translators: Status message shown in the progress dialog when the GitHub repository creation is skipped.
				wx.CallAfter(self._progress, step, _("Skipping GitHub repository creation..."))

			step += step_inc

			# translators: Status message shown in the progress dialog when the template repository is being cloned.
			wx.CallAfter(self._progress, step, _("Cloning template repository..."))
			self._cloneTemplateRepo()
			step += step_inc

			# translators: Status message shown in the progress dialog when the add-on structure is being generated.
			wx.CallAfter(self._progress, step, _("Generating add-on structure..."))
			createAddonStructure(
				self.baseFolder,
				self.variables["module"],
				doc=self.parent.checkAddonDoc.GetValue(),
				locale=self.parent.checkAddonLocale.GetValue(),
			)
			step += step_inc

			# translators: Status message shown in the progress dialog when the template files are being filled.
			wx.CallAfter(self._progress, step, _("Finalizing add-on..."))
			fillTemplate(self.templatePath, self.baseFolder, self.variables)

			wx.CallAfter(
				self.parent.showMessage,
				# translators: Status message shown in the progress dialog when the add-on structure is successfully created.
				_("The necessary structure for the development of the add-on was successfully created!"),
			)
			wx.CallAfter(self.parent.progressDialog.Destroy)

		except Exception as e:
			log.exception(f"Unexpected error during add-on creation: {e}")
			# translators: Status message shown in the progress dialog when an unexpected error occurs.
			wx.CallAfter(self.parent.showMessage, _("An error occurred during the creation of the add-on."))
			wx.CallAfter(self.parent.progressDialog.Destroy)

	def _progress(self, value, message):
		self.parent.progressDialog.progress.SetValue(value)
		self.parent.progressDialog.status.SetLabel(message)
		wx.CallAfter(self.parent.progressDialog.Refresh)

	def _cloneTemplateRepo(self):
		"""
		Prepare the add-on repository using the official NVDA addonTemplate.
		"""

		def _removeReadonly(func, path, _):
			try:
				os.chmod(path, stat.S_IWRITE)
				func(path)
			except Exception as e:
				wx.CallAfter(log.error, f"Erro ao remover {path}: {e}")

		# Safety check
		if os.path.exists(self.baseFolder):
			raise RuntimeError(
				f"Destination folder already exists: {self.baseFolder}",
			)

		# CASE 1: Publishing enabled
		if getAllowGithubPublish() and self.owner and self.token:
			userRepoURL = f"https://github.com/{self.owner}/{self.repoName}.git"

			wx.CallAfter(log.info, f"Cloning published repository: {userRepoURL}")

			repo = Repo.clone_from(userRepoURL, self.baseFolder)

			wx.CallAfter(log.info, "User repository cloned successfully")

			try:
				repo.git.checkout("master")
				wx.CallAfter(log.info, "Checked out master branch")
			except Exception as e:
				wx.CallAfter(log.warning, f"Could not checkout master branch: {e}")

			return

		# CASE 2: Local project only
		wx.CallAfter(log.info, f"Cloning official template: {self.officialTemplateURL}")

		repo = Repo.clone_from(
			self.officialTemplateURL,
			self.baseFolder,
		)

		wx.CallAfter(log.info, "Official addonTemplate cloned successfully")

		# Remove .git
		gitDir = os.path.join(self.baseFolder, ".git")

		if os.path.exists(gitDir):
			try:
				shutil.rmtree(gitDir, onerror=_removeReadonly)
				wx.CallAfter(log.info, ".git removed successfully")
			except Exception as e:
				wx.CallAfter(log.error, f"Error removing .git: {e}")
				raise

		# wx.CallAfter(log.info, f"Does .git exist after removal? {os.path.exists(gitDir)}")  # DEBUG

		# Initialize new repository
		wx.CallAfter(log.info, "Initializing new repository...")

		new_repo = Repo.init(self.baseFolder)
		new_repo.git.checkout("-B", "master")

		wx.CallAfter(log.info, "New initialized repository")

		self.owner = getRepoOwner()

		# Create remote
		if self.owner and self.repoName:
			remoteURL = f"https://github.com/{self.owner}/{self.repoName}.git"

			new_repo.create_remote("origin", remoteURL)

			wx.CallAfter(log.info, f"Origin configured: {remoteURL}")
		else:
			wx.CallAfter(log.warning, "Owner or repoName not defined - remote not created")

		# Initial commit
		new_repo.git.add(all=True)
		new_repo.index.commit("Initial commit")

		wx.CallAfter(log.info, "Initial commit created successfully")
