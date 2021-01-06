from stepbystep import Workflow, StepFactory, StepModel, Step, WorkflowModel


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
        def build_step(self, model: StepModel, workflow: Workflow) -> Step:
            if model.name == 'dummy1':
                return Dummy1Step(model, workflow)
            if model.name == 'dummy2':
                return Dummy2Step(model, workflow)
            return None

    step_factory = DummyStepFactory()
    workflow_model = WorkflowModel(dummy1_step_model, dummy2_step_model)

    workflow = Workflow(workflow_model, step_factory)
    workflow.run()

    assert dummy1_called_config == {'foo': 'bar1'}
    assert dummy2_called_config == {'foo': 'bar2'}
