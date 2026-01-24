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
import subprocess
from typing import Any, Dict, List, Optional

from core.Logging import logger
from core.taskSystem.AbstractTask import AbstractTask


class AdbCommandTask(AbstractTask):
    """Execute an ADB command and capture stdout/stderr/exit code."""

    def __init__(self, name: str = 'ADB Command', command: str = 'devices', deviceSerial: Optional[str] = None, timeoutSeconds: Optional[int] = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.command = command
        self.timeoutSeconds = timeoutSeconds
        self.deviceSerial = deviceSerial
        self._proc: Optional[subprocess.Popen] = None
        self._logger = logger.bind(component='TaskSystem')

    def _build_cmd(self) -> List[str]:
        base = ['adb']
        if self.deviceSerial:
            base += ['-s', str(self.deviceSerial)]
        # Split the command by spaces (simple demo); for complex cases, pass list directly
        parts = [p for p in self.command.split(' ') if p]
        return base + parts

    def handle(self) -> None:
        cmd = self._build_cmd()
        self._logger.info(f'{self.name}: running -> {" ".join(cmd)}')
        self.setProgress(5)
        try:
            self._proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            try:
                out, err = self._proc.communicate(timeout=self.timeoutSeconds)
            except subprocess.TimeoutExpired:
                self._logger.error(f'{self.name}: timeout after {self.timeoutSeconds}s; terminating')
                self._proc.kill()
                out, err = self._proc.communicate()
            rc = self._proc.returncode
            self._logger.info(f'{self.name}: exit code {rc}')
            self.result = {'exitCode': rc, 'stdout': out, 'stderr': err}
            # Progress to 100 when done
            self.setProgress(100)
            if rc != 0:
                # Mark failed but still return result payload
                self.fail(f'ADB exited with code {rc}')
        finally:
            self._proc = None

    def _performCancellationCleanup(self) -> None:
        if self._proc and self._proc.poll() is None:
            try:
                self._logger.warning(f'{self.name}: cancelling → killing subprocess')
                self._proc.kill()
            except Exception as e:
                self._logger.error(f'{self.name}: error killing subprocess: {e}')

    def serialize(self) -> Dict[str, Any]:
        data = super().serialize()
        data.update({'command': self.command, 'timeoutSeconds': self.timeoutSeconds, 'deviceSerial': self.deviceSerial})
        return data

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'AdbCommandTask':
        return cls(
            name=data.get('name', 'ADB Command'),
            command=data.get('command', 'devices'),
            deviceSerial=data.get('deviceSerial'),
            timeoutSeconds=data.get('timeoutSeconds'),
            description=data.get('description', ''),
            isPersistent=data.get('isPersistent', False),
            maxRetries=data.get('maxRetries', 0),
            retryDelaySeconds=data.get('retryDelaySeconds', 5),
            failSilently=data.get('failSilently', False),
        )
