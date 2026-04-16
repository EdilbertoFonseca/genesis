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
import sys
from gettext import gettext as _

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
from .varsConfig import ADDON_SUMMARY, ADDON_PATH, initConfiguration

# Add the lib/ folder to sys.path (only once)
libPath = os.path.join(ADDON_PATH, "lib")
if libPath not in sys.path:
	sys.path.insert(0, libPath)

# Initializes the translation
addonHandler.initTranslation()


def disableInSecureMode(decoratedCls):
	"""Disable plugin in secure mode (e.g. Windows logon screen)."""
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls


@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._isGenesisOpen = False
		self.dlgGenesis = None

		self.createMenu()

	# MENU
	def createMenu(self):
		# Initialize configuration storage (configobj)
		initConfiguration()

		# Register settings panel inside NVDA settings dialog
		if GenesisSettingsPanel not in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(GenesisSettingsPanel)

		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu

		# Translators: Add-on menu item in NVDA tools menu.
		self.genesisMenuItem = self.toolsMenu.Append(wx.ID_ANY, f"&{ADDON_SUMMARY}...")

		# Bind correct handler (not unbind)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_onGenesis, self.genesisMenuItem)

	# EVENT HANDLER - DIALOG CLOSE
	def onGenesisClosed(self, evt):
		"""Called whenever the Genesis dialog is closed."""
		self._isGenesisOpen = False
		self.dlgGenesis = None
		evt.Skip()

		# SCRIPT - OPEN GENESIS

	# Defining a script with a decorator:
	@script(
		gesture="kb:NVDA+Alt+G",
		# Translators: Text displayed in NVDA help.
		description=_("This add-on offers practical tools for developers to create new NVDA add-ons."),
		category=ADDON_SUMMARY,
	)
	def script_onGenesis(self, gesture=None):
		if self._isGenesisOpen:
			ui.message(
				_("An instance of {} is already open.").format(ADDON_SUMMARY),
			)
			return

		self._isGenesisOpen = True

		self.dlgGenesis = Genesis(gui.mainFrame, ADDON_SUMMARY)
		self.dlgGenesis.Bind(wx.EVT_WINDOW_DESTROY, self.onGenesisClosed)

		gui.mainFrame.prePopup()
		self.dlgGenesis.CentreOnScreen()
		self.dlgGenesis.Show()
		gui.mainFrame.postPopup()

	# TERMINATE
	def terminate(self):
		super().terminate()

		# Remove settings panel
		if GenesisSettingsPanel in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(GenesisSettingsPanel)

		# Remove menu item
		try:
			self.toolsMenu.Remove(self.genesisMenuItem)
		except Exception as e:
			log.warning(f"Error removing Genesis item: {e}")
