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
import sys
from pathlib import Path

# CRITICAL: Setup sys.path BEFORE any app imports
_PACKAGES_TO_LOADS = []
projectRoot = Path(__file__).parent
sys.path.append(str(projectRoot))
for relative in _PACKAGES_TO_LOADS:
    pAbs = projectRoot / "packages" / relative
    if pAbs.exists():
        sys.path.append(str(pAbs))
        print(f"Added to sys.path: {pAbs}")
    else:
        print(f"WARNING: Package path not found: {pAbs}")
        

def noop():
    pass
