#!/bin/env python
import os

from paver.easy import needs, path, sh
from paver.setuputils import install_distutils_tasks
from paver.tasks import task

install_distutils_tasks()

ROOT_PATH = path(__file__).dirname().abspath()

PLUGIN_PATH = ROOT_PATH / 'data' / 'plugins'

TOMATE_PATH = ROOT_PATH / 'tomate'


@needs(['test'])
@task
def default():
    pass


@task
@needs(['clean'])
def test(options):
    os.environ['PYTHONPATH'] = '%s:%s' % (TOMATE_PATH, PLUGIN_PATH)
    sh('nosetests --cover-erase --with-coverage tests.py')


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
