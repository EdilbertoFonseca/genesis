# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 07/12/2025
"""

import addonHandler
import config

# Get the name of the addon defined in the manifest.
ADDON_name = addonHandler.getCodeAddon().manifest["name"]

def onUninstall():
	# Go through the configuration profiles and try to remove the 'Contacts Manager for NVDA' key
	for key, value in list(config.conf._profileCache.items()):
		try:
			del config.conf._profileCache[key][ADDON_name]
		except KeyError:
			pass  # Ignore if key does not exist

	# Save configuration changes
	config.conf.save()
