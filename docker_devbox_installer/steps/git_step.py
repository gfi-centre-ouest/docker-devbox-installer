import shutil
import subprocess
from typing import Optional, AnyStr

import questionary

import stepbystep
from docker_devbox_installer.paquet_manager import get_package_manager
from docker_devbox_installer.utils.command_execution import CommandExecution

git_install_and_configure_step_model: stepbystep.StepModel = stepbystep.StepModel('git_install_and_configure')


class GitException(Exception):
    """
    In case of exception on git command execution
    """


class GitInstallAndConfigureStep(stepbystep.Step):

    def prepare(self):
        self.context['is_installed'] = (shutil.which('git') is not None)
        self.context['user.name'] = self.get_user_name()
        self.context['user.email'] = self.get_user_email()

    def prompt(self):
        while self.context.get('user.name') is None or self.context.get('user.name') == '':
            self.context['user.name'] = questionary.text("What GIT user.name you want to set?").ask()

        while self.context.get('user.email') is None or self.context.get('user.email') == '':
            self.context['user.email'] = questionary.text("What GIT user.email you want to set?").ask()

    def run(self):
        if self.context.get('is_installed'):
            print("[Git Install and Configure] Installed by user, nothing to do here")
        else:
            print("[Git Install and Configure] Installation")
            package_manager = get_package_manager()
            package_manager.install('git')
            print("[Git Install and Configure] Installed")

        print("[Git Install and Configure] Configuration")
        if self.context.get('user.name') is not None and self.context.get('user.name') != '':
            self.update_config('user.name', self.context.get('user.name'))

        if self.context.get('user.email') is not None and self.context.get('user.email') != '':
            self.update_config('user.email', self.context.get('user.email'))

        self.update_config('core.autocrlf', 'false')
        self.update_config('core.filemode', 'false')
        self.update_config('core.eol', 'lf')

        print("[Git Install and Configure] Configured")

    @staticmethod
    def get_user_name() -> Optional[AnyStr]:
        if not shutil.which('git'):
            return None

        return CommandExecution.execute(['git', 'config', '--global', 'user.name'], GitException)

    @staticmethod
    def get_user_email() -> Optional[AnyStr]:
        if not shutil.which('git'):
            return None

        return CommandExecution.execute(['git', 'config', '--global', 'user.email'], GitException)

    @staticmethod
    def update_config(key: str, value: str, is_global: bool = True) -> Optional[AnyStr]:
        """
        Update git configuration
        :param key: the key to update
        :param value: the value to set
        :param is_global: add the --global flag in command
        :return:
        """
        print(f"[Git Install and Configure] Setting {key} to {value}")
        if not shutil.which('git'):
            return None

        command = ['git', 'config']
        if is_global:
            command.append('--global')
        command.append(key)
        command.append(value)

        return CommandExecution.execute(command, GitException)
