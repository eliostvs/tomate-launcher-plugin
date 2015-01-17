from __future__ import unicode_literals

import unittest

from mock import patch


@patch('gi.repository.Unity.LauncherEntry.set_property')
class LauncherPluginTestCase(unittest.TestCase):

    def setUp(self):
        from launcher_plugin import LauncherPlugin
        self.plugin = LauncherPlugin()

    @patch('gi.repository.Unity.LauncherEntry.get_for_desktop_id')
    def test_should_get_tomate_desktop_id(self, mget_for_desktop_id, *args):
        from launcher_plugin import LauncherPlugin

        LauncherPlugin()

        mget_for_desktop_id.assert_called_with('tomate-gtk.desktop')

    def test_should_hide_launcher_and_progress(self, mset_property):
        self.plugin.deactivate()

        mset_property.assert_any_call('progress_visible', False)
        mset_property.assert_any_call('count_visible', False)

    def test_should_reset_and_show_progress(self, mset_property):
        self.plugin.on_session_started()

        mset_property.assert_any_call('progress', 0)
        mset_property.assert_any_call('progress_visible', True)

    def test_should_hide_counter(self, mset_property):
        self.plugin.on_session_started()

        mset_property.assert_any_call('count_visible', False)

    def test_should_show_counter(self, mset_property):
        self.plugin.show_counter(sessions=2)

        mset_property.assert_any_call('count_visible', True)
        mset_property.assert_any_call('count', 2)

        mset_property.reset_mock()

        self.plugin.show_counter()

        mset_property.assert_any_call('count_visible', True)
        mset_property.assert_any_call('count', 0)

    def test_should_hide_progress(self, mset_property):
        self.plugin.show_counter()

        mset_property.assert_any_call('progress_visible', False)

    def test_should_increment_progress(self, mset_property):
        self.plugin.on_timer_updated()
        mset_property.assert_called_with('progress', 0)

        self.plugin.on_timer_updated(time_ratio=0.5)
        mset_property.assert_called_with('progress', 0.5)
