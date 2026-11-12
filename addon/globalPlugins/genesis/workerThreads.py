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

import base64
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import quote

import addonHandler
import requests
import ui
import wx
from logHandler import log

from .addonUtils import createAddonStructure, fillTemplate
from .credentialManager import getGithubToken
from .repo import createRepoFromGithubTemplate
from .varsConfig import ADDON_PATH, getAllowGithubPublish

LIB_PATH = os.path.join(ADDON_PATH, "lib")
if LIB_PATH not in sys.path:
	sys.path.insert(0, LIB_PATH)

# GitPython import
try:
	from git import Repo
except ImportError:
	log.error("GitPython is not installed. Install: pip install gitpython")
	raise

# Initialize translation support
addonHandler.initTranslation()


class OperationCancelled(Exception):
	"""Raised when an operation is canceled by the user."""


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
			self._updateStatus(_("Checking destination folder..."))
			self._updateProgress()

			if os.path.exists(repoPath):
				# translators: Status message shown in the progress dialog when an existing folder is removed.
				self._updateStatus(_("Removing existing folder..."))
				shutil.rmtree(repoPath)

			if self._isCancelled():
				# translators: Message displayed when the clone operation is canceled.
				self._showMessage(_("Clone operation canceled."))
				return

			# translators: Status message shown in the progress dialog when the NVDA repository is being cloned.
			self._updateStatus(_("Cloning NVDA repository..."))

			success, msg = self._cloneGit(repoPath)

			if not success:
				if not self._isCancelled():
					self._showMessage(msg)
				return

			if self._isCancelled():
				shutil.rmtree(repoPath, ignore_errors=True)
				# translators: Message displayed when the operation is canceled and the cloned folder is removed.
				self._showMessage(_("Operation canceled and folder removed."))
				return

			# translators: Status message shown when the finalizing step begins.
			self._updateStatus(_("Finalizing..."))
			self._setProgress(100)

			# translators: Message displayed when the cloning is successful.
			self._showMessage(_("Clone completed successfully!"))

		except Exception as e:
			# translators: Status message shown when an error occurs.
			self._updateStatus(_("Error occurred."))
			msg = _("Error while cloning the repository: {}").format(e)
			log.exception(msg)
			self._showMessage(msg)

		finally:
			wx.CallAfter(self._destroyProgressDialog)

	def _cloneGit(self, target):
		"""
		Clone the repository using GitPython, with a subprocess fallback.

		The subprocess fallback supports cooperative cancellation.
		"""

		try:
			Repo.clone_from(self.repoURL, target)

			if self._isCancelled():
				shutil.rmtree(target, ignore_errors=True)
				# translators: Message displayed when the clone operation is canceled.
				return False, _("Clone operation canceled.")

			# translators: Status message shown when the repository is cloned successfully.
			return True, _("Repository cloned successfully.")

		except Exception as e:
			log.warning(f"GitPython clone failed, trying subprocess fallback: {e}")

			if self._isCancelled():
				# translators: Message displayed when the clone operation is canceled.
				return False, _("Clone operation canceled.")

			if os.path.exists(target):
				shutil.rmtree(target, ignore_errors=True)

		args = ["git", "clone", "--depth=1", self.repoURL, target]

		with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as errorFile:
			with subprocess.Popen(
				args,
				stdout=subprocess.DEVNULL,
				stderr=errorFile,
				text=True,
				shell=False,
			) as proc:
				self._currentProc = proc

				try:
					while proc.poll() is None:
						if self._isCancelled():
							proc.terminate()

							try:
								proc.wait(timeout=5)
							except subprocess.TimeoutExpired:
								proc.kill()
								proc.wait()

							shutil.rmtree(target, ignore_errors=True)

							# translators: Message displayed when the clone operation is canceled.
							return False, _("Clone operation canceled.")

						self._updateProgress()
						time.sleep(0.2)

					if proc.returncode == 0:
						# translators: Status message shown when the repository is cloned successfully.
						return True, _("Repository cloned successfully.")

					errorFile.seek(0)
					err = errorFile.read().strip()

					# translators: Error message displayed when cloning the repository fails.
					return False, _("Error cloning repository: {}").format(
						err or _("Unknown Git error."),
					)

				finally:
					self._currentProc = None

	def _isCancelled(self):
		return self.progressDialog.cancelled

	def _updateStatus(self, message):
		wx.CallAfter(self.progressDialog.status.SetLabel, message)

	def _updateProgress(self):
		wx.CallAfter(self.progressDialog.progress.Pulse)

	def _setProgress(self, value):
		wx.CallAfter(self.progressDialog.progress.SetValue, value)

	def _showMessage(self, message):
		wx.CallAfter(ui.message, message)

	def _destroyProgressDialog(self):
		try:
			self.progressDialog.Destroy()
		except (RuntimeError, wx.PyDeadObjectError):
			pass


class AddonCreationThread(threading.Thread):
	def __init__(
		self,
		parent,
		baseFolder,
		repoName,
		description,
		owner,
		private,
		templatePathBuildVars,
		templatePathPyProject,
		variables,
	):
		super().__init__(daemon=True)

		self.parent = parent
		self.baseFolder = baseFolder
		self.repoName = repoName
		self.description = description
		self.owner = (owner or "").strip()
		self.private = private
		self.templatePathBuildVars = templatePathBuildVars
		self.templatePathPyProject = templatePathPyProject
		self.variables = variables

		self.officialTemplateURL = "https://github.com/nvaccess/addonTemplate.git"

		self.token = None

		self.publishEnabled = bool(
			getAllowGithubPublish() and self.owner,
		)

	def run(self):
		try:
			if self.publishEnabled:
				try:
					self.token = getGithubToken()

				except Exception as e:
					raise RuntimeError(
						_(
							"Unable to retrieve the GitHub access token "
							+ "from Windows Credential Manager.",
						),
					) from e

				if not self.token:
					raise RuntimeError(
						_(
							"GitHub authentication token is missing. "
							+ "Please register a token before continuing.",
						),
					)

			step = 0
			stepInc = 20

			self._checkCancellation()

			# STEP 1 - Create GitHub repository.
			if self.publishEnabled:
				# translators: Status message shown when the GitHub repository is being created.
				self._progress(step, _("Creating GitHub repository..."))

				ok, msg = createRepoFromGithubTemplate(
					self.repoName,
					self.description,
					self.private,
					self.token,
					self.owner,
				)

				if not ok:
					# translators: Title displayed when GitHub repository creation fails.
					self._showError(msg, _("GitHub Error"))
					return
			else:
				# translators: Status message shown when GitHub repository creation is skipped.
				self._progress(step, _("Skipping GitHub repository creation..."))

			self._checkCancellation()
			step += stepInc

			# STEP 2 - Wait for the repository and clone it.
			# translators: Status message shown when waiting for the GitHub repository.
			if self.publishEnabled:
				self._progress(
					step,
					_("Waiting for GitHub repository..."),
				)

				self._waitForRepository()

			# translators: Status message shown when the template repository is being cloned.
			self._progress(step, _("Cloning template repository..."))

			self._cloneTemplateRepo()

			self._checkCancellation()
			step += stepInc

			# STEP 3 - Create add-on structure.
			# translators: Status message shown when the add-on structure is being generated.
			self._progress(step, _("Generating add-on structure..."))

			if not createAddonStructure(
				self.baseFolder,
				self.variables["module"],
				doc=self.variables.get("doc", False),
				locale=self.variables.get("locale", False),
			):
				raise RuntimeError(
					"Could not create the add-on directory structure.",
				)

			self._checkCancellation()
			step += stepInc

			# STEP 4 - Fill template files.
			# translators: Status message shown when the template files are being filled.
			self._progress(step, _("Finalizing add-on..."))

			if not fillTemplate(
				self.templatePathBuildVars,
				self.templatePathPyProject,
				self.baseFolder,
				self.variables,
			):
				raise RuntimeError(
					"Could not fill the add-on template files.",
				)

			self._checkCancellation()
			step += stepInc

			# STEP 5 - Commit and publish changes.
			if self.publishEnabled:
				# translators: Status message shown when generated files are being committed.
				self._progress(step, _("Committing add-on files..."))

				self._publishChanges()

			self._checkCancellation()

			# translators: Status message displayed when the add-on creation is completed.
			self._progress(100, _("Completed."))

			# translators: Message displayed when the add-on is successfully created.
			self._showSuccess(
				_(
					"The necessary structure for the development of the add-on was successfully created!",
				),
			)

		except OperationCancelled:
			self._cancelCreation()

		except Exception as e:
			log.exception(
				f"Unexpected error during add-on creation: {e}",
			)

			# translators: Message displayed when an unexpected error occurs during add-on creation.
			self._showError(
				_("An error occurred during the creation of the add-on: {}").format(e),
			)

	def _progress(self, value, message):
		"""Schedule a progress update in the GUI thread."""

		wx.CallAfter(self._updateProgressUI, value, message)

	def _updateProgressUI(self, value, message):
		"""Update the progress dialog in the GUI thread."""

		dialog = self.parent.progressDialog

		try:
			if dialog:
				dialog.progress.SetValue(value)
				dialog.status.SetLabel(message)
				dialog.Refresh()
		except (RuntimeError, wx.PyDeadObjectError):
			log.debug("Progress dialog is no longer available.")

	def _showSuccess(self, message):
		"""Schedule the success message in the GUI thread."""

		wx.CallAfter(self._displaySuccess, message)

	def _displaySuccess(self, message):
		"""Display the success message and close the progress dialog."""

		self._destroyProgressDialog()
		self.parent.showMessage(message)

	def _showError(self, message, title=None):
		"""Schedule the error message in the GUI thread."""

		wx.CallAfter(self._displayError, message, title)

	def _displayError(self, message, title=None):
		"""Display the error message and close the progress dialog."""

		self._destroyProgressDialog()

		if title is None:
			self.parent.showMessage(message)
		else:
			self.parent.showMessage(message, title)

	def _destroyProgressDialog(self):
		"""Destroy the progress dialog safely."""

		try:
			dialog = self.parent.progressDialog
			if dialog:
				dialog.Destroy()
		except (RuntimeError, wx.PyDeadObjectError):
			log.debug("Progress dialog was already destroyed.")

	def _cancelCreation(self):
		"""Handle cooperative cancellation of the add-on creation process."""

		# translators: Message displayed when add-on creation is canceled.
		self._showError(_("Add-on creation was canceled."))

	def _isCancelled(self):
		try:
			return self.parent.progressDialog.cancelled
		except (AttributeError, RuntimeError, wx.PyDeadObjectError):
			return False

	def _checkCancellation(self):
		if self._isCancelled():
			raise OperationCancelled

	def _getGitAuthEnvironment(self):
		"""
		Build a temporary Git authentication environment.

		The token is not stored in the repository configuration.
		"""

		if not self.token:
			raise RuntimeError("GitHub authentication token is missing.")

		credentials = f"{self.owner}:{self.token}".encode("utf-8")
		authHeader = base64.b64encode(credentials).decode("ascii")

		environment = os.environ.copy()
		environment.update(
			{
				"GIT_CONFIG_COUNT": "1",
				"GIT_CONFIG_KEY_0": "http.extraheader",
				"GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {authHeader}",
			},
		)

		return environment

	def _publishChanges(self):
		"""
		Commit generated files and push them to the GitHub repository.

		Raises:
			RuntimeError: If the repository cannot be committed or published.
		"""

		repo = Repo(self.baseFolder)

		if "origin" not in [remote.name for remote in repo.remotes]:
			raise RuntimeError("The GitHub remote 'origin' was not found.")

		if repo.head.is_detached:
			raise RuntimeError("The repository is in a detached HEAD state.")

		if "master" not in [branch.name for branch in repo.branches]:
			raise RuntimeError("The 'master' branch does not exist.")

		self._checkCancellation()

		# Stage all generated and modified files.
		repo.git.add(A=True)

		# Create a commit only when there are staged changes.
		if repo.is_dirty():
			repo.index.commit("Generate add-on structure")

		self._checkCancellation()

		# Push using temporary authentication.
		# The token is not saved in .git/config.
		# translators: Status message shown when changes are being sent to GitHub.
		self._progress(90, _("Publishing changes to GitHub..."))

		authEnvironment = self._getGitAuthEnvironment()

		try:
			with repo.git.custom_environment(
				GIT_CONFIG_COUNT=authEnvironment["GIT_CONFIG_COUNT"],
				GIT_CONFIG_KEY_0=authEnvironment["GIT_CONFIG_KEY_0"],
				GIT_CONFIG_VALUE_0=authEnvironment["GIT_CONFIG_VALUE_0"],
			):
				if repo.head.is_detached:
					raise RuntimeError(
						"The repository is in a detached HEAD state.",
					)

				branch = repo.active_branch.name

				if branch != "master":
					raise RuntimeError(
						f"Unexpected branch '{branch}'. Expected 'master'.",
					)

				repo.git.push("--set-upstream", "origin", branch)

		except Exception as e:
			log.exception("Could not publish add-on changes to GitHub.")
			raise RuntimeError(
				_("Could not publish the generated files to GitHub: {}").format(e),
			) from e

	def _waitForRepository(self):
		"""
		Wait until the GitHub repository's master branch is available.

		The method periodically checks the remote Git reference through
		the GitHub REST API before allowing the repository to be cloned.

		Raises:
			OperationCancelled: If the user cancels the operation.
			RuntimeError: If the branch is not available within the timeout
				or the GitHub API returns an unexpected response.
		"""

		timeout = 60
		retryInterval = 2
		startTime = time.monotonic()

		owner = quote(self.owner, safe="")
		repositoryName = quote(self.repoName, safe="")

		url = f"https://api.github.com/repos/{owner}/{repositoryName}/git/ref/heads/master"

		headers = {
			"Authorization": f"Bearer {self.token}",
			"Accept": "application/vnd.github+json",
			"X-GitHub-Api-Version": "2022-11-28",
		}

		while time.monotonic() - startTime < timeout:
			self._checkCancellation()

			try:
				response = requests.get(
					url,
					headers=headers,
					timeout=10,
				)

			except requests.exceptions.RequestException:
				pass

			else:
				if response.status_code == 200:
					try:
						referenceData = response.json()
					except ValueError as e:
						raise RuntimeError(
							"GitHub returned an invalid JSON response " + "while checking the master branch.",
						) from e

					commitSha = referenceData.get("object", {}).get("sha")

					if commitSha:
						return

				elif response.status_code not in (404, 409):
					raise RuntimeError(
						"Could not verify GitHub repository readiness. "
						+ f"HTTP status: {response.status_code}. "
						+ f"Response: {response.text}",
					)

			remainingTime = timeout - (time.monotonic() - startTime)

			if remainingTime > 0:
				time.sleep(min(retryInterval, remainingTime))

		raise RuntimeError(
			"Timed out waiting for the GitHub repository's " + "master branch to become available.",
		)

	def _cloneTemplateRepo(self):
		"""
		Prepare the add-on repository using the official NVDA addonTemplate.

		Raises:
			OperationCancelled: If the user cancels the operation.
			RuntimeError: If the destination or cloning operation is invalid.
		"""

		def _removeReadonly(func, path, _):
			try:
				os.chmod(path, stat.S_IWRITE)
				func(path)
			except OSError as e:
				log.error(f"Could not remove {path}: {e}")

		# Validate destination folder.
		if os.path.exists(self.baseFolder):
			if not os.path.isdir(self.baseFolder):
				raise RuntimeError(
					f"Destination path is not a directory: {self.baseFolder}",
				)

			if os.listdir(self.baseFolder):
				raise RuntimeError(
					f"Destination folder is not empty: {self.baseFolder}",
				)

		self._checkCancellation()

		# CASE 1 - Publishing enabled.
		if self.publishEnabled:
			userRepoURL = f"https://github.com/{self.owner}/{self.repoName}.git"

			Repo.clone_from(
				userRepoURL,
				self.baseFolder,
				branch="master",
				env=self._getGitAuthEnvironment(),
			)

			self._checkCancellation()
			return

		# CASE 2 - Local project only.
		Repo.clone_from(
			self.officialTemplateURL,
			self.baseFolder,
		)

		self._checkCancellation()

		# Remove .git.
		gitDir = os.path.join(self.baseFolder, ".git")

		if os.path.exists(gitDir):
			try:
				shutil.rmtree(gitDir, onerror=_removeReadonly)
			except OSError as e:
				log.error(f"Error removing .git: {e}")
				raise

		self._checkCancellation()

		# Initialize a new repository.
		newRepo = Repo.init(self.baseFolder)
		newRepo.git.checkout("-B", "master")

		# Configure remote.
		if self.owner and self.repoName:
			remoteURL = f"https://github.com/{self.owner}/{self.repoName}.git"
			newRepo.create_remote("origin", remoteURL)

		self._checkCancellation()

		# Create initial commit.
		newRepo.git.add(all=True)
		newRepo.index.commit("Initial commit")
