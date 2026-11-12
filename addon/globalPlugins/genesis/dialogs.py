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

Created on: 09/09/2025
"""

import addonHandler
import gui
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel
from logHandler import log

from .credentialManager import (
	deleteGithubToken,
	getGithubToken,
	saveGithubToken,
)
from .repo import validateToken
from .varsConfig import (
	getAllowGithubPublish,
	getProjectDir,
	getRepoOwner,
	getRepoPrivate,
	setAllowGithubPublish,
	setProjectDir,
	setRepoOwner,
	setRepoPrivate,
)

# Initialize translation support
addonHandler.initTranslation()


class ProgressDialog(wx.Dialog):
	def __init__(self, parent, title):
		super().__init__(parent, title=title, size=wx.Size(400, 150))

		self.progress = wx.Gauge(self, range=100, style=wx.GA_HORIZONTAL)
		# translators: Initial status message shown in the progress dialog when an operation starts.
		self.status = wx.StaticText(self, label=_("Starting..."))
		self.buttonCancel = wx.Button(self, label=_("Cancel"))
		self.cancelled = False

		self.buttonCancel.Bind(wx.EVT_BUTTON, self.onCancel)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.status, 0, wx.ALL | wx.EXPAND, 10)
		sizer.Add(self.progress, 0, wx.ALL | wx.EXPAND, 10)
		sizer.Add(self.buttonCancel, 0, wx.ALL | wx.ALIGN_CENTER, 10)

		self.SetSizer(sizer)
		self.Centre()

	def onCancel(self, event):
		self.cancelled = True


class GitHubAuthentication(wx.Dialog):
	"""
	Dialog for managing the GitHub access token.

	The token is stored in the Windows Credential Manager.
	"""

	def __init__(self, parent, title):
		super().__init__(parent, title=title)

		self.tokenExists = False

		panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

		gitBox = wx.StaticBox(
			panel,
			label=_("GitHub authentication"),
		)
		gitSizer = wx.StaticBoxSizer(gitBox, wx.VERTICAL)

		self.statusLabel = wx.StaticText(panel, label="")
		gitSizer.Add(
			self.statusLabel,
			0,
			wx.EXPAND | wx.ALL,
			5,
		)

		labelToken = wx.StaticText(
			panel,
			label=_("GitHub access token:"),
		)
		gitSizer.Add(
			labelToken,
			0,
			wx.ALL,
			5,
		)

		self.textGitToken = wx.TextCtrl(
			panel,
			style=wx.TE_PASSWORD,
		)
		gitSizer.Add(
			self.textGitToken,
			0,
			wx.EXPAND | wx.ALL,
			5,
		)

		mainSizer.Add(
			gitSizer,
			0,
			wx.EXPAND | wx.ALL,
			10,
		)

		self.buttonSave = wx.Button(
			panel,
			wx.ID_OK,
			label=_("&Save token"),
		)
		self.buttonSave.Bind(wx.EVT_BUTTON, self.onSave)

		self.buttonRemove = wx.Button(
			panel,
			wx.ID_ANY,
			label=_("&Remove token"),
		)
		self.buttonRemove.Bind(wx.EVT_BUTTON, self.onRemove)

		self.buttonCancel = wx.Button(
			panel,
			wx.ID_CANCEL,
			label=_("&Cancel"),
		)
		self.buttonCancel.Bind(wx.EVT_BUTTON, self.onCancel)

		buttonSizer.Add(self.buttonSave, 0, wx.ALL, 5)
		buttonSizer.Add(self.buttonRemove, 0, wx.ALL, 5)
		buttonSizer.Add(self.buttonCancel, 0, wx.ALL, 5)

		mainSizer.Add(
			buttonSizer,
			0,
			wx.ALIGN_CENTER | wx.ALL,
			5,
		)

		panel.SetSizer(mainSizer)

		self.checkCredential()
		self.Fit()
		self.CentreOnParent()

	def checkCredential(self):
		"""
		Check whether a GitHub token is stored.

		The token itself is never displayed or loaded into the text field.
		"""

		try:
			token = getGithubToken()
			self.tokenExists = token is not None

			if self.tokenExists:
				self.statusLabel.SetLabel(
					_("A GitHub access token is already stored."),
				)
			else:
				self.statusLabel.SetLabel(
					_("No GitHub access token is currently stored."),
				)

		except Exception:
			self.tokenExists = False

			self.statusLabel.SetLabel(
				_("Unable to access the stored GitHub credential."),
			)

			log.exception(
				"Failed to check the GitHub credential.",
			)

		self.buttonRemove.Enable(self.tokenExists)

	def onSave(self, event):
		"""
		Validate and save the GitHub access token.
		"""

		token = self.textGitToken.GetValue().strip()

		if not token:
			gui.messageBox(
				_("Please enter a GitHub access token."),
				_("Missing information"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textGitToken.SetFocus()
			return

		if not validateToken(token):
			gui.messageBox(
				_(
					"The GitHub access token is invalid or could not "
					+ "be validated. Please check your token and try again.",
				),
				_("Authentication error"),
				wx.OK | wx.ICON_ERROR,
			)
			self.textGitToken.SetFocus()
			return

		try:
			saveGithubToken(token)

		except Exception:
			log.exception(
				"Failed to save the GitHub access token.",
			)

			gui.messageBox(
				_(
					"Failed to save the GitHub access token " + "in Windows Credential Manager.",
				),
				_("Error"),
				wx.OK | wx.ICON_ERROR,
			)
			return

		self.tokenExists = True
		self.EndModal(wx.ID_OK)

	def onRemove(self, event):
		"""
		Remove the stored GitHub access token after confirmation.
		"""

		if not self.tokenExists:
			return

		result = gui.messageBox(
			_(
				"Are you sure you want to remove the stored GitHub access token?",
			),
			_("Confirm removal"),
			wx.YES_NO | wx.ICON_WARNING,
		)

		if result != wx.YES:
			return

		try:
			deleteGithubToken()

		except Exception:
			log.exception(
				"Failed to remove the GitHub access token.",
			)

			gui.messageBox(
				_(
					"Failed to remove the GitHub access token " + "from Windows Credential Manager.",
				),
				_("Error"),
				wx.OK | wx.ICON_ERROR,
			)
			return

		self.tokenExists = False

		gui.messageBox(
			_("The GitHub access token was successfully removed."),
			_("Success"),
			wx.OK | wx.ICON_INFORMATION,
		)

		self.EndModal(wx.ID_CANCEL)

	def onCancel(self, event):
		"""
		Close the dialog without changing the stored credential.
		"""

		self.EndModal(wx.ID_CANCEL)


class GenesisSettingsPanel(SettingsPanel):
	# translators: Title of the settings panel for the Genesis add-on, shown in NVDA settings dialog.
	title = _("Genesis settings")

	def makeSettings(self, sizer: wx.BoxSizer):
		settingsSizer = sizer  # Helper to keep the code cleaner and more organized
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		sizer = wx.BoxSizer(wx.VERTICAL)

		# Allow publishing repo on GitHub
		self.allowPublish = wx.CheckBox(
			self,
			# translators: Label for the checkbox that allows publishing the repository on GitHub.
			label=_("Allow publishing repository on GitHub"),
		)
		self.allowPublish.SetValue(getAllowGithubPublish())
		sizer.Add(self.allowPublish, flag=wx.ALL, border=10)

		# translators: Label for the checkbox that makes the repository private.
		self.privateRepo = wx.CheckBox(self, label=_("Make repository private"))
		self.privateRepo.SetValue(getRepoPrivate())
		sizer.Add(self.privateRepo, flag=wx.ALL, border=10)

		# Owner name
		ownerBox = wx.BoxSizer(wx.HORIZONTAL)
		# translators: Label for the GitHub username or organization field.
		ownerLabel = wx.StaticText(self, label=_("Username or organization:"))
		self.ownerField = wx.TextCtrl(self)
		self.ownerField.SetValue(getRepoOwner())
		ownerBox.Add(ownerLabel, flag=wx.ALL, border=10)
		ownerBox.Add(self.ownerField, flag=wx.ALL, border=10)
		sizer.Add(ownerBox)

		# Default project directory
		projectBoxSizer = wx.StaticBoxSizer(
			wx.HORIZONTAL,
			self,
			# translators: Label for the default project directory field.
			label=_("Default project directory:"),
		)
		projectBox = projectBoxSizer.GetStaticBox()
		projectGroup = guiHelper.BoxSizerHelper(self, sizer=projectBoxSizer)

		self.projectPicker = wx.DirPickerCtrl(
			projectBox,
			# translators: Label for the default project directory field.
			message=_("Choose where new add-ons will be created"),
		)
		self.projectPicker.SetPath(getProjectDir() or "")
		projectGroup.addItem(self.projectPicker, flag=wx.EXPAND)

		settingsSizerHelper.addItem(projectGroup)
		settingsSizer.Add(sizer)

	def onSave(self):
		setAllowGithubPublish(self.allowPublish.GetValue())
		setRepoPrivate(self.privateRepo.GetValue())
		setRepoOwner(self.ownerField.GetValue())
		setProjectDir(self.projectPicker.GetPath())
