"""
ChainDemoTask

A sample task demonstrating Task Chaining capabilities.
This task creates a chain of sub-tasks that share data via ChainContext.
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

import random
import time
from typing import Any, Dict

from core.Logging import logger
from core.taskSystem import AbstractTask, ChainRetryBehavior, TaskChain

logger = logger.bind(component='TaskSystem')


class DataGeneratorTask(AbstractTask):
    """Generates random data and stores it in ChainContext."""

    def __init__(self, name: str = 'Data Generator', count: int = 5, **kwargs):
        super().__init__(name=name, **kwargs)
        self.count = count

    def handle(self) -> None:
        self.setProgress(10)
        logger.info(f'Generating {self.count} random numbers...')
        time.sleep(1)
        self.setProgress(50)
        data = [random.randint(1, 100) for _ in range(self.count)]
        logger.info(f'Generated data: {data}')
        if self._chainContext:
            self._chainContext.set('raw_data', data)
            logger.info('Data stored in ChainContext')
        else:
            logger.warning('No ChainContext available!')
        self.setProgress(100)
        self.result = data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'DataGeneratorTask':
        return cls(
            name=data['name'],
            count=data.get('count', 5),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
            chainUuid=data.get('chainUuid'),
        )


class DataProcessorTask(AbstractTask):
    """Retrieves data from ChainContext, processes it, and stores result."""

    def __init__(self, name: str = 'Data Processor', multiplier: int = 2, **kwargs):
        super().__init__(name=name, **kwargs)
        self.multiplier = multiplier

    def handle(self) -> None:
        self.setProgress(10)
        rawData = []
        if self._chainContext:
            rawData = self._chainContext.get('raw_data', [])
            logger.info(f'Retrieved raw data: {rawData}')
        else:
            logger.warning('No ChainContext available!')
        if not rawData:
            self.fail('No data to process!')
            return
        processedData = []
        total = len(rawData)
        for i, num in enumerate(rawData):
            if self.isStopped():
                return
            time.sleep(0.5)
            result = num * self.multiplier
            processedData.append(result)
            progress = 10 + int((i + 1) / total * 80)
            self.setProgress(progress)
        logger.info(f'Processed data: {processedData}')
        if self._chainContext:
            self._chainContext.set('processed_data', processedData)
        self.setProgress(100)
        self.result = processedData

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'DataProcessorTask':
        return cls(
            name=data['name'],
            multiplier=data.get('multiplier', 2),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
            chainUuid=data.get('chainUuid'),
        )


class FlakyTask(AbstractTask):
    """A task that randomly fails to demonstrate retry behavior."""

    def __init__(self, name: str = 'Flaky Task', failureRate: float = 0.5, **kwargs):
        super().__init__(name=name, **kwargs)
        self.failureRate = failureRate

    def handle(self) -> None:
        self.setProgress(10)
        logger.info(f'Attempting flaky operation (failure rate: {self.failureRate})...')
        time.sleep(1)
        self.setProgress(50)
        if random.random() < self.failureRate:
            self.fail('Random failure occurred!')
            return
        logger.info('Operation succeeded!')
        self.setProgress(100)
        self.result = 'Success'

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'FlakyTask':
        return cls(
            name=data['name'],
            failureRate=data.get('failure_rate', 0.5),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
            chainUuid=data.get('chainUuid'),
        )


class ConsistentlyFailingTask(AbstractTask):
    """A task that fails a specific number of times before succeeding."""

    def __init__(self, name: str = 'Failing Task', failuresBeforeSuccess: int = 2, **kwargs):
        super().__init__(name=name, **kwargs)
        self.failuresBeforeSuccess = failuresBeforeSuccess
        self._attempts = 0

    def handle(self) -> None:
        self._attempts += 1
        self.setProgress(25)
        logger.info(f"Attempt {self._attempts} for task '{self.name}'...")
        time.sleep(1)
        if self._attempts <= self.failuresBeforeSuccess:
            self.setProgress(75)
            self.fail(f'Deliberate failure #{self._attempts}')
            return
        logger.info(f"Task '{self.name}' finally succeeded on attempt {self._attempts}.")
        self.setProgress(100)
        self.result = 'Success after failures'

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'ConsistentlyFailingTask':
        task = cls(
            name=data['name'],
            failuresBeforeSuccess=data.get('failures_before_success', 2),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
            chainUuid=data.get('chainUuid'),
        )
        task._attempts = data.get('_attempts', 0)
        return task


class ChainDemoTask:
    """Factory for creating demo chains."""

    @staticmethod
    def createDemoChain(name: str = 'Demo Chain') -> TaskChain:
        """
        Creates a sample chain with:
        1. DataGeneratorTask
        2. FlakyTask (with retry)
        3. DataProcessorTask
        """
        task1 = DataGeneratorTask(name='Step 1: Generate Data', count=5)
        task2 = FlakyTask(name='Step 2: Flaky Check', failureRate=0.7, maxRetries=3, retryDelaySeconds=2)
        task3 = DataProcessorTask(name='Step 3: Process Data', multiplier=10)
        retryMap = {'FlakyTask': ChainRetryBehavior.SKIP_TASK}
        chain = TaskChain(name=name, tasks=[task1, task2, task3], description='A demo chain showing context sharing and retry logic', retryBehaviorMap=retryMap)
        return chain

    @staticmethod
    def createRetryDemoChain(name: str = 'Retry Demo Chain') -> TaskChain:
        """
        Creates a chain to demonstrate auto-retry and delayed retry.
        1. ConsistentlyFailingTask: Fails twice, succeeds on the third try (task-level retry).
        2. FlakyTask: High failure rate, configured to retry the whole chain on failure.
        """
        task1 = ConsistentlyFailingTask(name='Step 1: Auto-Retry Task', failuresBeforeSuccess=2, maxRetries=2, retryDelaySeconds=10)
        task2 = FlakyTask(name='Step 2: Chain-Retry Task', failureRate=0.8, maxRetries=0, retryDelaySeconds=5)
        task3 = DataGeneratorTask(name='Step 3: Final Step', count=3)
        retryMap = {'FlakyTask': ChainRetryBehavior.RETRY_CHAIN, 'ConsistentlyFailingTask': ChainRetryBehavior.RETRY_TASK}
        chain = TaskChain(
            name=name,
            tasks=[task1, task2, task3],
            description='Demonstrates task-level and chain-level retries with delays.',
            retryBehaviorMap=retryMap,
            maxRetries=2,
            retryDelaySeconds=5,
        )
        return chain
