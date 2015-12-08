from __future__ import unicode_literals

import unittest

from mock import Mock, patch
from tomate.enums import State
from tomate.graph import graph


class TestLauncherPlugin(unittest.TestCase):

    @patch('gi.repository.Unity.LauncherEntry')
    def setUp(self, launcher_entry):
        graph.register_factory('tomate.session', Mock)

        from launcher_plugin import LauncherPlugin

        self.plugin = LauncherPlugin()
        self.launcher_entry = launcher_entry

    def test_get_tomate_desktop_id(self):
        self.launcher_entry.get_for_desktop_id.assert_called_with('tomate-gtk.desktop')

    def test_should_show_count_when_activate_and_pomodoro_is_stopped(self):
        self.plugin.session.status.return_value = {'state': State.stopped, 'sessions': 2}
        self.plugin.activate()

        self.plugin.launcher.set_property.assert_any_call('count', 2)
        self.plugin.launcher.set_property.assert_any_call('count_visible', True)

    def test_should_show_progress_whem_activate_and_pomodoro_is_running(self):
        self.plugin.session.status.return_value = {'state': State.running, 'sessions': 2}
        self.plugin.activate()

        self.plugin.launcher.set_property.assert_any_call('progress_visible', True)

    def test_should_hide_launcher_and_progress_when_deactivate(self):
        self.plugin.deactivate()

        self.plugin.launcher.set_property.assert_any_call('progress_visible', False)
        self.plugin.launcher.set_property.assert_any_call('count_visible', False)

    def test_should_hide_count_and_show_progress_when_session_started(self):
        self.plugin.on_session_started()

        self.plugin.launcher.set_property.assert_any_call('progress_visible', True)
        self.plugin.launcher.set_property.assert_any_call('progress', 0)
        self.plugin.launcher.set_property.assert_any_call('count_visible', False)

    def test_should_show_count_and_hide_progress_when_session_ended(self):
        self.plugin.on_session_ended(sessions=4)

        self.plugin.launcher.set_property.assert_any_call('progress_visible', False)
        self.plugin.launcher.set_property.assert_any_call('count_visible', True)
        self.plugin.launcher.set_property.assert_any_call('count', 4)

    def test_should_update_progress_when_timer_updated(self):
        self.plugin.update_progress()
        self.plugin.launcher.set_property.assert_called_with('progress', 0)

        self.plugin.update_progress(time_ratio=0.5)
        self.plugin.launcher.set_property.assert_called_with('progress', 0.5)
