from _pytest.capture import CaptureFixture

from docker_devbox_installer.__main__ import main


def test_main(capsys: CaptureFixture):
    """Should pass on DDB"""

    main()
    outerr = capsys.readouterr()
    assert outerr.out == "Hello World!\n"
