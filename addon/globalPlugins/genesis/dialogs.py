# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 09/09/2025
"""

import addonHandler
import gui
import wx
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel

from .repo import validate_token
from .varsConfig import (
	get_allow_github_publish,
	get_project_dir,
	get_repo_owner,
	get_repo_private,
	set_allow_github_publish,
	set_project_dir,
	set_repo_owner,
	set_repo_private,
)

# Initialize translation support
addonHandler.initTranslation()


class ProgressDialog(wx.Dialog):
	def __init__(self, parent, title):
		super().__init__(parent, title=title, size=wx.Size(400, 150))

		self.progress = wx.Gauge(self, range=100, style=wx.GA_HORIZONTAL)
		self.status = wx.StaticText(self, label=_("Starting..."))
		self.cancel_button = wx.Button(self, label=_("Cancel"))
		self.cancelled = False

		self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.status, 0, wx.ALL | wx.EXPAND, 10)
		sizer.Add(self.progress, 0, wx.ALL | wx.EXPAND, 10)
		sizer.Add(self.cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 10)

		self.SetSizer(sizer)
		self.Centre()

	def on_cancel(self, event):
		self.cancelled = True


class GitHubAuthentication(wx.Dialog):
	def __init__(self, parent, title):
		super().__init__(parent, title=title)

		panel = wx.Panel(self)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

		gitBox = wx.StaticBox(panel, label=_("GitHub"))
		gitSizer = wx.StaticBoxSizer(gitBox, wx.VERTICAL)

		label_owner = wx.StaticText(panel, label=_("Username or organization:"))
		gitSizer.Add(label_owner, 0, wx.ALL, 5)
		self.git_owner = wx.TextCtrl(panel)
		gitSizer.Add(self.git_owner, 1, wx.EXPAND | wx.ALL, 5)
		self.git_owner.SetValue(get_repo_owner())

		label_token = wx.StaticText(panel, label=_("GitHub Access Token:"))
		gitSizer.Add(label_token, 0, wx.ALL, 5)
		self.git_token = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
		gitSizer.Add(self.git_token, 1, wx.EXPAND | wx.ALL, 5)

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
		owner = self.git_owner.GetValue().strip()
		token = self.git_token.GetValue().strip()

		if not owner:
			gui.messageBox(_("The 'Username or organization name' field cannot be empty!"),
						   _("Error"), wx.OK | wx.ICON_WARNING)
			self.git_owner.SetFocus()
			return

		if len(token) < 20:
			gui.messageBox(_("The access token appears to be invalid or too short!"),
						   _("Error"), wx.OK | wx.ICON_WARNING)
			self.git_token.SetFocus()
			return

		if not validate_token(token):
			gui.messageBox(_("Invalid or unauthorized token."),
						   _("Authentication Error"), wx.OK | wx.ICON_ERROR)
			self.git_token.SetFocus()
			return

		self.owner = owner
		self.token = token
		self.EndModal(wx.ID_OK)

	def onCancel(self, event):
		self.EndModal(wx.ID_CANCEL)


class GenesisSettingsPanel(SettingsPanel):
	title = _("Genesis settings")

	def makeSettings(self, settingsSizer):
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		sizer = wx.BoxSizer(wx.VERTICAL)

		self.allowPublish = wx.CheckBox(
			self, label=_("Allow publishing repository on GitHub")
		)
		self.allowPublish.SetValue(get_allow_github_publish())
		sizer.Add(self.allowPublish, flag=wx.ALL, border=10)

		self.privateRepo = wx.CheckBox(self, label=_("Make repository private"))
		self.privateRepo.SetValue(get_repo_private())
		sizer.Add(self.privateRepo, flag=wx.ALL, border=10)

		ownerBox = wx.BoxSizer(wx.HORIZONTAL)
		ownerLabel = wx.StaticText(self, label=_("Username or organization:"))
		self.ownerField = wx.TextCtrl(self)
		self.ownerField.SetValue(get_repo_owner())
		ownerBox.Add(ownerLabel, flag=wx.ALL, border=10)
		ownerBox.Add(self.ownerField, flag=wx.ALL, border=10)
		sizer.Add(ownerBox)

		# Project directory group
		projectBoxSizer = wx.StaticBoxSizer(
			wx.HORIZONTAL, self, label=_("Default project directory:")
		)
		projectBox = projectBoxSizer.GetStaticBox()
		projectGroup = guiHelper.BoxSizerHelper(self, sizer=projectBoxSizer)

		# Directory selection control
		self.projectPicker = wx.DirPickerCtrl(
			projectBox,
			message=_("Choose where new add-ons will be created"),
		)
		self.projectPicker.SetPath(get_project_dir() or "")

		# Add to group internal layout
		projectGroup.addItem(self.projectPicker, flag=wx.EXPAND)

		# Add to settings panel
		settingsSizerHelper.addItem(projectGroup)

		settingsSizer.Add(sizer)

	def onSave(self):
		set_allow_github_publish(self.allowPublish.Value)
		set_repo_private(self.privateRepo.Value)
		set_repo_owner(self.ownerField.Value)
		set_project_dir(self.projectPicker.GetPath())
