from __future__ import unicode_literals

import logging

import gi

gi.require_version('Unity', '7.0')

from gi.repository import Unity

import tomate.plugin
from tomate.constant import State
from tomate.event import Events, on
from tomate.graph import graph
from tomate.utils import suppress_errors

logger = logging.getLogger(__name__)


class LauncherPlugin(tomate.plugin.Plugin):
    @suppress_errors
    def __init__(self):
        super(LauncherPlugin, self).__init__()

        self.launcher = Unity.LauncherEntry.get_for_desktop_id('tomate-gtk.desktop')
        self.session = graph.get('tomate.session')

    @suppress_errors
    def activate(self):
        super(LauncherPlugin, self).activate()

        if self.session.status()['state'] == State.started:
            self.enable_progress()

        else:
            self.enable_count()
            self.update_count(**self.session.status())

    @suppress_errors
    def deactivate(self):
        super(LauncherPlugin, self).deactivate()

        self.disable_count()
        self.disable_progress()

    @suppress_errors
    @on(Events['Session'], [State.started])
    def on_session_started(self, *args, **kwargs):
        self.disable_count()
        self.enable_progress()

    @suppress_errors
    @on(Events['Session'], [State.finished, State.stopped])
    def on_session_ended(self, *args, **kwargs):
        self.disable_progress()
        self.enable_count()
        self.update_count(**kwargs)

    def enable_progress(self):
        self.launcher.set_property('progress', 0)
        self.launcher.set_property('progress_visible', True)

    def disable_progress(self):
        self.launcher.set_property('progress_visible', False)

    @suppress_errors
    @on(Events['Timer'], [State.changed])
    def update_progress(self, *args, **kwargs):
        time_ratio = kwargs.get('time_ratio', 0)
        self.launcher.set_property('progress', time_ratio)

        logger.debug('luncher progress update to %.1f', time_ratio)

    def enable_count(self):
        self.launcher.set_property('count_visible', True)

    def disable_count(self):
        self.launcher.set_property('count_visible', False)

    @suppress_errors
    @on(Events['Session'], [State.reset])
    def update_count(self, *args, **kwargs):
        sessions = kwargs.get('sessions', 0)
        self.launcher.set_property('count', sessions)

        logger.debug('launcher count updated to %d', sessions)
