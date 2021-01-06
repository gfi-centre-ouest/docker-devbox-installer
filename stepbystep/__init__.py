"""
Stepbystep
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Dict, Any, Union, Optional, MutableMapping, Iterator


class StepModel:
    """
    A step model. It has a name that should be used by StepFactory to create the right step, and a specific
    configuration.
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self._name = name
        self._config = config if config else {}

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

    def __init__(self, model: StepModel, workflow: 'Workflow', workflow_run_context: 'WorkflowRunContext'):
        self.model = model  # type: StepModel
        self.workflow = workflow  # type: Workflow
        self._workflow_run_context = workflow_run_context  # type: WorkflowRunContext

    @property
    def context(self) -> 'StepRunContext':
        """
        Get the step context.
        :return:
        """
        return self._workflow_run_context.step(self)

    @property
    def workflow_context(self) -> 'WorkflowRunContext':
        """
        Get the workflow context.
        :return:
        """
        return self._workflow_run_context

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
    def build_step(self, model: StepModel, workflow: 'Workflow', context: 'WorkflowRunContext') -> Step:
        """
        Build a step from it's model and the current workflow.
        :param model: StepModel to create from
        :param workflow: current workflow
        :return: fresh Step instance, of None if this factory doesn't support provided StepModel
        """


class BaseRunContext(MutableMapping[str, Any]):  # pylint:disable=too-few-public-methods
    """
    Context base class.
    """

    def __init__(self):
        self._data = dict()

    def __setitem__(self, k: str, v: Any) -> None:
        self._data.__setitem__(k, v)

    def __delitem__(self, v: str) -> None:
        self._data.__delitem__(v)

    def __getitem__(self, k: str) -> Any:
        return self._data.__getitem__(k)

    def __len__(self) -> int:
        return self._data.__len__()

    def __iter__(self) -> Iterator[Any]:
        return self._data.__iter__()


class StepRunContext(BaseRunContext):  # pylint:disable=too-few-public-methods
    """
    Context of a step run.
    """


class WorkflowRunContext(BaseRunContext):
    """
    Context of a workflow run.
    """

    def __init__(self):
        super().__init__()
        self._step_context_by_index = defaultdict(list)
        self._step_context_by_model_name = defaultdict(list)
        self._step_context_by_model = defaultdict(list)
        self._step_context_by_step = defaultdict(list)

    def register_step(self, step: Step) -> StepRunContext:
        """
        Register a step inside this context.
        """
        step_run_context = StepRunContext()
        self._step_context_by_index[len(self._step_context_by_index)].append(step_run_context)
        self._step_context_by_step[step].append(step_run_context)
        self._step_context_by_model_name[step.model.name].append(step_run_context)
        self._step_context_by_model[step.model].append(step_run_context)
        return step_run_context

    def step(self, step: Union[int, str, StepModel, Step],
             solver=lambda contexts: contexts[-1] if contexts else None) -> Optional[StepRunContext]:
        """
        Retrieve a step run context from a StepModel name, StepModel instance, a Step instance or a Step position in
        the workflow.
        :param step: StepModel name, StepModel instance or Step instance to retrieve context from.
        :param solver: lambda function that choose the context to return amoung all contexts matching given step
        parameter.
        :return: The step run context.
        """
        if isinstance(step, int):
            return solver(self._step_context_by_index[step])
        if isinstance(step, str):
            return solver(self._step_context_by_model_name[step])
        if isinstance(step, StepModel):
            return solver(self._step_context_by_model[step])
        if isinstance(step, Step):
            return solver(self._step_context_by_step[step])
        return None

    def steps(self, step: Union[int, str, StepModel, Step]) -> List[StepRunContext]:
        """
        Retrieve step run contexts from a StepModel name, StepModel instance, a Step instance or a Step position in
        the workflow.
        :return: The list of step run context.
        """
        if isinstance(step, int):
            return self._step_context_by_index[step]
        if isinstance(step, str):
            return self._step_context_by_model_name[step]
        if isinstance(step, StepModel):
            return self._step_context_by_model[step]
        if isinstance(step, Step):
            return self._step_context_by_step[step]
        return []


class Workflow:
    """
    Workflow is able to run a defined WorkflowModel, using provided StepFactory.
    """

    def __init__(self, model: WorkflowModel, step_factory: StepFactory):
        self.model = model
        self.step_factory = step_factory

    def run(self):
        """
        Run all steps declared in WorkflowModel.
        """
        steps = []  # type: List[Step]
        context = WorkflowRunContext()
        for step_model in self.model.steps:
            step = self.step_factory.build_step(step_model, self, context)
            context.register_step(step)
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
