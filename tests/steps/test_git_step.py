import os
import shutil
from typing import Optional

import pytest

from docker_devbox_installer.steps.packet_manager_step import PacketManagerWindowsStep, \
    PacketManagerInstallationException, NotAdminException
from stepbystep import WorkflowModel, StepModel, StepFactory, Workflow, WorkflowRunContext, Step


class TestPacketManagerWindowsStep:
    """
    WIP
    """