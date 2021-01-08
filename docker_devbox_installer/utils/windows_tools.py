import ctypes
import sys


def is_admin() -> bool:
    """
    Check if current script is run in an admin shell
    :return: True if current script is run as admin, otherwise False
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin() -> None:
    """
    Force execution of current script as admin
    """
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
