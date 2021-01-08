import shutil
from typing import Optional

import pytest

from docker_devbox_installer.steps.git_step import GitInstallAndConfigureStep
from stepbystep import WorkflowModel, StepModel, StepFactory, Workflow, WorkflowRunContext, Step


class TestGitInstallAndConfigureStep:
    @staticmethod
    def get_simple_step() -> GitInstallAndConfigureStep:
        model = StepModel('git_install_and_config')
        workflow_model = WorkflowModel(model)

        class EmptyStepFactory(StepFactory):
            def build_step(self, model: StepModel, workflow: Workflow, context: WorkflowRunContext) -> Optional[Step]:
                return None

        workflow = Workflow(workflow_model, EmptyStepFactory())
        workflow_context = WorkflowRunContext()
        step = GitInstallAndConfigureStep(model, workflow, workflow_context)
        workflow_context.register_step(step)
        return step

    def test_prepare_not_admin(self):
        step = self.get_simple_step()
        step.prepare()

        assert step.context.get('is_installed') == bool(shutil.which('git'))
        assert step.context.get('user.name') == GitInstallAndConfigureStep.get_config('user.name')
        assert step.context.get('user.email') == GitInstallAndConfigureStep.get_config('user.email')

    def test_prompt_already_complete(self, capsys):
        step = self.get_simple_step()
        step.context['user.name'] = 'Dummy User'
        step.context['user.email'] = 'dummy@user.mail'
        step.prompt()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) == 1

    @pytest.mark.skip('TODO when found a test solution for questionary')
    def test_prompt(self, capsys):
        step = self.get_simple_step()
        step.prompt()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) == 1

    def test_run_already_installed(self, capsys):
        step = self.get_simple_step()
        step.context['is_installed'] = True
        step.run()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) == 7
        assert lines[0] == '[Git Install and Configure] Installed by user, nothing to do here'
        assert lines[1] == '[Git Install and Configure] Configuration'
        assert lines[2] == '[Git Install and Configure] Setting core.autocrlf to false'
        assert lines[3] == '[Git Install and Configure] Setting core.filemode to false'
        assert lines[4] == '[Git Install and Configure] Setting core.eol to lf'
        assert lines[5] == '[Git Install and Configure] Configured'

    @pytest.mark.skipif("os.name != 'nt' ")
    @pytest.mark.depends(on=['tests/steps/test_package_manager_step.py::TestPackageManagerWindowsStep::test_run'])
    def test_run_windows(self, capsys):
        if bool(shutil.which('git')):
            assert True
            return
        step = self.get_simple_step()
        step.context['is_installed'] = False
        step.context['user.name'] = 'Dummy User'
        step.context['user.email'] = 'dummy@user.mail'
        step.run()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) == 10
        assert lines[0] == '[Git Install and Configure] Installation'
        assert lines[1] == '[Git Install and Configure] Installed'
        assert lines[2] == '[Git Install and Configure] Configuration'
        assert lines[3] == '[Git Install and Configure] Setting user.name to dummy@user.name'
        assert lines[4] == '[Git Install and Configure] Setting user.email to dummy@user.mail'
        assert lines[5] == '[Git Install and Configure] Setting core.autocrlf to false'
        assert lines[6] == '[Git Install and Configure] Setting core.filemode to false'
        assert lines[7] == '[Git Install and Configure] Setting core.eol to lf'
        assert lines[8] == '[Git Install and Configure] Configured'

        assert GitInstallAndConfigureStep.get_config('user.name') == step.context['user.name']
        assert GitInstallAndConfigureStep.get_config('user.email') == step.context['user.email']

    @pytest.mark.skipif("os.name == 'nt'")
    def test_run_others(self, capsys):
        if bool(shutil.which('git')):
            assert True
            return

        step = self.get_simple_step()
        step.context['is_installed'] = False
        step.context['user.name'] = 'Dummy User'
        step.context['user.email'] = 'dummy@user.mail'
        step.run()

        captured = capsys.readouterr()
        lines = captured.out.split('\n')
        assert len(lines) == 10
        assert lines[0] == '[Git Install and Configure] Installation'
        assert lines[1] == '[Git Install and Configure] Installed'
        assert lines[2] == '[Git Install and Configure] Configuration'
        assert lines[3] == '[Git Install and Configure] Setting user.name to dummy@user.name'
        assert lines[4] == '[Git Install and Configure] Setting user.email to dummy@user.mail'
        assert lines[5] == '[Git Install and Configure] Setting core.autocrlf to false'
        assert lines[6] == '[Git Install and Configure] Setting core.filemode to false'
        assert lines[7] == '[Git Install and Configure] Setting core.eol to lf'
        assert lines[8] == '[Git Install and Configure] Configured'

        assert GitInstallAndConfigureStep.get_config('user.name') == step.context['user.name']
        assert GitInstallAndConfigureStep.get_config('user.email') == step.context['user.email']
