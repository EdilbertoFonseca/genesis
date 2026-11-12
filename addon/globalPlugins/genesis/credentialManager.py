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

Created on: 11/11/2026
"""

import ctypes
from ctypes import wintypes


# Windows Credential Manager constants.
CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2
ERROR_NOT_FOUND = 1168

# Credential identification.
CREDENTIAL_TARGET = "Genesis:GitHub"
CREDENTIAL_USERNAME = "GitHub"


class CREDENTIALW(ctypes.Structure):
	"""
	Windows credential structure.
	"""

	_fields_ = [
		("Flags", wintypes.DWORD),
		("Type", wintypes.DWORD),
		("TargetName", wintypes.LPWSTR),
		("Comment", wintypes.LPWSTR),
		("LastWritten", wintypes.FILETIME),
		("CredentialBlobSize", wintypes.DWORD),
		("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
		("Persist", wintypes.DWORD),
		("AttributeCount", wintypes.DWORD),
		("Attributes", ctypes.c_void_p),
		("TargetAlias", wintypes.LPWSTR),
		("UserName", wintypes.LPWSTR),
	]


# Load Windows Credential Manager API.
_advapi32 = ctypes.WinDLL("Advapi32.dll", use_last_error=True)


# Configure CredWriteW.
_CredWriteW = _advapi32.CredWriteW
_CredWriteW.argtypes = [
	ctypes.POINTER(CREDENTIALW),
	wintypes.DWORD,
]
_CredWriteW.restype = wintypes.BOOL


# Configure CredReadW.
_CredReadW = _advapi32.CredReadW
_CredReadW.argtypes = [
	wintypes.LPCWSTR,
	wintypes.DWORD,
	wintypes.DWORD,
	ctypes.POINTER(ctypes.POINTER(CREDENTIALW)),
]
_CredReadW.restype = wintypes.BOOL


# Configure CredDeleteW.
_CredDeleteW = _advapi32.CredDeleteW
_CredDeleteW.argtypes = [
	wintypes.LPCWSTR,
	wintypes.DWORD,
	wintypes.DWORD,
]
_CredDeleteW.restype = wintypes.BOOL


# Configure CredFree.
_CredFree = _advapi32.CredFree
_CredFree.argtypes = [ctypes.c_void_p]
_CredFree.restype = None


def saveGithubToken(token: str):
	"""
	Save or replace the GitHub access token.

	Args:
		token: GitHub personal access token.

	Raises:
		ValueError: If the token is empty or exceeds the supported size.
		OSError: If Windows cannot save the credential.
	"""

	token = (token or "").strip()

	if not token:
		raise ValueError("The GitHub access token cannot be empty.")

	blob = token.encode("utf-8")

	# Windows generic credentials support a maximum of 2560 bytes.
	if len(blob) > 2560:
		raise ValueError(
			"The GitHub access token exceeds the supported size.",
		)

	credentialBlob = ctypes.create_string_buffer(blob)

	credential = CREDENTIALW(
		Flags=0,
		Type=CRED_TYPE_GENERIC,
		TargetName=CREDENTIAL_TARGET,
		Comment="Genesis GitHub access token",
		LastWritten=wintypes.FILETIME(),
		CredentialBlobSize=len(blob),
		CredentialBlob=ctypes.cast(
			credentialBlob,
			ctypes.POINTER(ctypes.c_ubyte),
		),
		Persist=CRED_PERSIST_LOCAL_MACHINE,
		AttributeCount=0,
		Attributes=None,
		TargetAlias=None,
		UserName=CREDENTIAL_USERNAME,
	)

	if not _CredWriteW(ctypes.byref(credential), 0):
		raise ctypes.WinError(ctypes.get_last_error())


def getGithubToken():
	"""
	Retrieve the GitHub access token from Windows Credential Manager.

	Returns:
		The stored token, or None if no credential exists.

	Raises:
		OSError: If Windows cannot retrieve the credential.
		UnicodeDecodeError: If the stored credential is not valid UTF-8.
	"""

	credentialPointer = ctypes.POINTER(CREDENTIALW)()

	if not _CredReadW(
		CREDENTIAL_TARGET,
		CRED_TYPE_GENERIC,
		0,
		ctypes.byref(credentialPointer),
	):
		errorCode = ctypes.get_last_error()

		if errorCode == ERROR_NOT_FOUND:
			return None

		raise ctypes.WinError(errorCode)

	try:
		credential = credentialPointer.contents

		blob = ctypes.string_at(
			credential.CredentialBlob,
			credential.CredentialBlobSize,
		)

		return blob.decode("utf-8")

	finally:
		_CredFree(credentialPointer)


def deleteGithubToken():
	"""
	Delete the stored GitHub access token.

	Returns:
		True if the credential was deleted, False if it did not exist.

	Raises:
		OSError: If Windows cannot delete the credential.
	"""

	if _CredDeleteW(CREDENTIAL_TARGET, CRED_TYPE_GENERIC, 0):
		return True

	errorCode = ctypes.get_last_error()

	if errorCode == ERROR_NOT_FOUND:
		return False

	raise ctypes.WinError(errorCode)


def hasGithubToken():
	"""
	Check whether a GitHub access token is stored.

	Returns:
		True if a credential exists, False otherwise.
	"""

	return getGithubToken() is not None
