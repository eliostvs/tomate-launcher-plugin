import pytest
from blinker import NamedSignal

from tomate.pomodoro.event import Events
from tomate.pomodoro.graph import graph
from tomate.pomodoro.session import Payload as SessionPayload, Session, Type as SessionType
from tomate.pomodoro.timer import Payload as TimerPayload


@pytest.fixture
def bus():
    return NamedSignal("Test")


@pytest.fixture
def session(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture
def subject(bus, session):
    graph.providers.clear()
    graph.register_instance("tomate.bus", bus)
    graph.register_instance("tomate.session", session)

    import launcher_plugin

    return launcher_plugin.LauncherPlugin()


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


def test_enable_progress_when_session_start(bus, session, subject):
    subject.activate()

    bus.send(Events.SESSION_START)

    assert subject.widget.get_progress_visible() is True
    assert subject.widget.get_progress() == 0.0
    assert subject.widget.get_count_visible() is False


@pytest.mark.parametrize("event", [Events.SESSION_END, Events.SESSION_INTERRUPT])
def test_show_counter_when_session_stop(event, bus, subject):
    subject.activate()

    payload = SessionPayload(
        id="1234",
        type=SessionType.POMODORO,
        duration=0,
        pomodoros=4,
    )
    bus.send(event, payload=payload)

    assert subject.widget.get_progress_visible() is False
    assert subject.widget.get_count_visible() is True
    assert subject.widget.get_count() == 4


def test_updates_progress_when_timer_change(bus, session, subject):
    subject.activate()

    bus.send(Events.TIMER_UPDATE, payload=TimerPayload(time_left=5, duration=10))

    assert subject.widget.get_progress() == 0.5


def test_resets_counter_when_session_reset(bus, subject):
    subject.activate()
    subject.widget.set_count(4)

    bus.send(Events.SESSION_RESET)

    assert subject.widget.get_count() == 0
