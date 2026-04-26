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
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class SinkEntry:
    id: str
    sink: Any  # path str, callable, widget, sys.stderr
    level: str = 'DEBUG'
    enabled: bool = True
    position: int = 0
    filter: Optional[Callable] = None
    kwargs: dict = field(default_factory=dict)
    loguru_id: Optional[int] = field(default=None, repr=False)
