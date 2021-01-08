import pytest

from docker_devbox_installer.utils.run_as_admin import is_user_admin


@pytest.mark.skipif("os.name != 'nt' ")
def test_is_user_admin_windows():
    assert not is_user_admin()


@pytest.mark.skipif("os.name != 'nt' ")
def test_is_user_admin_posix():
    assert not is_user_admin()
