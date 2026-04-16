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

from pathlib import Path
import versionInfo
from logHandler import log

# Default add-on configuration
DEFAULTS = {
	"version": "2025.1.0",
	"minNVDA": "2023.3.4",
	"lastNVDA": versionInfo.version,  # versão do NVDA em execução
}

# List of selectable modules
SELECT_MODULE = [
	"appModules",
	"brailleDisplayDrivers",
	"globalPlugins",
	"synthDrivers",
	"visionEnhancementProviders",
]


def createAddonStructure(baseFolder, module, doc=False, locale=False):
	"""
	Creates the basic structure of add-on in the specified directory.
	"""
	baseFolder = Path(baseFolder)
	addonFolder = baseFolder / "addon"

	try:
		addonFolder.mkdir(parents=True, exist_ok=True)
		(addonFolder / module).mkdir(exist_ok=True)

		if doc:
			(addonFolder / "doc").mkdir(exist_ok=True)
		if locale:
			(addonFolder / "locale").mkdir(exist_ok=True)

		log.info("Addon structure created in {}".format(addonFolder))
		return True
	except Exception as e:
		log.error("Error creating addon structure: {}".format(e))
		return False


def fillTemplate(TEMPLATE_PATH, outputPath, variables):
	"""
	Fills a template file with the provided variables and saves it to the specified output path.

	Improvements applied:
	Robust path verification
	Cleaner and more consistent logging
	Removal of potential encoding issues
	"""

	templatePath = Path(TEMPLATE_PATH)
	outputPath = Path(outputPath)

	try:
		if not templatePath.exists():
			log.error(f"Template not found: {templatePath}")
			return False

		content = templatePath.read_text(encoding="utf-8")

		for key, value in variables.items():
			content = content.replace(f"{{{key}}}", str(value))

		outputFile = outputPath / "buildVars.py"
		outputFile.write_text(content, encoding="utf-8")

		log.info(f"Template successfully filled: {outputFile}")
		return True

	except Exception as e:
		log.error("Error processing template: {}".format(e))
		return False
