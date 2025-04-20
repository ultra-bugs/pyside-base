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
#
import datetime
import random
import time

from core import (ComputeIntensiveStep, ConditionStep, LoopStep, PrintStep, QtAppContext, SetVariableStep, SleepStep)
from core.Observer import Subscriber


class MainHandler(Subscriber):
    """Handler for main window events"""
    
    def __init__(self, widget_manager, events):
        super().__init__(events)
        self.widget_manager = widget_manager
        self.controller = widget_manager.controller
        
        # Get services from context
        self.task_manager = QtAppContext.get("task_manager")
        self.scheduler_service = QtAppContext.get("scheduler_service")
        
        # Configure task events to watch
        self.EVENT_ADD_SIMPLE_TASK = "add_simple_task"
        self.EVENT_ADD_SCHEDULED_TASK = "add_scheduled_task"
        self.EVENT_ADD_CONDITION_TASK = "add_condition_task"
        self.EVENT_ADD_LOOP_TASK = "add_loop_task"
        self.EVENT_ADD_CONCURRENT_TASKS = "add_concurrent_tasks"
        self.EVENT_CREATE_CPU_INTENSIVE_TASK = "create_cpu_intensive_task"
    
    def on_add_simple_task(self, data = None):
        """Handle event to create a simple task"""
        task = self.task_manager.create_task("Simple Task", "A simple demonstration task")
        
        # Add steps
        task.add_step(PrintStep("Task is running..."))
        task.add_step(SetVariableStep("counter", 1))
        task.add_step(PrintStep("Set counter = {counter}"))
        
        # Register signals
        self.controller.register_task_signals(task)
        # Update UI
        self.controller.update_task_table()
        # Run task
        self.task_manager.run_task(task)
        self.controller.log_message(f"Created and started simple task: {task.id}")
    
    def on_add_scheduled_task(self, data = None):
        """Handle event to create a scheduled task to run after 15 seconds"""
        task = self.task_manager.create_task("Scheduled Task", "A scheduled task that runs after 15 seconds")
        
        # Add steps
        task.add_step(PrintStep("Scheduled task is running!"))
        task.add_step(PrintStep("Current time: " + datetime.datetime.now().strftime("%H:%M:%S")))
        
        # Register signals
        self.controller.register_task_signals(task)
        # Update UI
        self.controller.update_schedule_table()
        self.controller.update_task_table()
        # Schedule task to run after 15 seconds
        run_at = time.time() + 15
        self.scheduler_service.add_schedule(task, run_at)
        
        self.controller.log_message(f"Scheduled task: {task.id} to run in 15 seconds")
    
    def on_add_condition_task(self, data = None):
        """Handle event to create a task with conditional execution"""
        task = self.task_manager.create_task("Condition Task", "A task with conditional execution")
        
        # Initialize variable
        task.add_step(SetVariableStep("test_condition", True))
        
        # Create steps for true and false conditions
        true_steps = [
            PrintStep("Condition is TRUE"),
            SetVariableStep("result", "Success")
        ]
        
        false_steps = [
            PrintStep("Condition is FALSE"),
            SetVariableStep("result", "Failed")
        ]
        
        # Add conditional step
        task.add_step(ConditionStep("test_condition", true_steps, false_steps))
        task.add_step(PrintStep("Result: {result}"))
        
        # Register signals
        self.controller.register_task_signals(task)
        # Update UI
        self.controller.update_task_table()
        # Run task
        self.task_manager.run_task(task)
        self.controller.log_message(f"Created and started condition task: {task.id}")
    
    def on_add_loop_task(self, data = None):
        """Handle event to create a task with a loop"""
        task = self.task_manager.create_task("Loop Task", "A task with loop")
        
        # Create steps for the loop
        loop_steps = [
            PrintStep("Loop iteration {loop_index}"),
            SetVariableStep("temp_value", "Loop value")
        ]
        
        # Add loop step
        task.add_step(LoopStep(5, loop_steps))
        task.add_step(PrintStep("Loop completed"))
        
        # Register signals
        self.controller.register_task_signals(task)
        # Update UI
        self.controller.update_task_table()
        # Run task
        self.task_manager.run_task(task)
        self.controller.log_message(f"Created and started loop task: {task.id}")
    
    def on_add_concurrent_tasks(self, data = None):
        """Handle event to create and run multiple concurrent tasks"""
        # Create several tasks that consume time
        task_count = 5
        tasks = []
        
        for i in range(task_count):
            # Random duration between 5-15 seconds
            duration = random.randint(5, 15)
            task = self.task_manager.create_task(
                    f"Concurrent Task {i + 1}",
                    f"A concurrent task that sleeps for {duration} seconds"
            )
            
            # Add sleep step to simulate time-consuming task
            context = {'task': task}  # Pass task to context for progress updates
            task.add_step(PrintStep(f"Starting concurrent task {i + 1} with {duration}s duration"))
            task.add_step(SleepStep(duration))
            task.add_step(PrintStep("Concurrent task completed"))
            
            # Register signals
            self.controller.register_task_signals(task)
            tasks.append(task)
        
        # Update UI
        self.controller.update_task_table()
        # Run all tasks concurrently
        task_ids = self.task_manager.run_tasks(tasks)
        
        # Log message
        active_count = self.task_manager.get_active_tasks_count()
        max_threads = self.task_manager.get_max_threads()
        self.controller.log_message(
                f"Started {len(tasks)} concurrent tasks. Active: {active_count}/{max_threads}"
        )
    
    def on_create_cpu_intensive_task(self, data = None):
        """Handle event to create a CPU-intensive task"""
        task = self.task_manager.create_task(
                "CPU Intensive Task",
                "A task that performs intensive computation"
        )
        
        # Random complexity between 10-20 million operations
        complexity = random.randint(10000000, 20000000)
        
        # Add steps
        task.add_step(PrintStep(f"Starting CPU-intensive task with complexity {complexity}"))
        task.add_step(ComputeIntensiveStep(complexity, "computation_result"))
        task.add_step(PrintStep("Computation result: {computation_result}"))
        
        # Register signals
        self.controller.register_task_signals(task)
        
        # Update UI
        self.controller.update_task_table()
        # Run task
        self.task_manager.run_task(task, {'task': task})
        self.controller.log_message(f"Created and started CPU-intensive task: {task.id}")
    
    def on_exit_app(self, data = None):
        """Handle event to close the application"""
        self.controller.close()
    
    def on_add_new_task(self, data = None):
        """Handle event to add new task from menu"""
        self.on_add_simple_task(data)
    
    def on_add_new_scheduled_task(self, data = None):
        """Handle event to add new scheduled task from menu"""
        self.on_add_scheduled_task(data)
