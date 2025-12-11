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
import sys

import addonHandler
import gui
import wx

from .addonUtils import DEFAULTS, SELECT_MODULE
from .dialogs import GitHubAuthentication, ProgressDialog
from .varsConfig import TEMPLATE_PATH, addonPath, get_allow_github_publish, get_project_dir
from .workerThreads import AddonCreationThread, CloneNVDARepoThread

# Add the lib/ folder to sys.path (only once)
libPath = os.path.join(addonPath, "lib")
if libPath not in sys.path:
	sys.path.insert(0, libPath)

# Initialize translation support
addonHandler.initTranslation()


class Genesis(wx.Dialog):
	"""Dialog for creating a new NVDA add-on project."""

	def __init__(self, parent, title):
		if hasattr(self, "initialized"):
			return
		self.initialized = True
		self.creation_thread = None

		super(Genesis, self).__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

		# Main sizer
		panel = wx.Panel(self)
		main_sizer = wx.BoxSizer(wx.VERTICAL)

		# Destination folder
		folderBox = wx.StaticBox(panel, label=_("Local folder of the Add-on"))
		folderSizer = wx.StaticBoxSizer(folderBox, wx.HORIZONTAL)

		self.folder_label = wx.StaticText(panel, label=_("Directory path:"))
		self.folder_picker = wx.DirPickerCtrl(panel, message=_("Select the destination folder"))
		folderSizer.Add(self.folder_label, 0, wx.ALL | wx.CENTER, 10)
		folderSizer.Add(self.folder_picker, 1, wx.ALL | wx.EXPAND, 10)
		main_sizer.Add(folderSizer, 0, wx.EXPAND | wx.ALL, 10)
		self.folder_picker.SetPath(get_project_dir())

		# Text fields
		addonBox = wx.StaticBox(panel, label=_("Add-on information"))
		addonSizer = wx.StaticBoxSizer(addonBox, wx.VERTICAL)

		label_name = wx.StaticText(panel, label=_("Add-on name:"))
		addonSizer.Add(label_name, 0, wx.ALL, 5)
		self.addon_name = wx.TextCtrl(panel)
		addonSizer.Add(self.addon_name, 1, wx.EXPAND | wx.ALL, 5)

		label_summary = wx.StaticText(panel, label=_("Summary:"))
		addonSizer.Add(label_summary, 0, wx.ALL, 5)
		self.addon_summary = wx.TextCtrl(panel)
		addonSizer.Add(self.addon_summary, 1, wx.EXPAND | wx.ALL, 5)

		label_description = wx.StaticText(panel, label=_("Description:"))
		addonSizer.Add(label_description, 0, wx.ALL, 5)
		self.addon_description = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
		addonSizer.Add(self.addon_description, 1, wx.EXPAND | wx.ALL, 5)

		label_version = wx.StaticText(panel, label=_("Version:"))
		addonSizer.Add(label_version, 0, wx.ALL, 5)
		self.addon_version = wx.TextCtrl(panel, value=DEFAULTS["version"])
		addonSizer.Add(self.addon_version, 1, wx.EXPAND | wx.ALL, 5)

		label_author = wx.StaticText(panel, label=_("Author:"))
		addonSizer.Add(label_author, 0, wx.ALL, 5)
		self.addon_author = wx.TextCtrl(panel)
		addonSizer.Add(self.addon_author, 1, wx.EXPAND | wx.ALL, 5)

		label_minimumNVDAVersion = wx.StaticText(panel, label=_("Minimum version of NVDA:"))
		addonSizer.Add(label_minimumNVDAVersion, 0, wx.ALL, 5)
		self.addon_minimumNVDAVersion = wx.TextCtrl(panel, value=DEFAULTS["minNVDA"])
		addonSizer.Add(self.addon_minimumNVDAVersion, 0, wx.EXPAND | wx.ALL, 5)

		label_lastTestedNVDAVersion = wx.StaticText(panel, label=_("Last tested NVDA version:"))
		addonSizer.Add(label_lastTestedNVDAVersion, 0, wx.ALL, 5)
		self.addon_lastTestedNVDAVersion = wx.TextCtrl(panel, value=DEFAULTS["lastNVDA"])
		addonSizer.Add(self.addon_lastTestedNVDAVersion, 1, wx.EXPAND | wx.ALL, 5)
		main_sizer.Add(addonSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Module
		moduleBox = wx.StaticBox(panel, label=_("Add-on modules"))
		moduleSizer = wx.StaticBoxSizer(moduleBox, wx.VERTICAL)

		module_label = wx.StaticText(panel, label=_("Module:"))
		self.selected_module = wx.Choice(panel, choices=SELECT_MODULE)
		self.selected_module.SetSelection(0)
		moduleSizer.Add(module_label, 0, wx.ALL, 5)
		moduleSizer.Add(self.selected_module, 1, wx.ALL | wx.EXPAND, 5)
		main_sizer.Add(moduleSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Location
		checkboxBox = wx.StaticBox(panel, label=_("Add-on location"))
		checkboxSizer = wx.StaticBoxSizer(checkboxBox, wx.VERTICAL)

		self.addon_doc = wx.CheckBox(panel, label=_("Include doc"))
		self.addon_locale = wx.CheckBox(panel, label=_("Include locale"))
		checkboxSizer.Add(self.addon_doc, 0, wx.ALL, 5)
		checkboxSizer.Add(self.addon_locale, 0, wx.ALL, 5)
		main_sizer.Add(checkboxSizer, 0, wx.EXPAND | wx.ALL, 10)

		# Buttons
		actionBox = wx.StaticBox(panel, label=_("Actions"))
		actionSizer = wx.StaticBoxSizer(actionBox, wx.HORIZONTAL)

		generate_button = wx.Button(panel, label=_("&Generate"))
		generate_button.Bind(wx.EVT_BUTTON, self.onGenerate)
		clean_button = wx.Button(panel, label=_("C&lean"))
		clean_button.Bind(wx.EVT_BUTTON, self.onClean)
		clone_button = wx.Button(panel, label=_("Clone the official &NVDA repository."))
		clone_button.Bind(wx.EVT_BUTTON, self.onCloneRepository)
		cancel_button = wx.Button(panel, wx.ID_CANCEL, label=_("&Cancel"))
		cancel_button.Bind(wx.EVT_BUTTON, self.onCancel)

		actionSizer.Add(generate_button, 0, wx.ALL, 5)
		actionSizer.Add(clean_button, 0, wx.ALL, 5)
		actionSizer.Add(clone_button, 0, wx.ALL, 5)
		actionSizer.Add(cancel_button, 0, wx.ALL, 5)
		main_sizer.Add(actionSizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

		panel.SetSizerAndFit(main_sizer)
		self.folder_picker.SetFocus()
		self.Fit()

	def onGenerate(self, event):
		self.destination_folder = self.folder_picker.GetPath()
		self.new_folder_name = self.addon_name.GetValue()
		self.desc = self.addon_description.GetValue().strip()
		self.private= get_allow_github_publish()

		# Dictionary with template variables
		variables = {
			"name": self.addon_name.GetValue(),
			"summary": self.addon_summary.GetValue(),
			"description": self.addon_description.GetValue(),
			"author": self.addon_author.GetValue(),
			"version": self.addon_version.GetValue(),
			"minimumNVDAVersion": self.addon_minimumNVDAVersion.GetValue(),
			"lastTestedNVDAVersion": self.addon_lastTestedNVDAVersion.GetValue(),
			"module": self.selected_module.GetStringSelection(),
		}

		if not self.destination_folder:  # Checks if the destination folder is empty
			self.show_message(_("Directory path cannot be empty."), _("Missing information"))
			self.folder_picker.SetFocus()
			return

		if self._are_required_fields_empty(variables):  # Checks if the required fields are empty
			return

		# --- GitHub authentication (only if publishing is allowed) ---
		if get_allow_github_publish():
			auth_dialog = GitHubAuthentication(self, _("GitHub Authentication"))

			if auth_dialog.ShowModal() == wx.ID_OK:
				self.token = auth_dialog.token
				self.owner = auth_dialog.owner
			else:
				# translators: This message is shown when the user cancels the authentication dialog or if the authentication fails.
				self.show_message(_("Authentication was canceled or failed."), _("Error"))
				return
		else:
			# If publishing is disabled, GitHub options will be ignored.
			self.token = ""
			self.owner = ""

		# Set the add-on path
		self.destination_folder = os.path.abspath(self.destination_folder)
		self.base_folder = os.path.join(self.destination_folder, self.new_folder_name)

		self.progress_dialog = ProgressDialog(self, _("Creating Addon"))
		self.progress_dialog.Show()

		# Create the add-on structure
		self.creation_thread = AddonCreationThread(
			self,
			self.base_folder,
			self.new_folder_name,
			self.desc,
			self.owner,
			self.token,
			self.private,
			TEMPLATE_PATH,
			variables,
		)
		self.creation_thread.start()

	def onClean(self, event):
		"""
		Cleans the form fields and resets the add-on creation dialog to its initial state."""
		text_controls = [
			self.addon_author,
			self.addon_description,
			self.addon_lastTestedNVDAVersion,
			self.addon_minimumNVDAVersion,
			self.addon_name,
			self.addon_summary,
			self.addon_version,
		]
		for ctrl in text_controls:
			ctrl.Clear()

		self.addon_doc.SetValue(False)
		self.addon_locale.SetValue(False)

		self.addon_version.SetValue(DEFAULTS["version"])
		self.addon_minimumNVDAVersion.SetValue(DEFAULTS["minNVDA"])
		self.addon_lastTestedNVDAVersion.SetValue(DEFAULTS["lastNVDA"])
		self.addon_name.SetFocus()

	def _are_required_fields_empty(self, variables):
		"""
		Checks if any of the required fields are empty."""
		required_fields = {
			"name": (self.addon_name, _("Addon name")),
			"summary": (self.addon_summary, _("Addon summary")),
			"description": (self.addon_description, _("Addon description")),
			"author": (self.addon_author, _("Author")),
			"version": (self.addon_version, _("Version")),
			"minimumNVDAVersion": (self.addon_minimumNVDAVersion, _("Minimum NVDA Version")),
			"lastTestedNVDAVersion": (self.addon_lastTestedNVDAVersion, _("Last Tested NVDA Version")),
		}

		for key, (control, label) in required_fields.items():
			value = variables.get(key, "").strip()
			if not value:
				# translators: This message is shown when a required field is empty.
				self.show_message(
					_("The field '{}' cannot be empty.").format(label),
					_("Missing information"),
					wx.OK | wx.ICON_WARNING,
				)
				control.SetFocus()
				return True
		return False

	def onCloneRepository(self, event):
		"""Clones the official NVDA repository to a local folder."""
		repo_url = "https://github.com/nvaccess/nvda"

		with wx.DirDialog(
			self,
			# translators: This message is shown when the user is prompted to choose a folder to clone the NVDA repository.
			message=_("Choose the folder where the NVDA repository will be cloned:"),
			style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				# translators: This message is shown when the user cancels the cloning operation.
				gui.messageBox(_("Clone canceled by the user."), _("Info"), wx.OK | wx.ICON_INFORMATION)
				return

			destination_folder = dialog.GetPath()

			progress_dialog = ProgressDialog(self, _("Cloning NVDA Repository"))
			progress_dialog.Show()

			thread = CloneNVDARepoThread(self, repo_url, destination_folder, progress_dialog)
			thread.start()

	def focus_on_empty_field(self, field):
		"""
		Sets focus on the specified empty field in the addon form.
		Parameters:
			field (str): The name of the field to focus on.
						 Accepted values are:
						 - "name": Focuses on the addon name field.
						 - "summary": Focuses on the addon summary field.
						 - "description": Focuses on the addon description field.
						 - "author": Focuses on the addon author field.
						 - "version": Focuses on the addon version field.
						 - "minimumNVDAVersion": Focuses on the minimum NVDA version field.
						 - "lastTestedNVDAVersion": Focuses on the last tested NVDA version field.
		Raises:
			AttributeError: If the specified field does not exist or is not recognized.
		"""

		if field == "name":
			self.addon_name.SetFocus()
		elif field == "summary":
			self.addon_summary.SetFocus()
		elif field == "description":
			self.addon_description.SetFocus()
		elif field == "author":
			self.addon_author.SetFocus()
		elif field == "version":
			self.addon_version.SetFocus()
		elif field == "minimumNVDAVersion":
			self.addon_minimumNVDAVersion.SetFocus()
		elif field == "lastTestedNVDAVersion":
			self.addon_lastTestedNVDAVersion.SetFocus()

	def show_message(self, message, caption=_("Attention"), style=wx.OK | wx.ICON_INFORMATION):
		"""
		Displays a message to the user in a dialog box.

		Args:
				message(str): The message to be displayed.
				caption(str, optional): The title of the dialog box. The default is ("").
				style(int, optional): The style of the dialog box,
				combining flags like wx.OK,
				wx.CANCEL, wx.ICON INFORMATION, etc. The default is wx.OK | wx.ICON_INFORMATION.
		"""

		dlg = wx.MessageDialog(self, message, caption, style)
		dlg.ShowModal()
		dlg.Destroy()

	def onCancel(self, event):
		"""
		Cancels the dialogue and destroys the window.

		Args:
		event(wx.Event): The event triggered by the cancel button.
		"""
		if self.creation_thread and self.creation_thread.is_alive():
			self.show_message(
				_("Please wait for the add-on creation to finish before closing."), _("Warning")
			)
			return
		self.Destroy()
		Genesis._instance = None  # Reset the instance to allow reopening the dialog
