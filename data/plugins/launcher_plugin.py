from __future__ import unicode_literals

import logging

from gi.repository import Unity
from tomate.plugin import TomatePlugin
from tomate.utils import suppress_errors

logger = logging.getLogger(__name__)


class LauncherPlugin(TomatePlugin):

    signals = (
        ('session_ended', 'show_counter'),
        ('session_interrupted', 'show_counter'),
        ('session_started', 'on_session_started'),
        ('sessions_reseted', 'show_counter'),
        ('timer_updated', 'on_timer_updated'),
    )

    def on_init(self):
        self.launcher = Unity.LauncherEntry.get_for_desktop_id('tomate-gtk.desktop')

    def on_deactivate(self):
        self.launcher.set_property('progress_visible', False)
        self.launcher.set_property('count_visible', False)

    @suppress_errors
    def on_session_started(self, sender=None, **kwargs):
        self.launcher.set_property('progress', 0)
        self.launcher.set_property('progress_visible', True)

        self.launcher.set_property('count_visible', False)

    @suppress_errors
    def on_timer_updated(self, sender=None, **kwargs):
        time_ratio = kwargs.get('time_ratio', 0)
        self.launcher.set_property('progress', time_ratio)

        logger.debug('Launcher progress %.1f', time_ratio)

    @suppress_errors
    def show_counter(self, sender=None, **kwargs):
        self.launcher.set_property('progress_visible', False)

        sessions = kwargs.get('sessions', 0)
        self.launcher.set_property('count_visible', True)
        self.launcher.set_property('count', sessions)

        logger.debug('Show launcher counter %d', sessions)
