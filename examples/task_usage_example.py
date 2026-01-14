"""
Example of using the Task System with custom tasks and steps.

This example demonstrates:
1. How to create and use a custom Task
2. How to create and use a custom TaskStep
3. How to register signal handlers
4. How to run a task with a task manager
"""
import sys
import time
from pathlib import Path
projectRoot = Path(__file__).parent.parent
sys.path.append(str(projectRoot))
from core import TaskManager, Task, TaskStep, PrintStep, SetVariableStep, TaskStatus

class DataProcessingTask(Task):
    """Task for processing data"""

    def __init__(self, data=None, name='Data Processing', description='Process input data'):
        super().__init__(name, description)
        self.data = data or {}
        self._setup_steps()

    def _setup_steps(self):
        """Set up task steps"""
        self.addStep(SetVariableStep('input_data', self.data))
        self.addStep(PrintStep('Processing input data: {input_data}'))
        self.addStep(DataValidationStep(outputVar='validation_result'))
        self.addStep(DataTransformStep(outputVar='transformed_data'))
        self.addStep(PrintStep('Processing complete. Result: {transformed_data}'))

class DataValidationStep(TaskStep):
    """Validate input data"""

    def __init__(self, outputVar=None):
        super().__init__('DataValidation', 'Validate input data')
        self.outputVariable = outputVar

    def execute(self, context, variables):
        """Execute step to validate data"""
        inputData = variables.get('input_data', {})
        print(f'[DataValidationStep] Validating data: {inputData}')
        time.sleep(1)
        task = context.get('task')
        if task:
            task.signals.progress.emit(task.id, 33)
        isValid = True
        return {'valid': isValid, 'message': 'Data is valid'}

class DataTransformStep(TaskStep):
    """Transform validated data"""

    def __init__(self, outputVar=None):
        super().__init__('DataTransform', 'Transform data into desired format')
        self.outputVariable = outputVar

    def execute(self, context, variables):
        """Execute step to transform data"""
        inputData = variables.get('input_data', {})
        validation = variables.get('validation_result', {'valid': False})
        if not validation.get('valid', False):
            return {'error': 'Cannot transform invalid data'}
        print(f'[DataTransformStep] Transforming data: {inputData}')
        time.sleep(1.5)
        task = context.get('task')
        if task:
            task.signals.progress.emit(task.id, 66)
        transformed = {'processed': True, 'source': inputData}
        return transformed

def onTaskStarted(taskId):
    """Handle task started event"""
    print(f'\n==> Task started: {taskId[:8]}...\n')

def onTaskProgress(taskId, progress):
    """Handle task progress event"""
    print(f'==> Task progress: {taskId[:8]}... - {progress}%')

def onTaskCompleted(taskId, result):
    """Handle task completed event"""
    print(f'\n==> Task completed: {taskId[:8]}...')
    print(f'==> Result: {result}\n')

def onTaskFailed(taskId, error):
    """Handle task failed event"""
    print(f'\n==> Task failed: {taskId[:8]}...')
    print(f'==> Error: {error}\n')

def main():
    """Run example"""
    print('=== Task System Example ===\n')
    taskManager = TaskManager(maxThreads=5)
    sampleData = {'name': 'Test', 'value': 42}
    task = DataProcessingTask(sampleData)
    task.signals.started.connect(onTaskStarted)
    task.signals.progress.connect(onTaskProgress)
    task.signals.completed.connect(onTaskCompleted)
    task.signals.failed.connect(onTaskFailed)
    context = {'task': task}
    taskManager.runTask(task, context)
    while task.status != TaskStatus.COMPLETED and task.status != TaskStatus.FAILED:
        time.sleep(0.5)
    print('Example completed.')
if __name__ == '__main__':
    main()