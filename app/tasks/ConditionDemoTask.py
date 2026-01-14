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


class ConditionDemoTask(AbstractTask):
    """Task with a simple conditional branch."""

    def __init__(self, name: str = 'Condition Task', testCondition: bool = True, **kwargs):
        super().__init__(name=name, **kwargs)
        self.testCondition = testCondition
        self._logger = logger.bind(component='TaskSystem')

    def handle(self) -> None:
        self._logger.info(f"{self.name}: evaluating condition = {self.testCondition}")
        self.setProgress(10)
        time.sleep(0.1)
        if self.isStopped():
            return
        if self.testCondition:
            self._logger.info("Condition is TRUE")
            self.result = { 'result': 'Success' }
        else:
            self._logger.info("Condition is FALSE")
            self.result = { 'result': 'Failed' }
        self.setProgress(100)

    def _performCancellationCleanup(self) -> None:
        pass

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({'testCondition': self.testCondition})
        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'ConditionDemoTask':
        return cls(
            name=data.get('name', 'Condition Task'),
            testCondition=data.get('testCondition', True),
            description=data.get('description', ''),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
        )
