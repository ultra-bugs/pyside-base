#!/usr/bin/env python3

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
import argparse
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core import Config, logger


def main():
    """Set application name and version"""
    parser = argparse.ArgumentParser(description='Set application name and version')
    parser.add_argument('--name', help='Application name')
    parser.add_argument('--version', help='Application version')
    args = parser.parse_args()
    if not args.name and not args.version:
        parser.print_help()
        return
    try:
        config = Config()
        config.load()
        if args.name:
            config.set('app.name', args.name)
            logger.info(f'Application name set to: {args.name}')
        if args.version:
            config.set('app.version', args.version)
            logger.info(f'Application version set to: {args.version}')
        config.save()
        from core.Utils import PathHelper
        if not PathHelper.isFileExists('.env'):
            env_example_path = project_root / '.env.example'
            env_path = project_root / '.env'
            try:
                env_path.write_text(env_example_path.read_text())
                logger.info(f'Copied {env_example_path} to {env_path}')
            except Exception as copy_e:
                logger.error(f'Failed to copy .env.example to .env: {copy_e}')
    except Exception as e:
        logger.error(f'Failed to set app info: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
