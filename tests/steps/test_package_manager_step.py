import os
import shutil
from typing import Optional

import pytest

from docker_devbox_installer.steps.packet_manager_step import PacketManagerStepWindows, \
    PacketManagerInstallationException, NotAdminException
from stepbystep import WorkflowModel, StepModel, StepFactory, Workflow, WorkflowRunContext, Step


@pytest.mark.skipif("os.name != 'nt'")
class TestPacketManagerStepWindows:
    @staticmethod
    def get_simple_step() -> PacketManagerStepWindows:
        model = StepModel('packet_manager')
        workflow_model = WorkflowModel(model)

        class EmptyStepFactory(StepFactory):
            def build_step(self, model: StepModel, workflow: Workflow, context: WorkflowRunContext) -> Optional[Step]:
                return None

        workflow = Workflow(workflow_model, EmptyStepFactory())
        workflow_context = WorkflowRunContext()
        step = PacketManagerStepWindows(model, workflow, workflow_context)
        workflow_context.register_step(step)
        return step

    def test_prepare_not_admin(self):
        step = self.get_simple_step()
        try:
            step.prepare()
            assert False
        except NotAdminException:
            assert True

    def test_prepare(self):
        os.environ['INSTALLER_ADMIN_CHECK'] = 'False'
        step = self.get_simple_step()
        step.prepare()
        assert step.context.get('is_installed') == (shutil.which('chocolatey') is not None)

    def test_run_nothing_todo(self, capsys):
        step = self.get_simple_step()
        step.context['is_installed'] = True
        step.run()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) >= 1
        assert lines[0] == '[CHOCOLATEY] Installed by user, nothing to do here'

    def test_run_needs_installation_exception(self, capsys):
        step = self.get_simple_step()
        step.context['is_installed'] = False

        try:
            step.run()
            assert False
        except PacketManagerInstallationException:
            assert True

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) >= 1
        assert lines[0] == '[CHOCOLATEY] Installation'

    @pytest.mark.skip('Must be done once elevation handled')
    def test_run_needs_installation_success(self, capsys):
        """
        TBT when having a solution windows elevation
        :param capsys:
        :return:
        """
        step = self.get_simple_step()
        step.context['is_installed'] = False

        step.run()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) >= 2
        assert lines[0] == '[CHOCOLATEY] Installation'
        assert lines[1] == '[CHOCOLATEY] Installed'

    def test_cleanup_user_installation(self, capsys):
        step = self.get_simple_step()
        step.context['is_installed'] = True
        step.cleanup()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) >= 1
        assert lines[0] == '[CHOCOLATEY] Installed by user, nothing to do here'

    def test_cleanup_success(self, capsys):
        step = self.get_simple_step()
        step.cleanup()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) >= 2
        assert lines[0] == '[CHOCOLATEY] Uninstallation'
        assert lines[1] == '[CHOCOLATEY] Uninstalled'
