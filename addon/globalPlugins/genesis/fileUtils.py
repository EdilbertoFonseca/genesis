# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 21/11/2024.
"""

import ctypes
import os
import shutil
from pathlib import Path

import gui
import ui
import wx
from logHandler import log


def set_hidden_attribute(path):
	"""Defines a file or folder as hidden on Windows."""
	FILE_ATTRIBUTE_HIDDEN = 0x02
	try:
		path = Path(path)
		if not path.exists():
			log.warning("The specified path does not exist: {}".format(path))
			return

		attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
		if attrs == -1:
			log.warning("Error obtaining attributes of {}. Error code: {}".format(path, ctypes.GetLastError()))
			return

		if not (attrs & FILE_ATTRIBUTE_HIDDEN):
			ctypes.windll.kernel32.SetFileAttributesW(str(path), attrs | FILE_ATTRIBUTE_HIDDEN)
			log.info("Hidden attribute set for: {}".format(path))
		else:
			log.info(f"The file or folder is already hidden: {path}")

	except Exception as e:
		log.warning("Failed to set hidden attribute for {}: {}".format(path, e))

def copy_folder(origin, destination):
	"""Copies the contents from one folder to another."""
	if not os.path.exists(origin):
		# translators: This message is shown when the source folder does not exist.
		msg = _("The folder of origin does not exist.")
		log.error(msg)
		wx.MessageBox(msg, _("Error"), wx.OK | wx.ICON_ERROR)
		return

	# Create the destination folder if it does not exist
	if not os.path.exists(destination):
		try:
			os.makedirs(destination, exist_ok=True)
		except OSError as e:
			# translators: This message is shown when there is an error creating the destination folder.
			msg = "Failed to create folder '{}': {}".format(destination, e)
			log.error(msg)
			wx.MessageBox(msg, _("Error"), wx.OK | wx.ICON_ERROR)
			return

	# Itra on items within the source folder
	for item in os.listdir(origin):
		origin_item = os.path.join(origin, item)
		destino_item = os.path.join(destination, item)

		if os.path.isdir(origin_item):
			copy_folder(origin_item, destino_item)
		else:
			try:
				shutil.copy2(origin_item, destino_item)

				# Restores the hidden attribute in the .git folder, if it exists in the destination
				git_folder = Path(destination) / ".git"
				if git_folder.exists():
					set_hidden_attribute(git_folder)

			except (PermissionError, IOError) as e:
				# translators: This message is shown when there is an error copying a file.
				msg = "Copying error {} -> {}: {}".format(origin_item, destino_item, e)
				log.warning(msg)
				wx.MessageBox(msg, _("Warning"), wx.OK | wx.ICON_WARNING)

def remove_directory(self, directory):
	"""Removes the specified directory and its contents."""
	try:
		if os.path.exists(directory):
			ui.message(
				_("Trying to remove the files from the directory {}...").format(directory))
			for root, dirs, files in os.walk(directory, topdown=False):
				for name in files:
					file_path = os.path.join(root, name)
					os.chmod(file_path, 0o777)
					os.remove(file_path)
				for name in dirs:
					os.rmdir(os.path.join(root, name))
			os.rmdir(directory)
			# translators: This message is shown when the directory is successfully removed.
			gui.messageBox(
				_("The directory {} was successfully removed!").format(directory),
				_("Success"),
				wx.OK | wx.ICON_INFORMATION
			)
		else:
			# translators: This message is shown when the specified directory does not exist.
			gui.messageBox(
				_("The directory {} does not exist.").format(directory),
				_("Info"),
				wx.OK | wx.ICON_INFORMATION
			)
	except Exception as e:
		log.error("Error when trying to remove the directory: {}".format(str(e)))
		# translators: This message is shown when there is an error removing the directory.
		self.show_message(
			_("Error when trying to remove the directory: {}").format(e))
