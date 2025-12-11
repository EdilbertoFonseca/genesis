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
import globalPluginHandler
import globalVars
import gui
import ui
import wx
from logHandler import log
from scriptHandler import script

from .dialogs import GenesisSettingsPanel
from .main import Genesis
from .varsConfig import ADDON_SUMMARY, addonPath, initConfiguration

# Add the lib/ folder to sys.path (only once)
libPath = os.path.join(addonPath, "lib")
if libPath not in sys.path:
	sys.path.insert(0, libPath)

# Initializes the translation
addonHandler.initTranslation()

_isGenesisOpen = False  # To track if the Genesis dialog is already open
dlgGenesis = None  # Reference to the Genesis dialog instance

def onGenesisClosed(evt):
	""" Handler for when the Genesis dialog is closed. """
	global 	_isGenesisOpen
	_isGenesisOpen = False
	evt.Skip()

def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls


@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# Creating the constructor of the newly created GlobalPlugin class.
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self.create_menu()

	def create_menu(self):
		# Initialize configuration
		initConfiguration()

		# Register the settings panel in NVDA
		if GenesisSettingsPanel not in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(GenesisSettingsPanel)

		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		# Translators: Add-on title in the tools menu.
		self.genesis = self.toolsMenu.Append(wx.ID_ANY, f"&{ADDON_SUMMARY}...")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_onGenesis, self.genesis)

	# defining a script with decorator:
	@script(
		gesture="kb:NVDA+Shift+G",
		# Translators: Text displayed in NVDA help.
		description=_(
			"This add-on for NVDA offers a practical and affordable tool for developers to create new add-ons."
		),
		category=ADDON_SUMMARY,
	)
	def script_onGenesis(self, gesture):
		global _isGenesisOpen, dlgGenesis

		if _isGenesisOpen:
			ui.message(_("An instance of {} is already open.").format(ADDON_SUMMARY))
			return

		_isGenesisOpen = True

		dlgGenesis = Genesis(gui.mainFrame, ADDON_SUMMARY)
		dlgGenesis.Bind(wx.EVT_WINDOW_DESTROY, onGenesisClosed)

		gui.mainFrame.prePopup()
		dlgGenesis.CentreOnScreen()
		dlgGenesis.Show()
		gui.mainFrame.postPopup()

	# This terminate function is necessary when creating new menus.
	def terminate(self):
		super(GlobalPlugin, self).terminate()
		# Remove the panel when the add-on is uninstalled
		if GenesisSettingsPanel in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(GenesisSettingsPanel)

		try:
			self.toolsMenu.Remove(self.genesis)
		except Exception as e:
			log.warning(f"Error removing Scraps and Genesis item: {e}")
