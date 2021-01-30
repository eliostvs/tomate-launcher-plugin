import pytest

from tomate.pomodoro import State, Sessions
from tomate.pomodoro.event import Events
from tomate.pomodoro.graph import graph
from tomate.pomodoro.session import Session, Payload as SessionPayload
from tomate.pomodoro.timer import Payload as TimerPayload


@pytest.fixture()
def session(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture()
def subject(session):
    graph.providers.clear()

    graph.register_instance("tomate.session", session)

    Events.Session.receivers.clear()
    Events.Timer.receivers.clear()

    from launcher_plugin import LauncherPlugin
    return LauncherPlugin()


def test_active_plugin_when_session_is_not_running(session, subject):
    session.is_running.return_value = False
    session.pomodoros = 5

    subject.activate()

    assert subject.widget.get_progress_visible() is False
    assert subject.widget.get_count_visible() is True
    assert subject.widget.get_count() == 5


def test_active_plugin_when_session_is_running(session, subject):
    session.is_running.return_value = True
    subject.widget.set_count_visible(True)
    subject.widget.set_progress_visible(False)

    subject.activate()

    assert subject.widget.get_count_visible() is False
    assert subject.widget.get_progress_visible() is True
    assert subject.widget.get_progress() == 0.0


def test_deactivate_plugin(subject):
    subject.widget.set_count_visible(True)
    subject.widget.set_progress_visible(True)

    subject.deactivate()

    assert subject.widget.get_count_visible() is False
    assert subject.widget.get_progress_visible() is False


def test_enable_progress_when_session_start(session, subject):
    subject.activate()

    Events.Session.send(State.started)

    assert subject.widget.get_progress_visible() is True
    assert subject.widget.get_progress() == 0.0
    assert subject.widget.get_count_visible() is False


@pytest.mark.parametrize("event", [State.finished, State.stopped])
def test_show_counter_when_session_stop(event, subject):
    subject.activate()

    payload = SessionPayload(
        id="1234",
        state=event,
        type=Sessions.pomodoro,
        duration=0,
        pomodoros=4,
    )

    Events.Session.send(event, payload=payload)

    assert subject.widget.get_progress_visible() is False
    assert subject.widget.get_count_visible() is True
    assert subject.widget.get_count() == 4


def test_update_progress_when_timer_change(session, subject):
    subject.activate()

    payload = TimerPayload(time_left=5, duration=10)
    Events.Timer.send(State.changed, payload=payload)

    assert subject.widget.get_progress() == 0.5


def test_reset_counter_when_session_reset(subject):
    subject.activate()
    subject.widget.set_count(4)

    Events.Session.send(State.reset)

    assert subject.widget.get_count() == 0
