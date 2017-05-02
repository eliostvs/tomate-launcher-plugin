from __future__ import unicode_literals

import pytest
from mock import Mock, patch
from tomate.constant import State
from tomate.graph import graph


@pytest.fixture()
@patch('gi.repository.Unity.LauncherEntry')
def plugin(launcher_entry):
    graph.register_factory('tomate.session', Mock)

    from launcher_plugin import LauncherPlugin

    return LauncherPlugin()


@patch('gi.repository.Unity.LauncherEntry')
def test_get_tomate_desktop_id(launcher_entry):
    graph.register_factory('tomate.session', Mock)

    from launcher_plugin import LauncherPlugin

    LauncherPlugin()

    launcher_entry.get_for_desktop_id.assert_called_with('tomate-gtk.desktop')


def test_should_show_count_when_activate_and_pomodoro_is_stopped(plugin):
    plugin.session.status.return_value = {'state': State.stopped, 'sessions': 2}

    plugin.activate()

    plugin.launcher.set_property.assert_any_call('count', 2)
    plugin.launcher.set_property.assert_any_call('count_visible', True)


def test_should_show_progress_whem_activate_and_pomodoro_is_running(plugin):
    plugin.session.status.return_value = {'state': State.started, 'sessions': 2}
    plugin.activate()

    plugin.launcher.set_property.assert_any_call('progress_visible', True)


def test_should_hide_launcher_and_progress_when_deactivate(plugin):
    plugin.deactivate()

    plugin.launcher.set_property.assert_any_call('progress_visible', False)
    plugin.launcher.set_property.assert_any_call('count_visible', False)


def test_should_hide_count_and_show_progress_when_session_started(plugin):
    plugin.on_session_started()

    plugin.launcher.set_property.assert_any_call('progress_visible', True)
    plugin.launcher.set_property.assert_any_call('progress', 0)
    plugin.launcher.set_property.assert_any_call('count_visible', False)


def test_should_show_count_and_hide_progress_when_session_ended(plugin):
    plugin.on_session_ended(sessions=4)

    plugin.launcher.set_property.assert_any_call('progress_visible', False)
    plugin.launcher.set_property.assert_any_call('count_visible', True)
    plugin.launcher.set_property.assert_any_call('count', 4)


def test_should_update_progress_when_timer_updated(plugin):
    plugin.update_progress()
    plugin.launcher.set_property.assert_called_with('progress', 0)

    plugin.update_progress(time_ratio=0.5)
    plugin.launcher.set_property.assert_called_with('progress', 0.5)
