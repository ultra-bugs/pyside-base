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
#              * -  Copyright © 2026 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *
import time
from typing import Any, Dict

from core.Logging import logger
from core.taskSystem.AbstractTask import AbstractTask


class SimpleDemoTask(AbstractTask):
    """A simple demonstration task that logs messages and updates progress."""

    def __init__(self, name: str = 'Simple Task', message: str = 'Task is running...', **kwargs):
        super().__init__(name=name, **kwargs)
        self.message = message
        self._shouldStop = False
        self._logger = logger.bind(component='TaskSystem')

    def handle(self) -> None:
        self._logger.info(f'{self.name}: start')
        self.setProgress(0)
        steps = [10, 30, 60, 100]
        for p in steps:
            if self.isStopped():
                return
            self._logger.info(f'{self.name}: {self.message}')
            self.setProgress(p)
            time.sleep(0.2)
        self.result = {'ok': True}

    def _performCancellationCleanup(self) -> None:
        # No resources to cleanup in this demo
        pass

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({'message': self.message})
        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'SimpleDemoTask':
        return cls(
            name=data.get('name', 'Simple Task'),
            message=data.get('message', 'Task is running...'),
            description=data.get('description', ''),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
        )
