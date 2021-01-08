import distro

from docker_devbox_installer.paquet_manager import ChocoPackageManager, get_package_manager, AptPackageManager, \
    OperatingSystemNotHandledException


def test_get_package_manager():
    if distro.id() in ChocoPackageManager.supported_os:
        assert get_package_manager() == ChocoPackageManager
    elif distro.id() in AptPackageManager.supported_os:
        assert get_package_manager() == AptPackageManager
    else:
        try:
            get_package_manager()
            assert False
        except OperatingSystemNotHandledException:
            assert True
