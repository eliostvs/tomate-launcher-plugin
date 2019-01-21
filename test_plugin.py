from unittest.mock import Mock, patch

import pytest

from tomate.constant import State, Sessions
from tomate.event import Events
from tomate.graph import graph
from tomate.session import Session, SessionPayload, FinishedSession
from tomate.timer import TimerPayload


def setup_function(function):
    graph.providers.clear()

    graph.register_instance("tomate.session", Mock(Session))

    Events.Session.receivers.clear()
    Events.Timer.receivers.clear()


@pytest.fixture()
@patch("gi.repository.Unity.LauncherEntry")
def plugin(launcher_entry):
    from launcher_plugin import LauncherPlugin

    return LauncherPlugin()


@patch("gi.repository.Unity.LauncherEntry")
def test_get_tomate_desktop_id(launcher_entry, mocker):
    graph.register_instance("tomate.session", mocker.Mock(Session))

    from launcher_plugin import LauncherPlugin

    LauncherPlugin()

    launcher_entry.get_for_desktop_id.assert_called_with("tomate-gtk.desktop")


class TestActivePlugin:
    def setup_method(self, method):
        setup_function(method)

    def test_should_show_count_when_session_is_stopped(self, mocker, plugin):
        # given
        plugin.session = mocker.Mock(state=State.stopped, sessions=[])

        # when
        plugin.activate()

        # then
        plugin.widget.set_property.assert_any_call("count", 0)
        plugin.widget.set_property.assert_any_call("count_visible", True)

    def test_should_show_progress_when_session_is_running(self, mocker, plugin):
        plugin.session = mocker.Mock(state=State.started)
        plugin.activate()

        plugin.widget.set_property.assert_any_call("progress_visible", True)


class TestDeactivatePlugin:
    def setup_method(self, method):
        setup_function(method)

    def test_should_hide_launcher_and_progress(self, plugin):
        # when
        plugin.deactivate()

        # then
        plugin.widget.set_property.assert_any_call("progress_visible", False)
        plugin.widget.set_property.assert_any_call("count_visible", False)


def test_should_hide_count_and_show_progress_when_session_starts(plugin, mocker):
    # given
    plugin.session = mocker.Mock(state=State.stopped, sessions=[])
    plugin.activate()

    # when
    Events.Session.send(State.started)

    # then
    plugin.widget.set_property.assert_any_call("progress_visible", True)
    plugin.widget.set_property.assert_any_call("progress", 0)
    plugin.widget.set_property.assert_any_call("count_visible", False)


def test_should_show_count_and_hide_progress_when_session_ends(plugin, mocker):
    for state_type in [State.finished, State.stopped]:
        # given
        plugin.session = mocker.Mock(state=State.started, sessions=[])
        plugin.activate()
        plugin.widget.mock_clear()

        payload = SessionPayload(
            type=Sessions.pomodoro,
            state=state_type,
            duration=0,
            task="",
            sessions=[FinishedSession(id=0, type=Sessions.pomodoro, duration=0)] * 4,
        )

        # when
        Events.Session.send(state_type, payload=payload)

        # then
        plugin.widget.set_property.assert_any_call("progress_visible", False)
        plugin.widget.set_property.assert_any_call("count_visible", True)
        plugin.widget.set_property.assert_any_call("count", 4)


def test_should_update_progress_when_timer_updates(plugin, mocker):
    # given
    plugin.session = mocker.Mock(state=State.started, sessions=[])
    payload = TimerPayload(time_left=5, duration=10)
    plugin.activate()

    # when
    Events.Timer.send(State.changed, payload=payload)

    # then
    plugin.widget.set_property.assert_called_with("progress", 0.5)


def test_should_update_counter_when_session_resets(plugin, mocker):
    # given
    plugin.session = mocker.Mock(state=State.stopped, sessions=[])
    payload = SessionPayload(
        type=Sessions.pomodoro, sessions=[], state=State.stopped, duration=0, task=""
    )
    plugin.activate()

    # when
    Events.Session.send(State.reset, payload=payload)

    # then
    plugin.widget.set_property.assert_called_with("count", 0)
