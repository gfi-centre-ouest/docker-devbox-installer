import os
import subprocess
import shutil

import stepbystep
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


class PacketManagerStepWindows(stepbystep.Step):
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
        output, errors = self._execute_powershell("; ".join(chocolatey_install_command))
        if errors:
            raise PacketManagerInstallationException(errors)

        print("[CHOCOLATEY] Installed")

    def cleanup(self):
        if self.context.get('is_installed'):
            print("[CHOCOLATEY] Installed by user, nothing to do here")
            return
        print("[CHOCOLATEY] Uninstallation")
        # TODO Handle uninstall
        print("[CHOCOLATEY] Uninstalled")

    @staticmethod
    def _execute_powershell(command: str):
        # TODO Find a way to elevate access
        process = subprocess.Popen(['powershell.exe', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        errors = process.stderr.read()
        output = process.stdout.read()

        return [output, errors]
