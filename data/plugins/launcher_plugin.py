from __future__ import unicode_literals

import logging

from gi.repository import Unity
from tomate.enums import State
from tomate.graph import graph
from tomate.plugin import Plugin
from tomate.utils import suppress_errors

logger = logging.getLogger(__name__)


class LauncherPlugin(Plugin):

    subscriptions = (
        ('session_ended', 'on_session_ended'),
        ('session_interrupted', 'on_session_ended'),
        ('session_started', 'on_session_started'),
        ('timer_updated', 'update_progress'),
        ('sessions_reseted', 'update_count'),
    )

    @suppress_errors
    def __init__(self):
        super(LauncherPlugin, self).__init__()

        self.launcher = Unity.LauncherEntry.get_for_desktop_id('tomate-gtk.desktop')
        self.session = graph.get('tomate.session')

    @suppress_errors
    def activate(self):
        super(LauncherPlugin, self).activate()

        if self.session.status()['state'] == State.running:
            self.enable_progress()

        else:
            self.enable_count()
            self.update_count(**self.session.status())

    @suppress_errors
    def deactivate(self):
        super(LauncherPlugin, self).deactivate()

        self.disable_count()
        self.disable_progress()

    def on_session_started(self, *args, **kwargs):
        self.disable_count()
        self.enable_progress()

    def on_session_ended(self, *args, **kwargs):
        self.disable_progress()
        self.enable_count()
        self.update_count(**kwargs)

    def enable_progress(self):
        self.launcher.set_property('progress', 0)
        self.launcher.set_property('progress_visible', True)

    def disable_progress(self):
        self.launcher.set_property('progress_visible', False)

    def update_progress(self, **kwargs):
        time_ratio = kwargs.get('time_ratio', 0)
        self.launcher.set_property('progress', time_ratio)

        logger.debug('luncher progress update to %.1f', time_ratio)

    def enable_count(self):
        self.launcher.set_property('count_visible', True)

    def disable_count(self):
        self.launcher.set_property('count_visible', False)

    def update_count(self, **kwargs):
        sessions = kwargs.get('sessions', 0)
        self.launcher.set_property('count', sessions)

        logger.debug('launcher count updated to %d', sessions)
