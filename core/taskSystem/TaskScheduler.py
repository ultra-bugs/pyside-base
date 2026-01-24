"""
TaskScheduler

Pure Qt-based task scheduler using QTimer.
No background threads - fully integrated with Qt event loop.
Supports date-based, interval-based, and basic cron-style scheduling.
"""

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

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from PySide6 import QtCore

from ..Config import Config
from ..Logging import logger
from .storage.BaseStorage import BaseStorage

logger = logger.bind(component='TaskSystem')


class ScheduledJob:
    """
    Represents a scheduled job with its timer and metadata.
    """

    def __init__(self, jobId: str, taskUuid: str, taskClass: str, taskData: Dict[str, Any], trigger: str, timer: QtCore.QTimer, nextRun: Optional[datetime] = None):
        self.jobId = jobId
        self.taskUuid = taskUuid
        self.taskClass = taskClass
        self.taskData = taskData
        self.trigger = trigger
        self.timer = timer
        self.nextRun = nextRun
        self.createdAt = datetime.now()

    def toDict(self) -> Dict[str, Any]:
        """Serialize job for persistence."""
        return {
            'jobId': self.jobId,
            'taskUuid': self.taskUuid,
            'taskClass': self.taskClass,
            'taskData': self.taskData,
            'trigger': self.trigger,
            'nextRun': self.nextRun.isoformat() if self.nextRun else None,
            'createdAt': self.createdAt.isoformat(),
        }


class TaskScheduler(QtCore.QObject):
    """
    Pure Qt task scheduler using QTimer.

    Features:
    - Date-based scheduling (one-time execution)
    - Interval-based scheduling (recurring)
    - Basic cron-style scheduling (daily at specific time)
    - Persistence via Storage
    - No background threads - uses Qt event loop

    Signals:
        jobScheduled: Emitted when a job is scheduled (jobId, taskUuid)
        jobUnscheduled: Emitted when a job is removed (jobId)
        jobExecuted: Emitted when a job triggers (jobId, taskUuid)
    """

    jobScheduled = QtCore.Signal(str, str)
    jobUnscheduled = QtCore.Signal(str)
    jobExecuted = QtCore.Signal(str, str)

    def __init__(self, taskQueue, storage: BaseStorage):
        """
        Initialize TaskScheduler.
        Args:
            taskQueue: TaskQueue instance for executing tasks
            storage: Storage backend for persistence
        """
        super().__init__()
        self._taskQueue = taskQueue
        self._storage = storage
        self._jobs: Dict[str, ScheduledJob] = {}
        self._loadJobs()
        logger.info('TaskScheduler initialized (Pure Qt)')

    def addScheduledTask(self, task: Any, trigger: str, runDate: Optional[datetime] = None, intervalSeconds: Optional[int] = None, **kwargs) -> str:
        """
        Schedule a task for execution.
        Args:
            task: AbstractTask instance to schedule
            trigger: Trigger type ('date', 'interval', 'cron')
            runDate: For 'date' trigger - when to run
            intervalSeconds: For 'interval' trigger - interval in seconds
            **kwargs: For 'cron' trigger (hour, minute)
        Returns:
            Job ID for the scheduled job
        Raises:
            ValueError: If trigger type is invalid or required parameters missing
        """
        taskUuid = task.uuid
        taskName = task.name
        taskData = task.serialize()
        taskClass = f'{task.__class__.__module__}.{task.__class__.__name__}'
        logger.debug(f'Scheduling task: {taskUuid} - Class: {taskClass} - Trigger: {trigger}')
        jobId = f'task_{taskUuid}'
        timer = QtCore.QTimer(self)
        timer.setSingleShot(trigger == 'date')
        nextRun = None
        if trigger == 'date':
            if not runDate:
                raise ValueError("runDate is required for 'date' trigger")
            now = datetime.now()
            if runDate <= now:
                raise ValueError(f'runDate must be in the future (got {runDate}, now is {now})')
            delayMs = int((runDate - now).total_seconds() * 1000)
            timer.setInterval(delayMs)
            nextRun = runDate
            logger.info(f'Scheduled one-time task {taskUuid} for {runDate} (in {delayMs}ms)')
        elif trigger == 'interval':
            if not intervalSeconds:
                raise ValueError("intervalSeconds is required for 'interval' trigger")
            if intervalSeconds <= 0:
                raise ValueError('intervalSeconds must be > 0')
            delayMs = intervalSeconds * 1000
            timer.setInterval(delayMs)
            nextRun = datetime.now() + timedelta(seconds=intervalSeconds)
            logger.info(f'Scheduled recurring task {taskUuid} every {intervalSeconds}s')
        elif trigger == 'cron':
            hour = kwargs.get('hour')
            minute = kwargs.get('minute', 0)
            if hour is None:
                raise ValueError("hour is required for 'cron' trigger")
            now = datetime.now()
            nextRun = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if nextRun <= now:
                nextRun += timedelta(days=1)
            delayMs = int((nextRun - now).total_seconds() * 1000)
            timer.setInterval(delayMs)
            timer.setSingleShot(True)
            logger.info(f'Scheduled cron task {taskUuid} for {nextRun} (daily at {hour}:{minute:02d})')
        else:
            raise ValueError(f'Unknown trigger type: {trigger}')
        timer.timeout.connect(lambda: self._executeScheduledTask(jobId, taskUuid, taskClass, taskData, trigger, **kwargs))
        job = ScheduledJob(jobId, taskUuid, taskClass, taskData, trigger, timer, nextRun)
        self._jobs[jobId] = job
        timer.start()
        self._saveJobs()
        self.jobScheduled.emit(jobId, taskUuid)
        logger.info(f'Task scheduled: {jobId} - {taskName}')
        return jobId

    def _executeScheduledTask(self, jobId: str, taskUuid: str, taskClass: str, taskData: Dict[str, Any], trigger: str, **kwargs) -> None:
        """
        Execute a scheduled task by reconstructing it from serialized data.
        Args:
            jobId: Job ID
            taskUuid: Task UUID
            taskClass: Fully qualified class name
            taskData: Serialized task data
            trigger: Trigger type (for rescheduling)
            **kwargs: Trigger-specific arguments (for cron rescheduling)
        """
        logger.info(f'Executing scheduled task: {taskUuid} - Job: {jobId}')
        try:
            moduleName, className = taskClass.rsplit('.', 1)
            logger.debug(f'Importing module: {moduleName}, class: {className}')
            module = __import__(moduleName, fromlist=[className])
            taskCls = getattr(module, className)
            logger.debug(f'Reconstructing task from data: {taskData.get("name", "Unknown")}')
            task = taskCls.deserialize(taskData)
            if task.uuid != taskUuid:
                logger.warning(f'Task UUID mismatch after deserialization: {task.uuid} != {taskUuid}')
                task.uuid = taskUuid
            logger.info(f'Adding reconstructed task to queue: {task.uuid} - {task.name}')
            self._taskQueue.addTask(task)
            self.jobExecuted.emit(jobId, taskUuid)
            if trigger == 'interval':
                logger.debug(f'Interval job {jobId} will repeat automatically')
            elif trigger == 'cron':
                job = self._jobs.get(jobId)
                if job:
                    hour = kwargs.get('hour')
                    minute = kwargs.get('minute', 0)
                    now = datetime.now()
                    nextRun = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    nextRun += timedelta(days=1)
                    delayMs = int((nextRun - now).total_seconds() * 1000)
                    job.timer.setInterval(delayMs)
                    job.timer.start()
                    job.nextRun = nextRun
                    logger.info(f'Rescheduled cron job {jobId} for {nextRun}')
            elif trigger == 'date':
                logger.info(f'One-time job {jobId} completed, removing')
                self.removeScheduledTask(jobId)
        except Exception as e:
            logger.error(f'Failed to reconstruct and execute scheduled task {taskUuid}: {e}', exc_info=True)

    def removeScheduledTask(self, jobId: str) -> None:
        """
        Remove a scheduled job.
        Args:
            jobId: Job ID to remove
        """
        if jobId not in self._jobs:
            logger.warning(f'Job {jobId} not found')
            raise KeyError(f'Job {jobId} not found')
        job = self._jobs[jobId]
        job.timer.stop()
        job.timer.deleteLater()
        del self._jobs[jobId]
        self._saveJobs()
        self.jobUnscheduled.emit(jobId)
        logger.info(f'Job removed: {jobId}')

    def getScheduledJobs(self) -> List[Dict[str, Any]]:
        """
        Get list of all scheduled jobs.
        Returns:
            List of dictionaries containing job information
        """
        jobs = []
        for job in self._jobs.values():
            jobInfo = {
                'id': job.jobId,
                'name': job.taskData.get('name', 'Unknown'),
                'task_uuid': job.taskUuid,
                'trigger': job.trigger,
                'next_run_time': job.nextRun.isoformat() if job.nextRun else None,
                'created_at': job.createdAt.isoformat(),
            }
            jobs.append(jobInfo)
        return jobs

    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the scheduler.
        Args:
            wait: Unused (for API compatibility)
        """
        logger.info('Shutting down TaskScheduler')
        for job in self._jobs.values():
            job.timer.stop()
            job.timer.deleteLater()
        self._jobs.clear()
        logger.info('TaskScheduler shutdown complete')

    def _saveJobs(self) -> None:
        """Save scheduled jobs to storage for persistence."""
        try:
            jobsData = [job.toDict() for job in self._jobs.values()]
            self._storage.save('scheduledJobs', jobsData)
            logger.debug(f'Saved {len(jobsData)} scheduled jobs to storage')
        except Exception as e:
            logger.error(f'Failed to save scheduled jobs: {e}')

    def _loadJobs(self) -> None:
        """Load scheduled jobs from storage."""
        try:
            jobsData = self._storage.load('scheduledJobs', [])
            if not jobsData:
                logger.debug('No persisted jobs to load')
                return
            logger.info(f'Loading {len(jobsData)} persisted jobs')
            for jobData in jobsData:
                try:
                    jobId = jobData['jobId']
                    taskUuid = jobData['taskUuid']
                    taskClass = jobData['taskClass']
                    taskData = jobData['taskData']
                    trigger = jobData['trigger']
                    nextRunStr = jobData.get('nextRun')
                    if not nextRunStr:
                        logger.warning(f'Job {jobId} has no nextRun time, skipping')
                        continue
                    nextRun = datetime.fromisoformat(nextRunStr)
                    now = datetime.now()
                    if nextRun < now and trigger == 'date':
                        logger.info(f'Skipping past one-time job {jobId} (was scheduled for {nextRun})')
                        continue
                    logger.info(f'Rescheduling persisted job {jobId}')
                    logger.warning(f'Job {jobId} persistence not fully implemented yet')
                except Exception as e:
                    logger.error(f'Failed to load job {jobData.get("jobId", "unknown")}: {e}')
                    continue
        except Exception as e:
            logger.error(f'Failed to load scheduled jobs: {e}')
