# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import datetime
import os
import shutil
import sys
import xml.etree.ElementTree as ET
import deploy_config


def log(s, is_error=False):
    file = sys.stderr if is_error else sys.stdout
    prefix = datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ')
    print('[{0}] {1}'.format(prefix, s), file=file)


class Deploy(object):
    def run(self):
        self.check_nodejs()
        self.check_variables()
        self.do_deployment()
        self.copy_web_config()
        self.post_python_deployment()

    def check_nodejs(self):
        if int(os.system('where node')) != 0:
            self.goto_error('Missing node.js executable, plaease install node.js, if already installed make sure it can be reached from current environment.')

    def check_variables(self):
        log('check variables ...')

        self.deploy_src_path = self.get_deploy_src_path()
        self.deploy_path = self.get_deploy_path()

        self.python_version = deploy_config.PYTHON_VERSION
        self.python_runtime = 'python-%s' % self.python_version
        self.python_path = deploy_config.PYTHON_PATH
        self.python_env_module = deploy_config.PYTHON_ENV_MODULE

        self.virtualenv_path = self.get_deploy_path('env')
        self.python_runtime_mark_path = os.path.join(self.virtualenv_path, self._('azure.env.{python_runtime}.txt'))

        self.requirements_path = self.get_deploy_path('requirements.txt')
        self.requirements_name = os.path.basename(self.requirements_path)

        self.config_src_path = self.get_deploy_src_path(self._('web.{python_version}.config'))
        self.config_dst_path = self.get_deploy_path('web.config')

        self.next_manifest_path = os.environ.get('NEXT_MANIFEST_PATH', None)
        self.prev_manifest_path = os.environ.get('PREVIOUS_MANIFEST_PATH', None)
        if self.next_manifest_path is None:
            self.next_manifest_path = self.current('..', 'artifacts', 'manifest')
            if self.prev_manifest_path is None:
                self.prev_manifest_path = self.current('..', 'artifacts', 'manifest')

        # https://github.com/projectkudu/kudu/wiki/Post-Deployment-Action-Hooks
        self.post_deployment_action = os.environ.get('POST_DEPLOYMENT_ACTION', None)


    def do_deployment(self):
        log('Handling python deployment.')
        kudu_sync_cmd = os.environ.get('KUDU_SYNC_CMD', None)
        if kudu_sync_cmd is None:
            log('Installing Kudu Sync')
            self.run_cmd('npm install kudusync -g --silent')
            # Locally just running "kuduSync" would also work
            kudu_sync_cmd = os.path.join(os.environ['appdata'], 'npm', 'kuduSync.cmd')

        self.run_cmd(
            '{kudu_sync_cmd} --verbose=300 '
            '--from="{deploy_src_path}" --to="{deploy_path}" '
            '--nextManifest="{next_manifest_path}" --previousManifest="{prev_manifest_path}" '
            '--ignore=".git;.hg;.deployment;deploy.cmd;deploy.py"', kudu_sync_cmd=kudu_sync_cmd)

        if not os.path.exists(self.requirements_path):
            self.goto_error('Missing {}'.format(self.requirements_name))
        else:
            log('create virtual environment ...')

            if os.path.exists(self.python_runtime_mark_path):
                log('Found compatible virtual environment.')
            else:
                if os.path.exists(self.virtualenv_path):
                    log('Deleting incompatible virtual environment.')
                    shutil.rmtree(self.virtualenv_path)

                log(self._('Creating {python_runtime} virtual environment.'))

                self.run_cmd('{python_path} -m {python_env_module} env --without-pip')

                open(self.python_runtime_mark_path, 'wb').truncate()

                log('Pip reinstall')
                pip_url = 'https://bootstrap.pypa.io/get-pip.py'
                self.run_cmd('curl "{}" | env\scripts\python"'.format(pip_url))

            log('Pip install requirements.')
            self.run_cmd('env\scripts\pip install --verbose -r "{requirements_path}"')

    def copy_web_config(self):
        log('copy web.config ...')
        if os.path.exists(self.config_src_path):
            log(self._('Overwriting web.config with web.{python_version}.config'))
            shutil.copyfile(self.config_src_path, self.config_dst_path)

    def post_python_deployment(self):
        if self.post_deployment_action:
            self.run_cmd(self.post_deployment_action)
        sys.exit(0)

    def run_cmd(self, cmd, fail_message=None, ignore_error=False, **kwargs):
        os.chdir(self.deploy_path)
        cmd = self._(cmd, **kwargs)
        log(cmd)
        if int(os.system(cmd)) != 0:
            if fail_message:
                log(fail_message, is_error=True)
            if not ignore_error:
                self.goto_error()

    def goto_error(self, message=None):
        if message:
            log(message, is_error=True)
        sys.exit(1)

    def _(self, s, **kwargs):
        kwargs.update(self.__dict__)
        return s.format(**kwargs)

    def current(self, *args):
        current_dir_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(current_dir_path, *args)

    def get_deploy_src_path(self, *args):
        deployment_source = os.environ.get('DEPLOYMENT_SOURCE', self.current())
        return os.path.join(deployment_source, *args)

    def get_deploy_path(self, *args):
        deployment_target = os.environ.get('DEPLOYMENT_TARGET', self.current('..', 'artifacts', 'wwwroot'))
        return os.path.join(deployment_target, *args)


if __name__ == '__main__':
    Deploy().run()

