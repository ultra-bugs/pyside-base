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

import math
import time
from typing import Any, Dict
from core.Logging import logger
from core.taskSystem.AbstractTask import AbstractTask


class CpuIntensiveDemoTask(AbstractTask):
    """CPU-intensive task that performs a number of operations and reports progress."""

    def __init__(self, name: str = 'CPU Intensive Task', complexity: int = 5000000, **kwargs):
        super().__init__(name=name, **kwargs)
        self.complexity = max(1000, int(complexity))
        self._logger = logger.bind(component='TaskSystem')

    def handle(self) -> None:
        ops = self.complexity
        reportEvery = max(ops // 20, 1)
        acc = 0.0
        for i in range(ops):
            if self.isStopped():
                return
            acc += math.sin(i % 360) * math.cos(i * 2 % 360)
            if (i + 1) % reportEvery == 0:
                pct = int((i + 1) / ops * 100)
                self.setProgress(min(99, pct))
        self.result = {'acc': acc, 'ops': ops}
        self.setProgress(100)

    def _performCancellationCleanup(self) -> None:
        pass

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({'complexity': self.complexity})
        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'CpuIntensiveDemoTask':
        return cls(
            name=data.get('name', 'CPU Intensive Task'),
            complexity=int(data.get('complexity', 5000000)),
            description=data.get('description', ''),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
        )
