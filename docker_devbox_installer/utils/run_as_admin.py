import os
from typing import List


def is_user_admin():
    if os.name == 'nt':
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    elif os.name == 'posix':
        return os.getuid() == 0
    else:
        raise RuntimeError(f"Unsupported operating system for this module: {os.name}")


def run_as_admin(cmd_line: List[str] = None, wait: bool = True):
    if os.name != 'nt':
        raise RuntimeError("This function is only implemented on Windows.")

    import win32con
    import win32event
    import win32process
    from win32comext.shell.shell import ShellExecuteEx
    from win32comext.shell import shellcon

    cmd = f'"{(cmd_line[0],)}"'
    params = " ".join([f'"{x}"' for x in cmd_line[1:]])
    showCmd = win32con.SW_SHOWNORMAL
    lp_verb = 'runas'  # causes UAC elevation prompt.

    procInfo = ShellExecuteEx(nShow=showCmd,
                              fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                              lpVerb=lp_verb,
                              lpFile=cmd,
                              lpParameters=params)

    if wait:
        procHandle = procInfo['hProcess']
        obj = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(procHandle)
    else:
        rc = None

    return rc
