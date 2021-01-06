from stepbystep import Workflow, StepFactory, StepModel, Step, WorkflowModel, WorkflowRunContext, BaseRunContext
from stepbystep.steps import NoopStep


def test_dummy_workflow():
    dummy1_called_config = None
    dummy2_called_config = None

    dummy1_step_model = StepModel('dummy1', {'foo': 'bar1'})
    dummy2_step_model = StepModel('dummy2', {'foo': 'bar2'})

    class Dummy1Step(Step):
        def run(self):
            nonlocal dummy1_called_config
            dummy1_called_config = self.model.config

    class Dummy2Step(Step):
        def run(self):
            nonlocal dummy2_called_config
            dummy2_called_config = self.model.config

    class DummyStepFactory(StepFactory):
        def build_step(self, model: StepModel, workflow: Workflow, context: WorkflowRunContext) -> Step:
            if model.name == 'dummy1':
                return Dummy1Step(model, workflow, context)
            if model.name == 'dummy2':
                return Dummy2Step(model, workflow, context)
            return None

    step_factory = DummyStepFactory()
    workflow_model = WorkflowModel(dummy1_step_model, dummy2_step_model)

    workflow = Workflow(workflow_model, step_factory)
    workflow.run()

    assert dummy1_called_config == {'foo': 'bar1'}
    assert dummy2_called_config == {'foo': 'bar2'}


class TestRunContext:
    def test_base_run_context(self):
        context = BaseRunContext()

        context['test'] = 'abc'
        assert context['test'] == 'abc'
        assert len(context) == 1
        for k, v in context.items():
            assert k == 'test'
            assert v == 'abc'
        del context['test']
        assert len(context) == 0
        assert context.get('test', 'default') == 'default'

    def test_workflow_run_context_step_not_found(self):
        context = WorkflowRunContext()

        assert context.step("not found") is None
        assert context.step(3) is None
        assert context.step(StepModel("not found")) is None
        assert context.step(NoopStep(StepModel("not found"), None, None)) is None

    def test_workflow_run_context_step_found(self):
        context = WorkflowRunContext()

        step_model = StepModel("noop")
        step = NoopStep(step_model, None, context)
        context.register_step(step)["foo"] = "bar"

        assert context.step("noop") == {"foo": "bar"}
        assert context.step(0) == {"foo": "bar"}
        assert context.step(step_model) == {"foo": "bar"}
        assert context.step(step) == {"foo": "bar"}

        assert step.context == {"foo": "bar"}
        assert step.workflow_context is context

    def test_workflow_run_context_steps_found(self):
        context = WorkflowRunContext()

        step_model = StepModel("noop")
        step = NoopStep(step_model, None, context)
        context.register_step(step)["foo"] = "bar"

        assert context.steps("noop") == [{"foo": "bar"}]
        assert context.steps(0) == [{"foo": "bar"}]
        assert context.steps(step_model) == [{"foo": "bar"}]
        assert context.steps(step) == [{"foo": "bar"}]

        assert step.context == {"foo": "bar"}
        assert step.workflow_context is context

    def test_workflow_run_context_step_found_default_solver(self):
        context = WorkflowRunContext()

        step_model = StepModel("noop")
        step = NoopStep(step_model, None, context)
        context.register_step(step)["foo"] = "bar"

        step_model2 = StepModel("noop", {"config": "2"})
        step2 = NoopStep(step_model2, None, context)
        context.register_step(step2)["foo"] = "bar2"

        assert context.step("noop") == {"foo": "bar2"}
        assert context.step(0) == {"foo": "bar"}
        assert context.step(1) == {"foo": "bar2"}
        assert context.step(step_model) == {"foo": "bar"}
        assert context.step(step_model2) == {"foo": "bar2"}
        assert context.step(step) == {"foo": "bar"}
        assert context.step(step2) == {"foo": "bar2"}

        assert step.context == {"foo": "bar"}
        assert step2.context == {"foo": "bar2"}

    def test_workflow_run_context_step_found_custom_solver(self):
        context = WorkflowRunContext()

        step_model = StepModel("noop")
        step = NoopStep(step_model, None, context)
        context.register_step(step)["foo"] = "bar"

        step_model2 = StepModel("noop", {"config": "2"})
        step2 = NoopStep(step_model2, None, context)
        context.register_step(step2)["foo"] = "bar2"

        solver = lambda contexts: contexts[0] if contexts else None

        assert context.step("noop", solver) == {"foo": "bar"}
        assert context.step(0, solver) == {"foo": "bar"}
        assert context.step(1, solver) == {"foo": "bar2"}
        assert context.step(step_model, solver) == {"foo": "bar"}
        assert context.step(step_model2, solver) == {"foo": "bar2"}
        assert context.step(step, solver) == {"foo": "bar"}
        assert context.step(step2, solver) == {"foo": "bar2"}

        assert step.context == {"foo": "bar"}
        assert step2.context == {"foo": "bar2"}
