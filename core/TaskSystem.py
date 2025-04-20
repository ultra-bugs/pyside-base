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
import random
import time
import uuid
from enum import Enum

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskSignals(QObject):
    started = Signal(str)  # task_id
    progress = Signal(str, int)  # task_id, progress_percent
    completed = Signal(str, object)  # task_id, result
    failed = Signal(str, str)  # task_id, error_message


class TaskStep:
    def __init__(self, name, description = ""):
        self.name = name
        self.description = description
        self.output_variable = None
    
    def execute(self, context, variables):
        """Execute the task step, return the result"""
        raise NotImplementedError


class Task:
    def __init__(self, name, description = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.steps = []
        self.variables = {}
        self.created_at = time.time()
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.signals = TaskSignals()
    
    def add_step(self, step):
        self.steps.append(step)
        return self
    
    def execute(self, context = None):
        """Execute task with optional context"""
        self.status = TaskStatus.RUNNING
        self.signals.started.emit(self.id)
        
        step_results = []
        step_count = len(self.steps)
        
        try:
            for i, step in enumerate(self.steps):
                # Report progress
                progress = int((i / step_count) * 100)
                self.signals.progress.emit(self.id, progress)
                
                # Execute step
                result = step.execute(context, self.variables)
                step_results.append(result)
                
                # Save result to variable if needed
                if step.output_variable:
                    self.variables[step.output_variable] = result
            
            # Complete
            self.status = TaskStatus.COMPLETED
            self.result = step_results
            self.signals.completed.emit(self.id, step_results)
            return True, step_results
        
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.signals.failed.emit(self.id, str(e))
            return False, str(e)


class TaskRunner(QRunnable):
    def __init__(self, task, context = None):
        super().__init__()
        self.task = task
        self.context = context
    
    def run(self):
        self.task.execute(self.context)


class TaskManager:
    def __init__(self, max_threads = 10):
        self.tasks = {}  # task_id -> Task
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(max_threads)  # Limit the number of concurrent tasks
    
    def create_task(self, name, description = ""):
        task = Task(name, description)
        self.tasks[task.id] = task
        return task
    
    def run_task(self, task, context = None):
        """Run task in the thread pool"""
        if task.id not in self.tasks:
            self.tasks[task.id] = task
        
        runner = TaskRunner(task, context)
        self.thread_pool.start(runner)
        return task.id
    
    def run_tasks(self, tasks, context = None):
        """Run multiple tasks in the thread pool"""
        task_ids = []
        for task in tasks:
            task_id = self.run_task(task, context)
            task_ids.append(task_id)
        return task_ids
    
    def get_task(self, task_id):
        return self.tasks.get(task_id)
    
    def get_all_tasks(self):
        return list(self.tasks.values())
    
    def get_active_tasks_count(self):
        """Return the number of currently running tasks"""
        return self.thread_pool.activeThreadCount()
    
    def get_max_threads(self):
        """Return the maximum number of threads"""
        return self.thread_pool.maxThreadCount()


class ConditionStep(TaskStep):
    def __init__(self, condition_var, true_steps = None, false_steps = None):
        super().__init__("Condition", f"Check condition {condition_var}")
        self.condition_var = condition_var
        self.true_steps = true_steps or []
        self.false_steps = false_steps or []
    
    def execute(self, context, variables):
        # Check condition
        condition_value = variables.get(self.condition_var, False)
        
        # Execute appropriate steps
        steps_to_execute = self.true_steps if condition_value else self.false_steps
        results = []
        
        for step in steps_to_execute:
            try:
                result = step.execute(context, variables)
                results.append(result)
                
                # Update variables
                if hasattr(step, 'output_variable') and step.output_variable:
                    variables[step.output_variable] = result
            except Exception as e:
                raise Exception(f"Error in condition: {str(e)}")
        
        return results


class LoopStep(TaskStep):
    def __init__(self, count, steps = None):
        super().__init__("Loop", f"Loop {count} times")
        self.count = count
        self.steps = steps or []
    
    def execute(self, context, variables):
        results = []
        
        for i in range(self.count):
            variables["loop_index"] = i
            loop_results = []
            
            for step in self.steps:
                try:
                    result = step.execute(context, variables)
                    loop_results.append(result)
                    
                    # Update variables
                    if hasattr(step, 'output_variable') and step.output_variable:
                        variables[step.output_variable] = result
                except Exception as e:
                    raise Exception(f"Error in loop: {str(e)}")
            
            results.append(loop_results)
        
        return results


# Simple steps for demo
class PrintStep(TaskStep):
    def __init__(self, message):
        super().__init__("Print", f"Print message: {message}")
        self.message = message
    
    def execute(self, context, variables):
        message = self.message
        # Replace variables in message
        for var_name, var_value in variables.items():
            if isinstance(var_value, str) or isinstance(var_value, int):
                message = message.replace(f"{{{var_name}}}", str(var_value))
        
        print(f"[Task] {message}")
        return message


class SetVariableStep(TaskStep):
    def __init__(self, variable_name, value):
        super().__init__("SetVariable", f"Set variable {variable_name} = {value}")
        self.variable_name = variable_name
        self.value = value
        self.output_variable = variable_name
    
    def execute(self, context, variables):
        return self.value


# Time-consuming steps for concurrent execution demo
class SleepStep(TaskStep):
    def __init__(self, seconds, report_interval = 1):
        super().__init__("Sleep", f"Sleep for {seconds} seconds")
        self.seconds = seconds
        self.report_interval = report_interval
    
    def execute(self, context, variables):
        start_time = time.time()
        elapsed = 0
        task = context.get('task') if context else None
        
        while elapsed < self.seconds:
            time.sleep(min(self.report_interval, self.seconds - elapsed))
            elapsed = time.time() - start_time
            
            # Report progress if task is available
            if task:
                progress = int((elapsed / self.seconds) * 100)
                task.signals.progress.emit(task.id, progress)
        
        return f"Slept for {elapsed:.2f} seconds"


class ComputeIntensiveStep(TaskStep):
    def __init__(self, complexity = 1000000, output_var = None):
        super().__init__("ComputeIntensive", f"Perform intensive computation (complexity={complexity})")
        self.complexity = complexity
        self.output_variable = output_var
    
    def execute(self, context, variables):
        """Simulate a CPU-intensive calculation"""
        task = context.get('task') if context else None
        result = 0
        
        for i in range(self.complexity):
            # Some arbitrary computation
            result += random.random()
            
            # Report progress occasionally
            if task and i % (self.complexity // 100) == 0:
                progress = int((i / self.complexity) * 100)
                task.signals.progress.emit(task.id, progress)
        
        return result
