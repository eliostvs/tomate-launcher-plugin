import logging

import gi

gi.require_version("Unity", "7.0")

from gi.repository import Unity

from tomate.pomodoro.event import Events, on
from tomate.pomodoro.graph import graph
from tomate.pomodoro.plugin import Plugin, suppress_errors
from tomate.pomodoro.session import Payload as SessionPayload
from tomate.pomodoro.timer import Payload as TimerPayload

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
        logger.debug("action=disable_counter")
        self.widget.set_property("count_visible", False)

    @suppress_errors
    @on(Events.SESSION_START)
    def on_session_started(self, *_, **__):
        self.disable_counter()
        self.enable_progress()

    def enable_progress(self):
        logger.debug("action=enable_progress")
        self.widget.set_property("progress", 0)
        self.widget.set_property("progress_visible", True)

    @suppress_errors
    @on(Events.SESSION_END, Events.SESSION_INTERRUPT)
    def on_session_ended(self, *_, payload: SessionPayload):
        self.disable_progress()
        self.enable_counter()
        self.update_counter(payload.pomodoros)

    def disable_progress(self):
        logger.debug("action=disable_progress")
        self.widget.set_property("progress_visible", False)

    def enable_counter(self):
        logger.debug("action=enable_counter")
        self.widget.set_property("count_visible", True)

    @suppress_errors
    @on(Events.TIMER_UPDATE)
    def update_progress(self, _, payload: TimerPayload):
        logger.debug("action=update progress=%.1f", payload.elapsed_ratio)
        self.widget.set_property("progress", payload.elapsed_ratio)

    @suppress_errors
    @on(Events.SESSION_RESET)
    def reset_counter(self, *_, **__):
        self.update_counter(0)

    def update_counter(self, count: int):
        logger.debug("action=update counter=%d", count)
        self.widget.set_property("count", count)
