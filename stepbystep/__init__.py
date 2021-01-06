"""
Stepbystep
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class StepModel:
    """
    A step model. It has a name that should be used by StepFactory to create the right step, and a specific
    configuration.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        self._name = name
        self._config = config

    @property
    def name(self) -> str:
        """
        Name for this step model.
        """
        return self._name

    @property
    def config(self) -> Dict[str, Any]:
        """
        Configuration for this step model.
        """
        return self._config


class WorkflowModel:
    """
    A model of workflow. It is composed of a list of StepModel instances.
    """

    def __init__(self, *steps: StepModel):
        self._steps = list(steps)

    @property
    def steps(self) -> List[StepModel]:
        """
        List of steps that constitute this workflow model.
        :return:
        """
        return self._steps


class Step(ABC):
    """
    Base class to implement a step.
    """

    def __init__(self, model: StepModel, workflow: 'Workflow'):
        self.model = model  # type: StepModel
        self.workflow = workflow  # type: Workflow

    def prepare(self):
        """
        Initial prepare task. Perform any automated operation before prompting the user.
        """

    def prompt(self):
        """
        Initial user prompt. Prompt the user for additional data that could be used by the run.
        """

    def prepare_before_run(self):
        """
        Prepare just before run. Perform any automated operation before prompting the user.
        """

    def prompt_before_run(self):
        """
        Prompt user just before run. Prompt the user for additional data that could be used by the run.
        """

    @abstractmethod
    def run(self):
        """
        Main run. It should actually perform the task described by the step model.
        """

    def prompt_after_run(self):
        """
        Prompt user just after run.
        """

    def cleanup_after_run(self):
        """
        Perform cleanup operations just after run.
        """

    def cleanup(self):
        """
        Final cleanup.
        """


class StepFactory(ABC):
    """
    Step factory can create Step implementations for each supported StepModel.
    """

    @abstractmethod
    def build_step(self, model: StepModel, workflow: 'Workflow') -> Step:
        """
        Build a step from it's model and the current workflow.
        :param model: StepModel to create from
        :param workflow: current workflow
        :return: fresh Step instance, of None if this factory doesn't support provided StepModel
        """


class Workflow:
    """
    Workflow is able to run a defined WorkflowModel, using provided StepFactory.
    """

    def __init__(self, model: WorkflowModel, step_factory: StepFactory):
        self.model = model
        self.context = {}  # type: Dict[str, Any]
        self.step_factory = step_factory

    def run(self):
        """
        Run all steps declared in WorkflowModel.
        """
        steps = []  # type: List[Step]
        for step_model in self.model.steps:
            step = self.step_factory.build_step(step_model, self)
            steps.append(step)

        for step in steps:
            step.prepare()

        for step in steps:
            step.prompt()

        for step in steps:
            step.prepare_before_run()
            step.prompt_before_run()
            step.run()
            step.prompt_after_run()
            step.cleanup_after_run()

        for step in steps:
            step.cleanup()
