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
from .varsConfig import TEMPLATE_PATH, getAllowGithubPublish, getProjectDir
from .workerThreads import AddonCreationThread, CloneNVDARepoThread

# Initialize translation support
addonHandler.initTranslation()


def validateAddonName(name: str) -> bool:
	"""
	Validates the addon name to be a package/folder identifier:
	- letters (upper and lower case)
	- can contain numbers and underscores
	- do not start with a number
	- no spaces or special characters

		Valid examples:
		addonName
		myAddon
		Addon1
		my_addon
	"""

	if not name:
		return False

	# Allow letters (A-Z, a-z), numbers and underscore,
	# but don't start with number
	return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name) is not None


def validateNvdaVersion(v: str) -> bool:
	"""
	Validates versions of the type: 2023.3 or 2023.3.2 (year.minor[.patch])
	"""
	if not v:
		return False
	return re.match(r"^\d{4}\.\d+(\.\d+)?$", v) is not None


def isDirWritable(path: str) -> bool:
	"""
	Checks if `path` exists and is writable, or if its parent is writable (allows you to create the folder).
	"""
	try:
		if not path:
			return False
		path = os.path.abspath(path)
		# if it already exists and is a directory, we test write permission
		if os.path.isdir(path):
			return os.access(path, os.W_OK)
		# if it doesn't exist, we check if the parent is writable
		parent = os.path.dirname(path) or os.path.abspath(".")
		return os.path.isdir(parent) and os.access(parent, os.W_OK)
	except Exception:
		return False


class Genesis(wx.Dialog):
	"""Dialog for creating a new NVDA add-on project."""

	def __init__(self, parent, title):
		super(Genesis, self).__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

		self.creationThread = None

		panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)

		# Destination folder
		folderBox = wx.StaticBox(panel, label=_("Local folder of the Add-on"))
		folderSizer = wx.StaticBoxSizer(folderBox, wx.HORIZONTAL)

		self.folderLabel = wx.StaticText(panel, label=_("Directory path:"))
		self.folderPicker = wx.DirPickerCtrl(panel, message=_("Select the destination folder"))
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
		self.textAddonDescription = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
		addonSizer.Add(labelDescription, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonDescription, 1, wx.EXPAND | wx.ALL, 5)

		labelVersion = wx.StaticText(panel, label=_("Version:"))
		self.textAddonVersion = wx.TextCtrl(panel, value=DEFAULTS["version"])
		addonSizer.Add(labelVersion, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonVersion, 1, wx.EXPAND | wx.ALL, 5)

		labelAuthor = wx.StaticText(panel, label=_("Author:"))
		self.textAddonAuthor = wx.TextCtrl(panel)
		addonSizer.Add(labelAuthor, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonAuthor, 1, wx.EXPAND | wx.ALL, 5)

		labelMinNVDA = wx.StaticText(panel, label=_("Minimum version of NVDA:"))
		self.textAddonMinimumNVDAVersion = wx.TextCtrl(panel, value=DEFAULTS["minNVDA"])
		addonSizer.Add(labelMinNVDA, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonMinimumNVDAVersion, 0, wx.EXPAND | wx.ALL, 5)

		labelLastNVDA = wx.StaticText(panel, label=_("Last tested NVDA version:"))
		self.textAddonLastTestedNVDAVersion = wx.TextCtrl(panel, value=DEFAULTS["lastNVDA"])
		addonSizer.Add(labelLastNVDA, 0, wx.ALL, 5)
		addonSizer.Add(self.textAddonLastTestedNVDAVersion, 1, wx.EXPAND | wx.ALL, 5)

		mainSizer.Add(addonSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Module
		moduleBox = wx.StaticBox(panel, label=_("Add-on modules"))
		moduleSizer = wx.StaticBoxSizer(moduleBox, wx.VERTICAL)

		moduleLabel = wx.StaticText(panel, label=_("Module:"))
		self.selectedModule = wx.Choice(panel, choices=SELECT_MODULE)
		self.selectedModule.SetSelection(0)

		moduleSizer.Add(moduleLabel, 0, wx.ALL, 5)
		moduleSizer.Add(self.selectedModule, 1, wx.ALL | wx.EXPAND, 5)

		mainSizer.Add(moduleSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Optional folders
		checkboxBox = wx.StaticBox(panel, label=_("Add-on location"))
		checkboxSizer = wx.StaticBoxSizer(checkboxBox, wx.VERTICAL)

		self.checkAddonDoc = wx.CheckBox(panel, label=_("Include doc"))
		self.checkAddonLocale = wx.CheckBox(panel, label=_("Include locale"))

		checkboxSizer.Add(self.checkAddonDoc, 0, wx.ALL, 5)
		checkboxSizer.Add(self.checkAddonLocale, 0, wx.ALL, 5)

		mainSizer.Add(checkboxSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Buttons
		actionBox = wx.StaticBox(panel, label=_("Actions"))
		actionSizer = wx.StaticBoxSizer(actionBox, wx.HORIZONTAL)

		generateButton = wx.Button(panel, label=_("&Generate"))
		generateButton.Bind(wx.EVT_BUTTON, self.onGenerate)

		cleanBbutton = wx.Button(panel, label=_("C&lean"))
		cleanBbutton.Bind(wx.EVT_BUTTON, self.onClean)

		cloneButton = wx.Button(panel, label=_("Clone the official &NVDA repository."))
		cloneButton.Bind(wx.EVT_BUTTON, self.onCloneRepository)

		cancelButton = wx.Button(panel, wx.ID_CANCEL, label=_("&Cancel"))
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancel)

		actionSizer.Add(generateButton, 0, wx.ALL, 5)
		actionSizer.Add(cleanBbutton, 0, wx.ALL, 5)
		actionSizer.Add(cloneButton, 0, wx.ALL, 5)
		actionSizer.Add(cancelButton, 0, wx.ALL, 5)

		mainSizer.Add(actionSizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

		panel.SetSizerAndFit(mainSizer)
		self.Fit()
		self.folderPicker.SetFocus()

	# Focus helper
	def focusOnEmptyField(self, field):
		if field == "name":
			self.textAddonName.SetFocus()
		elif field == "summary":
			self.textAddonSummary.SetFocus()
		elif field == "description":
			self.textAddonDescription.SetFocus()
		elif field == "author":
			self.textAddonAuthor.SetFocus()
		elif field == "version":
			self.textAddonVersion.SetFocus()
		elif field == "minimumNVDAVersion":
			self.textAddonMinimumNVDAVersion.SetFocus()
		elif field == "lastTestedNVDAVersion":
			self.textAddonLastTestedNVDAVersion.SetFocus()

	# GENERATE
	def onGenerate(self, event):
		self.destinationFolder = self.folderPicker.GetPath()
		self.newFolderName = self.textAddonName.GetValue().strip()
		self.desc = self.textAddonDescription.GetValue().strip()

		# 1 - Checa se pasta destino preenchida e gravável
		if not self.destinationFolder:
			self.showMessage(_("Directory path cannot be empty."), _("Missing information"))
			self.folderPicker.SetFocus()
			return

		if not isDirWritable(self.destinationFolder):
			self.showMessage(
				_("The selected directory is not writable. Please choose another directory."),
				_("Error"),
				wx.OK | wx.ICON_ERROR,
			)
			self.folderPicker.SetFocus()
			return

		# 2 - Required fields (with focus on empty field)
		requiredFields = {
			"name": (self.textAddonName.GetValue().strip(), _("Addon name")),
			"summary": (self.textAddonSummary.GetValue().strip(), _("Addon summary")),
			"description": (self.textAddonDescription.GetValue().strip(), _("Addon description")),
			"author": (self.textAddonAuthor.GetValue().strip(), _("Author")),
			"version": (self.textAddonVersion.GetValue().strip(), _("Version")),
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

		# 3 - Validate addon name
		if not validateAddonName(self.newFolderName):
			self.showMessage(
				_(
					"Invalid add-on name. Use only lowercase letters, numbers and underscore, and do not start with a number.",
				),
				_("Invalid name"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textAddonName.SetFocus()
			return

		# 4 - Validates NVDA versions
		minVersion = self.textAddonMinimumNVDAVersion.GetValue().strip()
		lastVersion = self.textAddonLastTestedNVDAVersion.GetValue().strip()
		if not validateNvdaVersion(minVersion):
			self.showMessage(
				_(
					"Minimum NVDA version is invalid. Expected format: YYYY.Major or YYYY.Major.Patch (e.g. 2023.3 or 2023.3.2)",
				),
				_("Invalid version"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textAddonMinimumNVDAVersion.SetFocus()
			return
		if not validateNvdaVersion(lastVersion):
			self.showMessage(
				_(
					"Last tested NVDA version is invalid. Expected format: YYYY.Major or YYYY.Major.Patch (e.g. 2023.3 or 2023.3.2)",
				),
				_("Invalid version"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textAddonLastTestedNVDAVersion.SetFocus()
			return

		# 5 - GitHub authentication (if enabled)
		token = owner = ""
		if getAllowGithubPublish():
			auth = GitHubAuthentication(self, _("GitHub Authentication"))
			if auth.ShowModal() != wx.ID_OK:
				self.showMessage(_("Authentication was canceled or failed."), _("Error"))
				return
			token = auth.token
			owner = auth.owner
			# Valida owner simples (caracteres permitidos)
			if not re.match(r"^[A-Za-z0-9_.-]+$", owner):
				self.showMessage(
					_("Owner contains invalid characters."),
					_("Invalid owner"),
					wx.OK | wx.ICON_WARNING,
				)
				return

		# 6 - Prepare creation
		self.baseFolder = os.path.join(self.destinationFolder, self.newFolderName)

		# translators: Status message shown in the progress dialog when the add-on is being created.
		self.progressDialog = ProgressDialog(self, _("Creating Addon"))
		self.progressDialog.Show()

		vars = {
			"name": self.textAddonName.GetValue(),
			"summary": self.textAddonSummary.GetValue(),
			"description": self.textAddonDescription.GetValue(),
			"author": self.textAddonAuthor.GetValue(),
			"version": self.textAddonVersion.GetValue(),
			"minimumNVDAVersion": self.textAddonMinimumNVDAVersion.GetValue(),
			"lastTestedNVDAVersion": self.textAddonLastTestedNVDAVersion.GetValue(),
			"module": self.selectedModule.GetStringSelection(),
		}

		self.creationThread = AddonCreationThread(
			self,
			self.baseFolder,
			self.newFolderName,
			self.desc,
			owner,
			token,
			getAllowGithubPublish(),
			TEMPLATE_PATH,
			vars,
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
				gui.messageBox(_("Clone canceled by the user."), _("Info"), wx.OK | wx.ICON_INFORMATION)
				return

			dest = dialog.GetPath()

			progress = ProgressDialog(self, _("Cloning NVDA Repository"))
			progress.Show()

			thread = CloneNVDARepoThread(self, "https://github.com/nvaccess/nvda", dest, progress)
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

	def showMessage(self, message, caption=None, style=wx.OK | wx.ICON_INFORMATION):
		if caption is None:
			caption = _("Message")

		dlg = wx.MessageDialog(self, message, caption, style)
		dlg.ShowModal()
		dlg.Destroy()
