from stepbystep import Step, StepModel, Workflow, WorkflowRunContext


class NoopStep(Step):
    """
    A step that performs nothing.
    """

    def __init__(self, model: StepModel, workflow: Workflow, workflow_run_context: WorkflowRunContext):
        super().__init__(model, workflow, workflow_run_context)

    def run(self):
        pass
