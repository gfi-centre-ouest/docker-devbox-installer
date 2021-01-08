from abc import ABC, abstractmethod
from typing import AnyStr, Optional, Type, List

import distro

from docker_devbox_installer.utils.command_execution import CommandExecution


class OperatingSystemNotHandledException(Exception):
    """
    Raised in case of choco error
    """


class PacketInstallationException(Exception):
    """
    Raised in case of choco error
    """


class PacketUninstallationException(Exception):
    """
    Raised in case of choco error
    """


class AbstractPackageManager(ABC):
    """
    Methods to be declare in packet manager
    """
    supported_os: List[str]

    @classmethod
    def support_os(cls, os_name: str) -> bool:
        """
        Get the supporter operating system
        :param os_name: The name of the os to check
        :return:
        """
        return os_name in cls.supported_os

    @staticmethod
    @abstractmethod
    def install(name: str):
        """
        Install the Required Software
        :return:
        """

    @staticmethod
    @abstractmethod
    def uninstall(name: str):
        """
        Uninstall the Required Software
        :return:
        """


class ChocoPackageManager(AbstractPackageManager):
    """
    Choco paquet manager
    """
    supported_os: List[str] = ['windows_nt']

    @staticmethod
    def install(name: str) -> AnyStr:
        return CommandExecution.execute(['choco', 'install', '--confirm', name],
                                        exception_class=PacketInstallationException)

    @staticmethod
    def uninstall(name: str) -> AnyStr:
        return CommandExecution.execute(['choco', 'uninstall', name],
                                        exception_class=PacketUninstallationException)


class AptPackageManager(AbstractPackageManager):
    """
    Choco paquet manager
    """
    supported_os: List[str] = ["debian", "ubuntu"]

    @staticmethod
    def install(name: str) -> AnyStr:
        return CommandExecution.execute(['apt-get', 'install', '--no-install-recommends', '-y', name],
                                        exception_class=PacketInstallationException)

    @staticmethod
    def uninstall(name: str) -> AnyStr:
        return CommandExecution.execute(['apt-get', 'remove', '-y', '--purge', name],
                                        exception_class=PacketUninstallationException)


def get_package_manager() -> Optional[Type[AbstractPackageManager]]:
    """
    Get the appropriate packet manager
    :return:
    """
    for manager in [ChocoPackageManager]:
        if manager.support_os(distro.id()):
            return manager

    raise OperatingSystemNotHandledException('Operating System {distro.id()} not yet handled')
