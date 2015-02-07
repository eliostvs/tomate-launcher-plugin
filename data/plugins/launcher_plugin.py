from __future__ import unicode_literals

import logging

from gi.repository import Unity

from tomate.plugin import TomatePlugin
from tomate.utils import suppress_errors
from tomate.constants import State

logger = logging.getLogger(__name__)


class LauncherPlugin(TomatePlugin):

    signals = (
        ('session_ended', 'on_session_ended'),
        ('session_interrupted', 'on_session_ended'),
        ('session_started', 'on_session_started'),
        ('timer_updated', 'update_progress'),
    )

    @suppress_errors
    def on_init(self):
        self.launcher = Unity.LauncherEntry.get_for_desktop_id('tomate-gtk.desktop')

    @suppress_errors
    def on_activate(self):
        pomodoro = self.app.status()['pomodoro']

        if pomodoro['state'] == State.running:
            self.enable_progress()

        else:
            self.enable_count()
            self.update_count(**pomodoro)

    @suppress_errors
    def on_deactivate(self):
        self.disable_count()
        self.disable_progress()

    def on_session_started(self, *args, **kwargs):
        self.disable_count(*args, **kwargs)
        self.enable_progress(*args, **kwargs)

    def on_session_ended(self, *args, **kwargs):
        self.disable_progress(*args, **kwargs)
        self.enable_count(*args, **kwargs)
        self.update_count(*args, **kwargs)

    @suppress_errors
    def enable_progress(self, *args, **kwargs):
        self.launcher.set_property('progress', 0)
        self.launcher.set_property('progress_visible', True)

    @suppress_errors
    def disable_progress(self, *args, **kwargs):
        self.launcher.set_property('progress_visible', False)

    @suppress_errors
    def update_progress(self, *args, **kwargs):
        time_ratio = kwargs.get('time_ratio', 0)
        self.launcher.set_property('progress', time_ratio)

        logger.debug('luncher progress update to %.1f', time_ratio)

    @suppress_errors
    def enable_count(self, *args, **kwargs):
        self.launcher.set_property('count_visible', True)

    @suppress_errors
    def disable_count(self, *args, **kwargs):
        self.launcher.set_property('count_visible', False)

    @suppress_errors
    def update_count(self, *args, **kwargs):
        sessions = kwargs.get('sessions', 0)
        self.launcher.set_property('count', sessions)

        logger.debug('launcher count updated to %d', sessions)
