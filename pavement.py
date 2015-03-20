#!/bin/env python
import os
from optparse import Option

from paver.easy import cmdopts, needs, path, sh
from paver.tasks import task

ROOT_PATH = path(__file__).dirname().abspath()

PLUGIN_PATH = ROOT_PATH / 'data' / 'plugins'

TOMATE_PATH = ROOT_PATH / 'tomate'


@needs(['test'])
@task
def default():
    pass


@task
@needs(['clean'])
@cmdopts([
    Option('-v', '--verbosity', default=1, type=int),
])
def test(options):
    os.environ['PYTHONPATH'] = '%s:%s' % (TOMATE_PATH, PLUGIN_PATH)
    sh('nosetests --cover-erase --with-coverage --verbosity=%s tests.py' % options.test.verbosity)


@task
def clean():
    sh('pyclean data/plugin')
    sh('pyclean .')
    sh('rm -f .coverage', ignore_error=True)


@task
@needs(['docker_rmi', 'docker_build', 'docker_run'])
def docker_test():
    pass


@task
def docker_rmi():
    sh('docker rmi eliostvs/tomate-launcher-plugin', ignore_error=True)


@task
def docker_build():
    sh('docker build -t eliostvs/tomate-launcher-plugin .')


@task
def docker_run():
    sh('docker run --rm -v $PWD:/code eliostvs/tomate-launcher-plugin')
