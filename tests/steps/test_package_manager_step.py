import os
import shutil
from typing import Optional

import pytest

from docker_devbox_installer.steps.package_manager_step import PackageManagerWindowsStep, \
    NotAdminException, PowershellException
from stepbystep import WorkflowModel, StepModel, StepFactory, Workflow, WorkflowRunContext, Step


@pytest.mark.skipif("os.name != 'nt'")
class TestPackageManagerWindowsStep:
    @staticmethod
    def get_simple_step() -> PackageManagerWindowsStep:
        model = StepModel('package_manager')
        workflow_model = WorkflowModel(model)

        class EmptyStepFactory(StepFactory):
            def build_step(self, model: StepModel, workflow: Workflow, context: WorkflowRunContext) -> Optional[Step]:
                return None

        workflow = Workflow(workflow_model, EmptyStepFactory())
        workflow_context = WorkflowRunContext()
        step = PackageManagerWindowsStep(model, workflow, workflow_context)
        workflow_context.register_step(step)
        return step

    def test_prepare(self):
        os.environ['INSTALLER_ADMIN_CHECK'] = 'False'
        step = self.get_simple_step()
        step.prepare()
        assert step.context.get('is_installed') == bool(shutil.which('chocolatey'))

    def test_run_nothing_todo(self, capsys):
        step = self.get_simple_step()
        step.context['is_installed'] = True
        step.run()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) == 2
        assert lines[0] == '[CHOCOLATEY] Installed by user, nothing to do here'

    def test_run(self, capsys):
        """
        TBT when having a solution windows elevation
        :param capsys:
        :return:
        """
        if bool(shutil.which('choco')):
            assert True
            return
        step = self.get_simple_step()
        step.context['is_installed'] = False

        step.run()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) >= 2
        assert lines[0] == '[CHOCOLATEY] Installation'
        assert lines[1] == '[CHOCOLATEY] Installed'
