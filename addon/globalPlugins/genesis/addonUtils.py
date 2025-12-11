# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 21/11/2024.
"""

from pathlib import Path

import versionInfo
from logHandler import log

# Default add-on configuration
DEFAULTS = {
	"version": "2025.1.0",
	"minNVDA": "2023.3.4",
	"lastNVDA": versionInfo.version,
}

# List of modules that can be selected for the add-on
SELECT_MODULE = [
	"appModules",
	"brailleDisplayDrivers",
	"globalPlugins",
	"synthDrivers",
	"visionEnhancementProviders",
]

def create_addon_structure(base_folder, module, doc=False, locale=False):
	"""Creates the basic structure of add-on in the specified directory."""
	base_folder = Path(base_folder)  # Certifique-se de que base_folder é um objeto Path
	addon_folder = base_folder / "addon"

	try:
		addon_folder.mkdir(parents=True, exist_ok=True)
		(addon_folder / module).mkdir(exist_ok=True)

		if doc:
			(addon_folder / "doc").mkdir(exist_ok=True)
		if locale:
			(addon_folder / "locale").mkdir(exist_ok=True)

		log.info("Addon structure created in {}".format(addon_folder))
		return True
	except Exception as e:
		log.error("Error creating addon structure: {}".format(e))
		return False


def fill_template(TEMPLATE_PATH, output_path, variables):
	"""Fills a template file with the provided variables and saves it to the specified output path."""
	template_path = Path(TEMPLATE_PATH)
	output_path = Path(output_path)

	try:
		content = template_path.read_text(encoding="utf-8")
		for key, value in variables.items():
			content = content.replace(f"{{{key}}}", str(value))

		output_file = output_path / "buildVars.py"
		output_file.write_text(content, encoding="utf-8")
		log.info(f"Template successfully filled: {output_file}")
		return True
	except Exception as e:
		log.error("Error processing template: {}".format(e))
		return False
