import logging

import gi
from gi.repository import Unity

from tomate.pomodoro import State
from tomate.pomodoro.event import Events, on
from tomate.pomodoro.graph import graph
from tomate.pomodoro.plugin import suppress_errors, Plugin
from tomate.pomodoro.session import Payload as SessionPayload
from tomate.pomodoro.timer import Payload as TimerPayload

gi.require_version("Unity", "7.0")

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

        if self.session.is_running():
            self.enable_progress()
            self.disable_counter()
        else:
            self.enable_counter()
            self.update_counter(self.session.pomodoros)

    @suppress_errors
    def deactivate(self):
        super(LauncherPlugin, self).deactivate()

        self.disable_counter()
        self.disable_progress()

    def disable_counter(self):
        self.widget.set_property("count_visible", False)

    @suppress_errors
    @on(Events.Session, [State.started])
    def on_session_started(self, *args, **kwargs):
        self.disable_counter()
        self.enable_progress()

    def enable_progress(self):
        self.widget.set_property("progress", 0)
        self.widget.set_property("progress_visible", True)

    @suppress_errors
    @on(Events.Session, [State.finished, State.stopped])
    def on_session_ended(self, *args, payload: SessionPayload):
        self.disable_progress()
        self.enable_counter()
        self.update_counter(payload.pomodoros)

    def disable_progress(self):
        self.widget.set_property("progress_visible", False)

    def enable_counter(self):
        self.widget.set_property("count_visible", True)

    @suppress_errors
    @on(Events.Timer, [State.changed])
    def update_progress(self, _, payload: TimerPayload):
        self.widget.set_property("progress", payload.elapsed_ratio)

        logger.debug("launcher progress update to %.1f", payload.elapsed_ratio)

    @suppress_errors
    @on(Events.Session, [State.reset])
    def reset_counter(self, *args, **kwargs):
        self.update_counter(0)

    def update_counter(self, count: int):
        self.widget.set_property("count", count)

        logger.debug("launcher count updated to %d", count)
