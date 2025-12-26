# chargingNotifier add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2025 Cary-rowen <manchen_0528@outlook.com>

"""Settings panel for charging notifier preferences."""

import addonHandler
import config
import gui
import wx
from gui import guiHelper

try:
	addonHandler.initTranslation()
except addonHandler.AddonError:
	pass


class ChargingNotifierPanel(gui.settingsDialogs.SettingsPanel):
	"""Settings panel for configuring charging status notifications."""

	# Translators: Title of the Charging Notifier settings panel.
	title = _("Charging Notifier")

	def makeSettings(self, settingsSizer):
		helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		# Translators: Label for the notification type combo box.
		label = _("Charging status notification type:")
		# Translators: Notification option.
		choices = [_("Voice"), _("Sound"), _("Voice and Sound")]

		self._notificationTypeChoice = helper.addLabeledControl(
			label,
			wx.Choice,
			choices=choices,
		)
		self._notificationTypeChoice.SetSelection(
			config.conf["chargingNotifier"]["notificationType"]
		)

	def onSave(self):
		config.conf["chargingNotifier"]["notificationType"] = (
			self._notificationTypeChoice.GetSelection()
		)
