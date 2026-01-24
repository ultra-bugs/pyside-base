#                  M""""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *

import datetime
import random
from datetime import timedelta
from core.Observer import Subscriber
from core.QtAppContext import QtAppContext
from core.Logging import logger
from app.tasks import SimpleDemoTask, ConditionDemoTask, LoopDemoTask, SleepDemoTask, CpuIntensiveDemoTask, AdbCommandTask, ChainDemoTask


class MainHandler(Subscriber):
    """Handler for main window events"""

    def __init__(self, widgetManager, events):
        super().__init__(events)
        self.widgetManager = widgetManager
        self.controller = widgetManager.controllere
        ctx = QtAppContext.globalInstance()
        self.taskManager = ctx.taskManager
        # self.EVENT_ADD_SIMPLE_TASK = 'add_simple_task'
        # self.EVENT_ADD_SCHEDULED_TASK = 'add_scheduled_task'
        # self.EVENT_ADD_CONDITION_TASK = 'add_condition_task'
        # self.EVENT_ADD_LOOP_TASK = 'add_loop_task'
        # self.EVENT_ADD_CONCURRENT_TASKS = 'add_concurrent_tasks'
        # self.EVENT_CREATE_CPU_INTENSIVE_TASK = 'create_cpu_intensive_task'
        # self.EVENT_ADD_CHAIN_TASK = 'add_chain_task'
        # self.EVENT_ADD_RETRY_CHAIN_TASK = 'add_retry_chain_task'

    def onAddSimpleTask(self, data=None):
        """Create a simple demo task using new TaskSystem and enqueue it."""
        task = SimpleDemoTask(name='Simple Task', description='A simple demonstration task')
        self.taskManager.addTask(task)
        self.controller.logMessage(f'Created and enqueued simple task: {task.uuid[:8]}')

    def onAddScheduledTask(self, data=None):
        """Create a scheduled task to run after 15 seconds using TaskScheduler via TaskManagerService."""
        task = SimpleDemoTask(name='Scheduled Task', description='Runs after 15 seconds')
        scheduleInfo = {'trigger': 'date', 'runDate': datetime.datetime.now() + timedelta(seconds=15)}
        self.taskManager.addTask(task, scheduleInfo=scheduleInfo)
        self.controller.logMessage(f'Scheduled task: {task.uuid[:8]} to run in 15 seconds')

    def onAddConditionTask(self, data=None):
        """Create a conditional demo task and enqueue it."""
        task = ConditionDemoTask(name='Condition Task', description='Conditional execution demo', testCondition=True)
        self.taskManager.addTask(task)
        self.controller.logMessage(f'Created and enqueued condition task: {task.uuid[:8]}')

    def onAddLoopTask(self, data=None):
        """Create a loop demo task and enqueue it."""
        task = LoopDemoTask(name='Loop Task', description='Loop demo', loopCount=5, delaySeconds=0.2)
        self.taskManager.addTask(task)
        self.controller.logMessage(f'Created and enqueued loop task: {task.uuid[:8]}')

    def onAddConcurrentTasks(self, data=None):
        """Create and enqueue multiple concurrent sleep tasks."""
        taskCount = 5
        for i in range(taskCount):
            duration = random.randint(5, 15)
            task = SleepDemoTask(name=f'Concurrent Task {i + 1}', description=f'Sleeps for {duration}s', durationSeconds=duration)
            self.taskManager.addTask(task)
        qs = self.taskManager.getQueueStatus()
        self.controller.logMessage(f'Started {taskCount} concurrent tasks. Running: {qs.get("running", 0)}/{qs.get("maxConcurrent", 0)} (pending: {qs.get("pending", 0)})')

    def onCreateCpuIntensiveTask(self, data=None):
        """Create a CPU-intensive demo task and enqueue it."""
        complexity = random.randint(1000000, 2000000) * 10
        task = CpuIntensiveDemoTask(name='CPU Intensive Task', description='Performs heavy computations', complexity=complexity)
        self.taskManager.addTask(task)
        self.controller.logMessage(f'Created and enqueued CPU-intensive task: {task.uuid[:8]}')

    def onAddChainTask(self, data=None):
        """Create a chain demo task and enqueue it."""
        chain = ChainDemoTask.createDemoChain()
        self.taskManager.addTask(chain)
        self.controller.logMessage(f'Created and enqueued chain task: {chain.uuid[:8]}')

    def onAddRetryChainTask(self, data=None):
        """Create a chain demo task with retry logic and enqueue it."""
        chain = ChainDemoTask.createRetryDemoChain()
        self.taskManager.addTask(chain)
        self.controller.logMessage(f'Created and enqueued retry chain task: {chain.uuid[:8]}')

    def onExitApp(self, data=None):
        """Handle event to close the application"""
        self.controller.close()

    def onAddNewTask(self, data=None):
        """Handle event to add new task from menu"""
        self.onAddSimpleTask(data)

    def onAddNewScheduledTask(self, data=None):
        """Handle event to add new scheduled task from menu"""
        self.onAddScheduledTask(data)

    def onRunAdbDevices(self, data=None):
        task = AdbCommandTask(name='ADB: devices', command='devices')
        self.taskManager.addTask(task)
        self.controller.logMessage(f'Enqueued ADB task: {task.uuid[:8]}')
