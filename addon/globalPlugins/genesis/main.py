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
import re

import addonHandler
import gui
import wx

from .addonUtils import DEFAULTS, SELECT_MODULE
from .dialogs import GitHubAuthentication, ProgressDialog
from .varsConfig import (
	TEMPLATE_PATH_BUILD_VARS,
	TEMPLATE_PATH_PY_PROJECT,
	getAllowGithubPublish,
	getProjectDir,
	getRepoOwner,
)
from .workerThreads import AddonCreationThread, CloneNVDARepoThread

# Initialize translation support
addonHandler.initTranslation()


def validateAddonName(name: str) -> bool:
	"""
	Validate the add-on name as a Python package and folder identifier.

	Valid characters:
	- Uppercase and lowercase letters.
	- Numbers.
	- Underscores.

	The name cannot start with a number.

	Args:
		name: Add-on name to validate.

	Returns:
		True if the name is valid, False otherwise.
	"""
	if not name:
		return False

	return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name) is not None


def validateNvdaVersion(v: str) -> bool:
	"""
	Validate NVDA versions in the format YYYY.Major or YYYY.Major.Patch.

	Args:
		v: Version string to validate.

	Returns:
		True if the version is valid, False otherwise.
	"""
	if not v:
		return False

	return re.match(r"^\d{4}\.\d+(\.\d+)?$", v) is not None


def isDirWritable(path: str) -> bool:
	"""
	Check whether a directory exists and is writable.

	If the directory does not exist, check whether its parent directory
	exists and is writable.

	Args:
		path: Directory path to check.

	Returns:
		True if the directory or its parent is writable, False otherwise.
	"""
	try:
		if not path:
			return False

		path = os.path.abspath(path)

		if os.path.isdir(path):
			return os.access(path, os.W_OK)

		parent = os.path.dirname(path) or os.path.abspath(".")

		return os.path.isdir(parent) and os.access(parent, os.W_OK)

	except OSError:
		return False


class Genesis(wx.Dialog):
	"""Dialog for creating a new NVDA add-on project."""

	def __init__(self, parent, title):
		super().__init__(
			parent,
			title=title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
		)

		self.creationThread = None

		panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)

		# Destination folder
		folderBox = wx.StaticBox(panel, label=_("Local folder of the Add-on"))
		folderSizer = wx.StaticBoxSizer(folderBox, wx.HORIZONTAL)

		self.folderLabel = wx.StaticText(panel, label=_("Directory path:"))
		self.folderPicker = wx.DirPickerCtrl(
			panel,
			message=_("Select the destination folder"),
		)
		self.folderPicker.SetPath(getProjectDir())

		folderSizer.Add(self.folderLabel, 0, wx.ALL | wx.CENTER, 10)
		folderSizer.Add(self.folderPicker, 1, wx.ALL | wx.EXPAND, 10)
		mainSizer.Add(folderSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Add-on Information
		addonBox = wx.StaticBox(panel, label=_("Add-on information"))
		addonSizer = wx.StaticBoxSizer(addonBox, wx.VERTICAL)

		labelName = wx.StaticText(panel, label=_("Add-on name:"))
		self.textAddonName = wx.TextCtrl(panel)
		addonSizer.Add(labelName, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonName, 1, wx.EXPAND | wx.ALL, 5)

		labelSummary = wx.StaticText(panel, label=_("Summary:"))
		self.textAddonSummary = wx.TextCtrl(panel)
		addonSizer.Add(labelSummary, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonSummary, 1, wx.EXPAND | wx.ALL, 5)

		labelDescription = wx.StaticText(panel, label=_("Description:"))
		self.textAddonDescription = wx.TextCtrl(
			panel,
			style=wx.TE_MULTILINE,
		)
		addonSizer.Add(labelDescription, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonDescription, 1, wx.EXPAND | wx.ALL, 5)

		labelVersion = wx.StaticText(panel, label=_("Version:"))
		self.textAddonVersion = wx.TextCtrl(
			panel,
			value=DEFAULTS["version"],
		)
		addonSizer.Add(labelVersion, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonVersion, 1, wx.EXPAND | wx.ALL, 5)

		labelAuthor = wx.StaticText(panel, label=_("Author:"))
		self.textAddonAuthor = wx.TextCtrl(panel)
		addonSizer.Add(labelAuthor, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonAuthor, 1, wx.EXPAND | wx.ALL, 5)

		labelMinNVDA = wx.StaticText(
			panel,
			label=_("Minimum version of NVDA:"),
		)
		self.textAddonMinimumNVDAVersion = wx.TextCtrl(
			panel,
			value=DEFAULTS["minNVDA"],
		)
		addonSizer.Add(labelMinNVDA, 0, wx.ALL, 5)
		addonSizer.Add(
			self.textAddonMinimumNVDAVersion,
			0,
			wx.EXPAND | wx.ALL,
			5,
		)

		labelLastNVDA = wx.StaticText(
			panel,
			label=_("Last tested NVDA version:"),
		)
		self.textAddonLastTestedNVDAVersion = wx.TextCtrl(
			panel,
			value=DEFAULTS["lastNVDA"],
		)
		addonSizer.Add(labelLastNVDA, 0, wx.ALL, 5)
		addonSizer.Add(
			self.textAddonLastTestedNVDAVersion,
			1,
			wx.EXPAND | wx.ALL,
			5,
		)

		mainSizer.Add(addonSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Module
		moduleBox = wx.StaticBox(panel, label=_("Add-on modules"))
		moduleSizer = wx.StaticBoxSizer(moduleBox, wx.VERTICAL)

		moduleLabel = wx.StaticText(panel, label=_("Module:"))
		self.selectedModule = wx.Choice(
			panel,
			choices=SELECT_MODULE,
		)
		self.selectedModule.SetSelection(0)

		moduleSizer.Add(moduleLabel, 0, wx.ALL, 5)
		moduleSizer.Add(
			self.selectedModule,
			1,
			wx.ALL | wx.EXPAND,
			5,
		)

		mainSizer.Add(moduleSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Optional folders
		checkboxBox = wx.StaticBox(
			panel,
			label=_("Add-on location"),
		)
		checkboxSizer = wx.StaticBoxSizer(
			checkboxBox,
			wx.VERTICAL,
		)

		self.checkAddonDoc = wx.CheckBox(
			panel,
			label=_("Include doc"),
		)
		self.checkAddonLocale = wx.CheckBox(
			panel,
			label=_("Include locale"),
		)

		checkboxSizer.Add(self.checkAddonDoc, 0, wx.ALL, 5)
		checkboxSizer.Add(self.checkAddonLocale, 0, wx.ALL, 5)

		mainSizer.Add(checkboxSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Buttons
		actionBox = wx.StaticBox(panel, label=_("Actions"))
		actionSizer = wx.StaticBoxSizer(
			actionBox,
			wx.HORIZONTAL,
		)

		generateButton = wx.Button(
			panel,
			label=_("&Generate"),
		)
		generateButton.Bind(wx.EVT_BUTTON, self.onGenerate)

		cleanButton = wx.Button(
			panel,
			label=_("C&lean"),
		)
		cleanButton.Bind(wx.EVT_BUTTON, self.onClean)

		cloneButton = wx.Button(
			panel,
			label=_("Clone the official &NVDA repository."),
		)
		cloneButton.Bind(
			wx.EVT_BUTTON,
			self.onCloneRepository,
		)

		cancelButton = wx.Button(
			panel,
			wx.ID_CANCEL,
			label=_("&Cancel"),
		)
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

		actionSizer.Add(generateButton, 0, wx.ALL, 5)
		actionSizer.Add(cleanButton, 0, wx.ALL, 5)
		actionSizer.Add(cloneButton, 0, wx.ALL, 5)
		actionSizer.Add(cancelButton, 0, wx.ALL, 5)

		mainSizer.Add(
			actionSizer,
			0,
			wx.ALIGN_CENTER_HORIZONTAL | wx.ALL,
			10,
		)

		panel.SetSizerAndFit(mainSizer)
		self.Fit()
		self.folderPicker.SetFocus()

	# Focus helper
	def focusOnEmptyField(self, field):
		fields = {
			"name": self.textAddonName,
			"summary": self.textAddonSummary,
			"description": self.textAddonDescription,
			"author": self.textAddonAuthor,
			"version": self.textAddonVersion,
			"minimumNVDAVersion": self.textAddonMinimumNVDAVersion,
			"lastTestedNVDAVersion": self.textAddonLastTestedNVDAVersion,
		}

		control = fields.get(field)

		if control:
			control.SetFocus()

	# GENERATE
	def onGenerate(self, event):
		# Prevent starting another creation while the previous one is running.
		if self.creationThread and self.creationThread.is_alive():
			self.showMessage(
				_("An add-on creation is already in progress."),
				_("Warning"),
				wx.OK | wx.ICON_WARNING,
			)
			return

		self.destinationFolder = self.folderPicker.GetPath().strip()
		self.newFolderName = self.textAddonName.GetValue().strip()
		self.desc = self.textAddonDescription.GetValue().strip()

		# 1 - Validate destination folder
		if not self.destinationFolder:
			self.showMessage(
				_("Directory path cannot be empty."),
				_("Missing information"),
			)
			self.folderPicker.SetFocus()
			return

		if not isDirWritable(self.destinationFolder):
			self.showMessage(
				_(
					"The selected directory is not writable. Please choose another directory.",
				),
				_("Error"),
				wx.OK | wx.ICON_ERROR,
			)
			self.folderPicker.SetFocus()
			return

		# 2 - Validate required fields
		requiredFields = {
			"name": (
				self.newFolderName,
				_("Addon name"),
			),
			"summary": (
				self.textAddonSummary.GetValue().strip(),
				_("Addon summary"),
			),
			"description": (
				self.desc,
				_("Addon description"),
			),
			"author": (
				self.textAddonAuthor.GetValue().strip(),
				_("Author"),
			),
			"version": (
				self.textAddonVersion.GetValue().strip(),
				_("Version"),
			),
			"minimumNVDAVersion": (
				self.textAddonMinimumNVDAVersion.GetValue().strip(),
				_("Minimum NVDA Version"),
			),
			"lastTestedNVDAVersion": (
				self.textAddonLastTestedNVDAVersion.GetValue().strip(),
				_("Last Tested NVDA Version"),
			),
		}

		for key, (value, label) in requiredFields.items():
			if not value:
				self.showMessage(
					_("The field '{}' cannot be empty.").format(label),
					_("Missing information"),
					wx.OK | wx.ICON_WARNING,
				)
				self.focusOnEmptyField(key)
				return

		# 3 - Validate add-on name
		if not validateAddonName(self.newFolderName):
			self.showMessage(
				_(
					"Invalid add-on name. Use only uppercase or lowercase "
					+ "letters, numbers and underscores, and do not start "
					+ "with a number.",
				),
				_("Invalid name"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textAddonName.SetFocus()
			return

		# 4 - Validate NVDA versions
		minVersion = self.textAddonMinimumNVDAVersion.GetValue().strip()
		lastVersion = self.textAddonLastTestedNVDAVersion.GetValue().strip()

		if not validateNvdaVersion(minVersion):
			self.showMessage(
				_(
					"Minimum NVDA version is invalid. Expected format: "
					+ "YYYY.Major or YYYY.Major.Patch "
					+ "(e.g. 2023.3 or 2023.3.2)",
				),
				_("Invalid version"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textAddonMinimumNVDAVersion.SetFocus()
			return

		if not validateNvdaVersion(lastVersion):
			self.showMessage(
				_(
					"Last tested NVDA version is invalid. Expected format: "
					+ "YYYY.Major or YYYY.Major.Patch "
					+ "(e.g. 2023.3 or 2023.3.2)",
				),
				_("Invalid version"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textAddonLastTestedNVDAVersion.SetFocus()
			return

		# 5 - GitHub authentication
		token = ""
		owner = ""

		if getAllowGithubPublish():
			auth = GitHubAuthentication(
				self,
				_("GitHub Authentication"),
			)

			try:
				authResult = auth.ShowModal()

				if authResult == wx.ID_OK:
					token = auth.token
					owner = auth.owner

			finally:
				auth.Destroy()

			if not token or not owner:
				self.showMessage(
					_("Authentication was canceled or failed."),
					_("Error"),
				)
				return

			if not re.match(r"^[A-Za-z0-9_.-]+$", owner):
				self.showMessage(
					_("Owner contains invalid characters."),
					_("Invalid owner"),
					wx.OK | wx.ICON_WARNING,
				)
				return

		# 6 - Prepare creation
		self.baseFolder = os.path.join(
			self.destinationFolder,
			self.newFolderName,
		)

		# Use the authenticated owner when publishing.
		# Otherwise, use the owner stored in the add-on configuration.
		repoOwner = owner or (getRepoOwner() or "").strip()

		templateVariables = {
			"name": self.newFolderName,
			"summary": self.textAddonSummary.GetValue().strip(),
			"description": self.desc,
			"author": self.textAddonAuthor.GetValue().strip(),
			"version": self.textAddonVersion.GetValue().strip(),
			"minimumNVDAVersion": minVersion,
			"lastTestedNVDAVersion": lastVersion,
			"module": self.selectedModule.GetStringSelection(),
			"repoOwner": repoOwner,
			"doc": self.checkAddonDoc.GetValue(),
			"locale": self.checkAddonLocale.GetValue(),
		}

		# translators: Status message shown in the progress dialog when the add-on is being created.
		self.progressDialog = ProgressDialog(
			self,
			_("Creating Add-on"),
		)
		self.progressDialog.Show()

		self.creationThread = AddonCreationThread(
			self,
			self.baseFolder,
			self.newFolderName,
			self.desc,
			owner,
			token,
			getAllowGithubPublish(),
			TEMPLATE_PATH_BUILD_VARS,
			TEMPLATE_PATH_PY_PROJECT,
			templateVariables,
		)

		self.creationThread.start()

	# CLEAN
	def onClean(self, event):
		for ctrl in (
			self.textAddonName,
			self.textAddonSummary,
			self.textAddonDescription,
			self.textAddonAuthor,
			self.textAddonVersion,
			self.textAddonMinimumNVDAVersion,
			self.textAddonLastTestedNVDAVersion,
		):
			ctrl.Clear()

		self.checkAddonDoc.SetValue(False)
		self.checkAddonLocale.SetValue(False)

		self.textAddonVersion.SetValue(DEFAULTS["version"])
		self.textAddonMinimumNVDAVersion.SetValue(DEFAULTS["minNVDA"])
		self.textAddonLastTestedNVDAVersion.SetValue(DEFAULTS["lastNVDA"])

		self.textAddonName.SetFocus()

	# CLONE NVDA REPOSITORY
	def onCloneRepository(self, event):
		with wx.DirDialog(
			self,
			message=_("Choose the folder where the NVDA repository will be cloned:"),
			style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				gui.messageBox(
					_("Clone canceled by the user."),
					_("Info"),
					wx.OK | wx.ICON_INFORMATION,
				)
				return

			dest = dialog.GetPath()

			progress = ProgressDialog(
				self,
				_("Cloning NVDA Repository"),
			)
			progress.Show()

			thread = CloneNVDARepoThread(
				self,
				"https://github.com/nvaccess/nvda",
				dest,
				progress,
			)
			thread.start()

	# CANCEL
	def onCancel(self, event):
		if self.creationThread and self.creationThread.is_alive():
			self.showMessage(
				_("Please wait for the add-on creation to finish before closing."),
				_("Warning"),
			)
			return

		self.Destroy()

	# Utility
	def showMessage(
		self,
		message,
		caption=None,
		style=wx.OK | wx.ICON_INFORMATION,
	):
		if caption is None:
			caption = _("Message")

		dlg = wx.MessageDialog(
			self,
			message,
			caption,
			style,
		)
		dlg.ShowModal()
		dlg.Destroy()
