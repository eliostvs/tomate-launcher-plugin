import logging

import gi

gi.require_version("Unity", "7.0")

from gi.repository import Unity

from tomate.pomodoro import State
from tomate.pomodoro.event import Events, on
from tomate.pomodoro.graph import graph
from tomate.pomodoro.plugin import suppress_errors, Plugin
from tomate.pomodoro.session import SessionPayload, Session
from tomate.pomodoro.timer import TimerPayload

logger = logging.getLogger(__name__)


class LauncherPlugin(Plugin):
    @suppress_errors
    def __init__(self):
        super(LauncherPlugin, self).__init__()

        self.widget = Unity.LauncherEntry.get_for_desktop_id("tomate-gtk.desktop")
        self.session = graph.get("tomate.session")

    @suppress_errors
    def activate(self):
        super(LauncherPlugin, self).activate()

        if self.session.state is State.started:
            self.enable_progress()

        else:
            self.enable_counter()
            self.update_counter(len(Session.finished_pomodoros(self.session.sessions)))

    @suppress_errors
    def deactivate(self):
        super(LauncherPlugin, self).deactivate()

        self.disable_counter()
        self.disable_progress()

    @suppress_errors
    @on(Events.Session, [State.started])
    def on_session_started(self, *args, **kwargs):
        self.disable_counter()
        self.enable_progress()

    @suppress_errors
    @on(Events.Session, [State.finished, State.stopped])
    def on_session_ended(self, *args, payload: SessionPayload):
        self.disable_progress()
        self.enable_counter()
        self.update_counter(len(payload.finished_pomodoros))

    def enable_progress(self):
        self.widget.set_property("progress", 0)
        self.widget.set_property("progress_visible", True)

    def disable_progress(self):
        self.widget.set_property("progress_visible", False)

    @suppress_errors
    @on(Events.Timer, [State.changed])
    def update_progress(self, _, payload: TimerPayload):
        self.widget.set_property("progress", payload.elapsed_ratio)

        logger.debug("launcher progress update to %.1f", payload.elapsed_ratio)

    def enable_counter(self):
        self.widget.set_property("count_visible", True)

    def disable_counter(self):
        self.widget.set_property("count_visible", False)

    def update_counter(self, count: int):
        self.widget.set_property("count", count)

        logger.debug("launcher count updated to %d", count)

    @suppress_errors
    @on(Events.Session, [State.reset])
    def update_count(self, _, payload: SessionPayload):
        self.update_counter(len(payload.finished_pomodoros))
