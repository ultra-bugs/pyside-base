#!/usr/bin/env python3

#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

#
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

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core import (
    TaskManager, Task, TaskStep, PrintStep, SetVariableStep,
    TaskStatus
)


# Example of using a task created with the generator
# Uncomment these lines after creating a custom task and step
# from tasks import MyCustomTask
# from tasks.steps import MyCustomStep


# Example of a custom Task class created manually
class DataProcessingTask(Task):
    """Task for processing data"""
    
    def __init__(self, data = None, name = "Data Processing", description = "Process input data"):
        super().__init__(name, description)
        self.data = data or {}
        self._setup_steps()
    
    def _setup_steps(self):
        """Set up task steps"""
        # Set variables
        self.add_step(SetVariableStep("input_data", self.data))
        self.add_step(PrintStep("Processing input data: {input_data}"))
        
        # Add processing steps
        self.add_step(DataValidationStep(output_var="validation_result"))
        self.add_step(DataTransformStep(output_var="transformed_data"))
        
        # Print result
        self.add_step(PrintStep("Processing complete. Result: {transformed_data}"))


# Example of a custom TaskStep class created manually
class DataValidationStep(TaskStep):
    """Validate input data"""
    
    def __init__(self, output_var = None):
        super().__init__("DataValidation", "Validate input data")
        self.output_variable = output_var
    
    def execute(self, context, variables):
        """Execute step to validate data"""
        input_data = variables.get("input_data", {})
        
        # Simulate validation
        print(f"[DataValidationStep] Validating data: {input_data}")
        time.sleep(1)  # Simulate processing time
        
        # Report progress if task is available
        task = context.get('task')
        if task:
            task.signals.progress.emit(task.id, 33)  # 33% progress
        
        # Return validation result
        is_valid = True  # Simplified validation
        return {"valid": is_valid, "message": "Data is valid"}


class DataTransformStep(TaskStep):
    """Transform validated data"""
    
    def __init__(self, output_var = None):
        super().__init__("DataTransform", "Transform data into desired format")
        self.output_variable = output_var
    
    def execute(self, context, variables):
        """Execute step to transform data"""
        input_data = variables.get("input_data", {})
        validation = variables.get("validation_result", {"valid": False})
        
        if not validation.get("valid", False):
            return {"error": "Cannot transform invalid data"}
        
        # Simulate transformation
        print(f"[DataTransformStep] Transforming data: {input_data}")
        time.sleep(1.5)  # Simulate processing time
        
        # Report progress if task is available
        task = context.get('task')
        if task:
            task.signals.progress.emit(task.id, 66)  # 66% progress
        
        # Return transformed data (simplified example)
        transformed = {"processed": True, "source": input_data}
        return transformed


def on_task_started(task_id):
    """Handle task started event"""
    print(f"\n==> Task started: {task_id[:8]}...\n")


def on_task_progress(task_id, progress):
    """Handle task progress event"""
    print(f"==> Task progress: {task_id[:8]}... - {progress}%")


def on_task_completed(task_id, result):
    """Handle task completed event"""
    print(f"\n==> Task completed: {task_id[:8]}...")
    print(f"==> Result: {result}\n")


def on_task_failed(task_id, error):
    """Handle task failed event"""
    print(f"\n==> Task failed: {task_id[:8]}...")
    print(f"==> Error: {error}\n")


def main():
    """Run example"""
    print("=== Task System Example ===\n")
    
    # Initialize task manager
    task_manager = TaskManager(max_threads=5)
    
    # Create a task with sample data
    sample_data = {"name": "Test", "value": 42}
    task = DataProcessingTask(sample_data)
    
    # Register signal handlers
    task.signals.started.connect(on_task_started)
    task.signals.progress.connect(on_task_progress)
    task.signals.completed.connect(on_task_completed)
    task.signals.failed.connect(on_task_failed)
    
    # Run the task with context (task reference is passed for progress reporting)
    context = {'task': task}
    task_manager.run_task(task, context)
    
    # Wait for task to complete (for this example)
    while task.status != TaskStatus.COMPLETED and task.status != TaskStatus.FAILED:
        time.sleep(0.5)
    
    print("Example completed.")


if __name__ == "__main__":
    main()
