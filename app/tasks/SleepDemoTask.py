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


class SleepDemoTask(AbstractTask):
    """Task that sleeps for a duration, updating progress periodically."""

    def __init__(self, name: str = 'Sleep Task', durationSeconds: int = 5, **kwargs):
        super().__init__(name=name, **kwargs)
        self.durationSeconds = max(1, int(durationSeconds))
        self._logger = logger.bind(component='TaskSystem')

    def handle(self) -> None:
        total = self.durationSeconds
        for i in range(total):
            if self.isStopped():
                return
            pct = int(((i + 1) / total) * 100)
            self._logger.info(f'{self.name}: sleeping {i + 1}/{total}s')
            self.setProgress(min(99, pct))
            time.sleep(1.0)
        self.setProgress(100)
        self.result = {'sleptSeconds': total}

    def _performCancellationCleanup(self) -> None:
        pass

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({'durationSeconds': self.durationSeconds})
        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'SleepDemoTask':
        return cls(
            name=data.get('name', 'Sleep Task'),
            durationSeconds=int(data.get('durationSeconds', 5)),
            description=data.get('description', ''),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
        )
