import pytest
from wiring import Graph

from tomate.pomodoro import Bus, Events, Session, SessionPayload, SessionType, TimerPayload


@pytest.fixture
def bus() -> Bus:
    return Bus()


@pytest.fixture
def graph() -> Graph:
    g = Graph()
    g.register_instance(Graph, g)
    return g


@pytest.fixture
def session(mocker):
    return mocker.Mock(spec=Session)


@pytest.fixture
def subject(bus, graph, session):
    graph.providers.clear()
    graph.register_instance("tomate.bus", bus)
    graph.register_instance("tomate.session", session)

    import launcher_plugin

    instance = launcher_plugin.LauncherPlugin()
    instance.configure(bus, graph)
    return instance


def test_active_plugin_when_session_is_not_running(session, subject):
    session.is_running.return_value = False
    session.pomodoros = 5

    subject.activate()

    assert subject.launcher.get_progress_visible() is False
    assert subject.launcher.get_count_visible() is True
    assert subject.launcher.get_count() == 5


def test_active_plugin_when_session_is_running(session, subject):
    session.is_running.return_value = True
    subject.launcher.set_count_visible(True)
    subject.launcher.set_progress_visible(False)

    subject.activate()

    assert subject.launcher.get_count_visible() is False
    assert subject.launcher.get_progress_visible() is True
    assert subject.launcher.get_progress() == 0.0


def test_deactivate_plugin(subject):
    subject.launcher.set_count_visible(True)
    subject.launcher.set_progress_visible(True)

    subject.deactivate()

    assert subject.launcher.get_count_visible() is False
    assert subject.launcher.get_progress_visible() is False


def test_enable_progress_when_session_start(bus, session, subject):
    subject.activate()

    bus.send(Events.SESSION_START)

    assert subject.launcher.get_progress_visible() is True
    assert subject.launcher.get_progress() == 0.0
    assert subject.launcher.get_count_visible() is False


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

    assert subject.launcher.get_progress_visible() is False
    assert subject.launcher.get_count_visible() is True
    assert subject.launcher.get_count() == 4


def test_updates_progress_when_timer_change(bus, session, subject):
    subject.activate()

    bus.send(Events.TIMER_UPDATE, payload=TimerPayload(time_left=5, duration=10))

    assert subject.launcher.get_progress() == 0.5


def test_resets_counter_when_session_reset(bus, subject):
    subject.activate()
    subject.launcher.set_count(4)

    bus.send(Events.SESSION_RESET)

    assert subject.launcher.get_count() == 0
