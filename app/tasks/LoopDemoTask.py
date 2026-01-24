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

#
import time
from typing import Any, Dict

from core.Logging import logger
from core.taskSystem.AbstractTask import AbstractTask


class LoopDemoTask(AbstractTask):
    """Task that runs a simple loop with progress updates."""

    def __init__(self, name: str = 'Loop Task', loopCount: int = 5, delaySeconds: float = 0.2, **kwargs):
        super().__init__(name=name, **kwargs)
        self.loopCount = max(1, int(loopCount))
        self.delaySeconds = float(delaySeconds)
        self._logger = logger.bind(component='TaskSystem')

    def handle(self) -> None:
        if self.loopCount <= 0:
            self.loopCount = 1
        for i in range(self.loopCount):
            if self.isStopped():
                return
            pct = int(((i + 1) / self.loopCount) * 100)
            self._logger.info(f'{self.name}: iteration {i + 1}/{self.loopCount}')
            self.setProgress(min(99, pct))
            time.sleep(self.delaySeconds)
        self.setProgress(100)
        self.result = {'iterations': self.loopCount}

    def _performCancellationCleanup(self) -> None:
        pass

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({'loopCount': self.loopCount, 'delaySeconds': self.delaySeconds})
        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'LoopDemoTask':
        return cls(
            name=data.get('name', 'Loop Task'),
            loopCount=int(data.get('loopCount', 5)),
            delaySeconds=float(data.get('delaySeconds', 0.2)),
            description=data.get('description', ''),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
        )
