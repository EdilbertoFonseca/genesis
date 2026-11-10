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
import re
import tempfile
from pathlib import Path

import versionInfo
from logHandler import log


# Default add-on configuration
DEFAULTS = {
	"version": "2026.1.0",
	"minNVDA": "2025.1.0",
	"lastNVDA": versionInfo.version,
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
	Creates the basic structure of an add-on in the specified directory.

	Args:
		baseFolder: Base directory where the add-on structure will be created.
		module: Selected NVDA module.
		doc: Whether to create the documentation directory.
		locale: Whether to create the localization directory.

	Returns:
		bool: True if the structure was created successfully, False otherwise.
	"""
	if module not in SELECT_MODULE:
		log.error(f"Invalid add-on module: {module}")
		return False

	addonFolder = Path(baseFolder) / "addon"

	try:
		addonFolder.mkdir(parents=True, exist_ok=True)
		(addonFolder / module).mkdir(exist_ok=True)

		if doc:
			(addonFolder / "doc").mkdir(exist_ok=True)

		if locale:
			(addonFolder / "locale").mkdir(exist_ok=True)

		log.info(f"Add-on structure created in {addonFolder}")
		return True

	except OSError:
		log.exception("Error creating add-on structure")
		return False


def _fillTemplateVariables(content, variables):
	"""
	Replaces template placeholders with their corresponding values.

	Args:
		content: Template content.
		variables: Dictionary containing replacement variables.

	Returns:
		tuple: Processed content and a list of unresolved placeholders.
	"""
	if variables:
		pattern = re.compile(
			r"\{(" + "|".join(re.escape(key) for key in sorted(variables, key=len, reverse=True)) + r")\}",
		)

		content = pattern.sub(
			lambda match: str(variables[match.group(1)]),
			content,
		)

	# Identify placeholders that were not replaced.
	unresolved = re.findall(
		r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}",
		content,
	)

	return content, sorted(set(unresolved))


def fillTemplate(
	TEMPLATE_PATH_BUILD_VARS,
	TEMPLATE_PATH_PY_PROJECT,
	outputPath,
	variables,
):
	"""
	Fills template files with the provided variables and saves them.

	Args:
		TEMPLATE_PATH_BUILD_VARS: Path to the buildVars.py template.
		TEMPLATE_PATH_PY_PROJECT: Path to the pyproject.toml template.
		outputPath: Destination directory.
		variables: Dictionary containing template replacement variables.

	Returns:
		bool: True if both files were generated successfully, False otherwise.
	"""
	templatePaths = {
		"buildVars.py": Path(TEMPLATE_PATH_BUILD_VARS),
		"pyproject.toml": Path(TEMPLATE_PATH_PY_PROJECT),
	}

	outputPath = Path(outputPath)
	tempFiles = {}

	try:
		# Validate template files.
		for filename, templatePath in templatePaths.items():
			if not templatePath.is_file():
				log.error(f"Template file not found: {templatePath}")
				return False

		# Read and process all templates before writing any output.
		processedFiles = {}

		for filename, templatePath in templatePaths.items():
			content = templatePath.read_text(encoding="utf-8")

			content, unresolved = _fillTemplateVariables(
				content,
				variables,
			)

			if unresolved:
				log.error(
					f"Unresolved placeholders in {filename}: {', '.join(unresolved)}",
				)
				return False

			processedFiles[filename] = content

		# Ensure the destination directory exists.
		outputPath.mkdir(parents=True, exist_ok=True)

		if not outputPath.is_dir():
			log.error(f"Output path is not a directory: {outputPath}")
			return False

		# Write temporary files before replacing the destination files.
		for filename, content in processedFiles.items():
			with tempfile.NamedTemporaryFile(
				mode="w",
				encoding="utf-8",
				dir=outputPath,
				prefix=f".{filename}.",
				suffix=".tmp",
				delete=False,
			) as tempFile:
				tempFile.write(content)
				tempFiles[filename] = Path(tempFile.name)

		# Replace destination files only after all temporary files
		# have been successfully created.
		for filename, tempPath in tempFiles.items():
			outputFile = outputPath / filename
			os.replace(tempPath, outputFile)

			log.info(f"Template successfully generated: {outputFile}")

		return True

	except (OSError, UnicodeError, TypeError, ValueError):
		log.exception("Error processing template files")
		return False

	finally:
		# Remove any temporary files left behind.
		for tempPath in tempFiles.values():
			try:
				tempPath.unlink(missing_ok=True)
			except OSError:
				log.warning(f"Could not remove temporary file: {tempPath}")
