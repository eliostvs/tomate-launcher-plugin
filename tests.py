from __future__ import unicode_literals

import unittest

from mock import Mock, patch


@patch('gi.repository.Unity.LauncherEntry.set_property')
class LauncherPluginTestCase(unittest.TestCase):

    def setUp(self):
        from launcher_plugin import LauncherPlugin
        self.plugin = LauncherPlugin()
        self.plugin.application = Mock()

    @patch('gi.repository.Unity.LauncherEntry.get_for_desktop_id')
    def test_should_get_tomate_desktop_id(self, mget_for_desktop_id, *args):
        from launcher_plugin import LauncherPlugin

        LauncherPlugin()

        mget_for_desktop_id.assert_called_with('tomate-gtk.desktop')

    def test_should_show_count_when_activate_and_pomodoro_is_stopped(self, mset_property):
        self.plugin.application.status.return_value = {'pomodoro': {'sessions': 2, 'state': 'stopped'}}
        self.plugin.activate()

        mset_property.assert_any_call('count', 2)
        mset_property.assert_any_call('count_visible', True)

    def test_should_show_progress_whem_activate_and_pomodoro_is_running(self, mset_property):
        self.plugin.application.status.return_value = {'pomodoro': {'progress': 0.2, 'state': 'running'}}
        self.plugin.activate()

        mset_property.assert_any_call('progress_visible', True)

    def test_should_hide_launcher_and_progress_when_deactivate(self, mset_property):
        self.plugin.deactivate()

        mset_property.assert_any_call('progress_visible', False)
        mset_property.assert_any_call('count_visible', False)

    def test_should_hide_count_and_show_progress_when_session_started(self, mset_property):
        self.plugin.on_session_started()

        mset_property.assert_any_call('progress_visible', True)
        mset_property.assert_any_call('progress', 0)
        mset_property.assert_any_call('count_visible', False)

    def test_should_show_count_and_hide_progress_when_session_ended(self, mset_property):
        self.plugin.on_session_ended(sessions=4)

        mset_property.assert_any_call('progress_visible', False)
        mset_property.assert_any_call('count_visible', True)
        mset_property.assert_any_call('count', 4)

    def test_should_update_progress_when_timer_updated(self, mset_property):
        self.plugin.update_progress()
        mset_property.assert_called_with('progress', 0)

        self.plugin.update_progress(time_ratio=0.5)
        mset_property.assert_called_with('progress', 0.5)
