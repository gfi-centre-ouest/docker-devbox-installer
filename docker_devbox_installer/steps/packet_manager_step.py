import os
import shutil
import subprocess

import stepbystep
from docker_devbox_installer.utils.command_execution import CommandExecution
from docker_devbox_installer.utils.windows_tools import is_admin

packet_manager_step_model: stepbystep.StepModel = stepbystep.StepModel('packet_manager')


class PacketManagerInstallationException(Exception):
    """
    Raised if installation of packet manager return an error
    """


class NotAdminException(Exception):
    """
    Raised if current user is not admin
    """


class PowershellException(Exception):
    """
    Raised in case of powershell error
    """


class PacketManagerWindowsStep(stepbystep.Step):
    """
    Install the packet manager
    """

    def prepare(self):
        self.context['is_installed'] = (shutil.which('chocolatey') is not None)
        if os.environ.get('INSTALLER_ADMIN_CHECK') != 'False' and not is_admin():  # Patch for pytest, TBR
            raise NotAdminException('You need to run this software as administrator')

    def run(self):
        if self.context.get('is_installed'):
            print("[CHOCOLATEY] Installed by user, nothing to do here")
            return
        print("[CHOCOLATEY] Installation")

        chocolatey_install_command = [
            "Set-ExecutionPolicy Bypass -Scope Process -Force",
            "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072",
            "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
        ]
        self._execute_powershell("; ".join(chocolatey_install_command))

        print("[CHOCOLATEY] Installed")

    @staticmethod
    def _execute_powershell(command: str):
        return CommandExecution.execute(['powershell.exe', command], exception_class=PowershellException)
