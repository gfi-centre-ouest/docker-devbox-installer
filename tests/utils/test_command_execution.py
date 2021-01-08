import distro

from docker_devbox_installer.utils.command_execution import CommandExecution, UnknownCommandException


class DummyException(Exception):
    """
    A dummy exception
    """


class TestCommandExecution:

    def test_execute_exception(self):
        try:
            CommandExecution.execute(['TOTO'])
            assert False
        except UnknownCommandException:
            assert True

    def test_execute_hello_world(self):
        output = CommandExecution.execute(['echo', '"Hello World"'])
        lines = output.split('\n')
        assert len(lines) >= 1
        assert lines[0] == '"Hello World"'

    def test_execute_exception_class(self):
        try:
            if distro.id() == 'windows_nt':
                CommandExecution.execute(['rmdir'], exception_class=DummyException)
            else:
                CommandExecution.execute(['echo', '$(unknowncommand)'], exception_class=DummyException)
            assert False
        except DummyException:
            assert True

    def test_execute_with_elevation(self):
        output = CommandExecution.execute(['echo', '"Hello World"'], elevate=True)
        lines = output.split('\n')
        assert len(lines) >= 1
        assert lines[0] == '"Hello World"'
