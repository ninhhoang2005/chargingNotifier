# chargingNotifier add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2025 Cary-rowen <manchen_0528@outlook.com>

"""
Replaces NVDA's voice announcements for AC power status changes
with sound notifications.
"""

import os
from enum import IntEnum

import addonHandler
import config
import globalPluginHandler
import gui
import nvwave
from winAPI import _powerTracking
from winAPI._powerTracking import PowerState, _ReportContext

from . import settings

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	pass


class NotificationType(IntEnum):
	"""Notification type for charging status changes."""
	VOICE = 0
	SOUND = 1
	VOICE_AND_SOUND = 2


# Configuration specification
CONFSPEC = {
	"notificationType": f"integer(default={NotificationType.VOICE}, min=0, max=2)",
}
config.conf.spec["chargingNotifier"] = CONFSPEC

# Store original function for restoration
_originalReportPowerStatus = _powerTracking._reportPowerStatus


def _getSoundPath(name: str) -> str:
	"""Return the full path to a sound file."""
	return os.path.join(os.path.dirname(__file__), "sounds", f"{name}.wav")


def _playChargingSound(currentState: PowerState, previousState: PowerState) -> None:
	"""Play the appropriate charging sound based on state change."""
	if currentState != previousState:
		if currentState == PowerState.AC_ONLINE:
			nvwave.playWaveFile(_getSoundPath("connected"))
		elif currentState == PowerState.AC_OFFLINE:
			nvwave.playWaveFile(_getSoundPath("disconnected"))


def _patchedReportPowerStatus(context: _ReportContext) -> None:
	"""
	Patched power status reporter that plays sounds for AC changes
	when configured to do so.
	"""
	# Only intercept AC status changes
	if context != _ReportContext.AC_STATUS_CHANGE:
		_originalReportPowerStatus(context)
		return

	notificationType = config.conf["chargingNotifier"]["notificationType"]

	# Voice mode: delegate to original
	if notificationType == NotificationType.VOICE:
		_originalReportPowerStatus(context)
		return

	# Get current power status
	status = _powerTracking._getPowerStatus()
	if status is None:
		return

	currentState = status.ACLineStatus
	previousState = _powerTracking._powerState

	# Sound mode: play sound only
	if notificationType == NotificationType.SOUND:
		_playChargingSound(currentState, previousState)
		_powerTracking._powerState = currentState
		return

	# Voice and Sound mode: play sound first, then voice
	if notificationType == NotificationType.VOICE_AND_SOUND:
		_playChargingSound(currentState, previousState)
		_originalReportPowerStatus(context)
		return


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Global plugin for charging status sound notifications."""

	def __init__(self):
		super().__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(
			settings.ChargingNotifierPanel
		)
		_powerTracking._reportPowerStatus = _patchedReportPowerStatus

	def terminate(self):
		super().terminate()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
			settings.ChargingNotifierPanel
		)
		_powerTracking._reportPowerStatus = _originalReportPowerStatus
