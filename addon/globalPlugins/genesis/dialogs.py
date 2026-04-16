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
	def __init__(self, parent, title):
		super().__init__(parent, title=title)

		panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

		# translators: Label for the GitHub section in the authentication dialog.
		gitBox = wx.StaticBox(panel, label=_("GitHub"))
		gitSizer = wx.StaticBoxSizer(gitBox, wx.VERTICAL)

		# translators: Label for the GitHub username or organization field.
		labelOwner = wx.StaticText(panel, label=_("Username or organization:"))
		gitSizer.Add(labelOwner, 0, wx.ALL, 5)
		self.textGitOwner = wx.TextCtrl(panel)
		gitSizer.Add(self.textGitOwner, 1, wx.EXPAND | wx.ALL, 5)
		self.textGitOwner.SetValue(getRepoOwner())

		# translators: Label for the GitHub access token field.
		labelToken = wx.StaticText(panel, label=_("GitHub Access Token:"))
		gitSizer.Add(labelToken, 0, wx.ALL, 5)
		self.textGitToken = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
		gitSizer.Add(self.textGitToken, 1, wx.EXPAND | wx.ALL, 5)

		mainSizer.Add(gitSizer, 0, wx.EXPAND | wx.ALL, 10)

		self.buttonOk = wx.Button(panel, wx.ID_OK, label=_("&Ok"))
		self.buttonOk.Bind(wx.EVT_BUTTON, self.onOK)

		self.buttonCancel = wx.Button(panel, wx.ID_CANCEL, label=_("&Cancel"))
		self.buttonCancel.Bind(wx.EVT_BUTTON, self.onCancel)

		buttonSizer.Add(self.buttonOk, 0, wx.ALL, 5)
		buttonSizer.Add(self.buttonCancel, 0, wx.ALL, 5)

		mainSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER)
		panel.SetSizer(mainSizer)
		self.Fit()

	def onOK(self, event):
		owner = self.textGitOwner.GetValue().strip()
		token = self.textGitToken.GetValue().strip()

		if not owner:
			gui.messageBox(
				# translators: Error message shown when the GitHub username or organization field is empty.
				_("The 'Username or organization name' field cannot be empty!"),
				_("Error"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textGitOwner.SetFocus()
			return

		if len(token) < 20:
			gui.messageBox(
				# translators: Error message shown when the GitHub access token field is invalid.
				_("The access token appears to be invalid or too short!"),
				_("Error"),
				wx.OK | wx.ICON_WARNING,
			)
			self.textGitToken.SetFocus()
			return

		if not validateToken(token):
			gui.messageBox(
				# translators: Error message shown when the GitHub access token is invalid or unauthorized.
				_("Invalid or unauthorized token."),
				_("Authentication Error"),
				wx.OK | wx.ICON_ERROR,
			)
			self.textGitToken.SetFocus()
			return

		self.owner = owner
		self.token = token
		self.EndModal(wx.ID_OK)

	def onCancel(self, event):
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
