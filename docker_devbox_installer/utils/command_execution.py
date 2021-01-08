import shutil
import subprocess
from typing import List, Type, AnyStr


class UnknownCommandException(Exception):
    """
    Raise in case of the command requested is unknown
    """


class CommandExecution:
    @staticmethod
    def execute(command: List[str], exception_class: Type = Exception, elevate: bool = False) -> AnyStr:
        # TODO Handle the elevate
        if shutil.which(command[0]) is None:
            raise UnknownCommandException(f"Command {command[0]} not found")

        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        errors = process.stderr.read()
        if errors:
            raise exception_class(errors)

        return process.stdout.read().decode("utf-8")
