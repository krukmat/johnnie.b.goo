import os
from functools import wraps
from contextlib import contextmanager, nested

from fabric.api import (
    cd, run as _run, task, env, hide, sudo as _sudo
)
from fabric.colors import red, green, blue, yellow
from fabric.operations import require as require_env, open_shell
from fabric.contrib.files import exists
import fabtools

__author__ = 'matiasleandrokruk'

################
# Config setup #
################


env.project_name = 'jbg'

# env.user = env.project_name
env.password = 'qwerty123'
env.db_user = env.project_name
env.db_name = env.project_name
env.db_password = env.project_name
env.db_host = '127.0.0.1'
env.db_test_name = env.db_name + '_test'

env.debian_packages = "debian_packages.txt"

env.git_url = 'ssh://krukmat@github.com/krukmat/johnnie.b.goo.git'

env.python = 'python'
env.virtualenv_path = 'venv'
env.nodeenv_path = os.path.join('~', 'nenv')
env.project_path = os.path.join('~', env.project_name)

env.django_static_url = '/static/'
env.django_static_root = os.path.join(env.project_path, 'static/')
env.cdn_static_root = os.path.join(env.project_path, 'dummy/cdn/')
env.user_site_static_root = os.path.join(env.project_path, 'dummy/usersite/')

env.config_file = '__init__.py'
env.local_config_file = 'local.py'

env.frontend_ip = '0.0.0.0'

env.ruby_version = '2.0.0'


def environment(func):
    @wraps(func)
    def update_env(*args, **kawrgs):
        env['is_%s' % func.__name__] = True
        return func(*args, **kawrgs)
    return update_env

@task
@environment
def production():
    """[ENV]"""
    env.hosts = ['54.164.56.152']
    env.django_settings = 'webserver.settings.prod'

@task
@environment
def vagrant(name=''):
    """[ENV]"""
    from fabtools.vagrant import vagrant as _vagrant
    _vagrant(name)
    env.project_user = 'vagrant'


def _print(output):
    print os.linesep, output, os.linesep


def print_command(command):
    _print(blue("$ ", bold=True) +
           yellow(command, bold=True) +
           red(" ->", bold=True))

@task
def run(command, show=True, args=("running",), quiet=False, shell=True):
    """Runs a shell comand on the remote server."""

    if show:
        print_command(command)
    else:
        args += ('stdout',)

    with hide(*args):
        return _run(command, quiet=quiet, shell=True)

@task
def sudo(command, show=True, shell_escape=None, shell=True):
    """Runs a command as sudo on the remote server."""
    if show:
        print_command(command)
    with hide("running"):
        return _sudo(command, shell_escape=shell_escape, shell=shell)

@task
def install_virtualenv():
    """
    Create a new virtual environment for a project.
    """

    require_env('virtualenv_path', 'project_path')

    # Replaces fabtools version since ther is some bug with pip install script
    # looks like curl fails on redirect.
    fabtools.deb.install('python-pip')
#     fabtools.python.install_pip()

    fabtools.python.install('virtualenv', use_sudo=True)

    if exists(env.virtualenv_path):
        run('rm -r %s' % env.virtualenv_path)

    # Create virtualenv
    run('virtualenv --no-site-packages -p %s --distribute %s' %
        (env.python, env.virtualenv_path))

    if not exists('~/activate'):
        run('ln -s %s/bin/activate ~/activate' % env.virtualenv_path)

        with cd(env.virtualenv_path):
            append_extract = 'export PYTHONPATH=%s' % env.project_path
            sudo('echo "%s" >> bin/activate' % append_extract)

    # Make shortcut
    sudo('ln -sf %s %s' % (env.virtualenv_path, os.path.join(env.project_path, 'venv')))

    _print(green('virtualenv installed'))

    # Make shortcut
    sudo('ln -sf %s %s' % (env.virtualenv_path, os.path.join(env.project_path, 'venv')))


@task
def install_git_repository(branch=None):
    require_env('project_path', 'git_url')

    if not exists(env.project_path):
        if env.get('is_vagrant') and exists('/vagrant'):
            run('ln -s /vagrant %s' % env.project_path)
        else:
            # not tested on testing/staging
            fabtools.require.directory(env.project_path)
            fabtools.git.clone(env.git_url, path=env.project_path)

    if branch:
        fabtools.git.checkout(env.project_path, branch=branch)

@contextmanager
def project():
    """Runs commands within the project's directory."""
    require_env('project_path', 'virtualenv_path')

    with fabtools.python.virtualenv(env.virtualenv_path):
        with cd(env.project_path):
            yield

@task
def install_python_modules():
    with project():
        fabtools.python.install_requirements('requirements.txt')


@task
def install_debian_packages():

    require_env('debian_packages')
    fabtools.deb.update_index()

    filename = os.path.join(os.path.dirname(__file__),
                            env.debian_packages)

    with open(filename, 'r') as file_:
        packages = [line.strip() for line in file_]

    fabtools.deb.install(packages)
    fabtools.deb.upgrade()

@task
def install_echo_point():
    # git clone -b release-4.12 git://github.com/echonest/echoprint-codegen.git
    run("git clone -q -b release-4.12 git://github.com/echonest/echoprint-codegen.git", quiet=True)
    # cd echoprint-codegen/src
    with cd('echoprint-codegen/src'):
        run('make')


@task
def install():
    run('sudo add-apt-repository ppa:mc3man/trusty-media')
    run('sudo apt-get update')
    install_git_repository()
    install_virtualenv()
    install_debian_packages()
    install_echo_point()
    install_python_modules()

@task
def update():
    install_debian_packages()
    install_virtualenv()
    install_python_modules()