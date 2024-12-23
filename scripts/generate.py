#!/usr/bin/env python3

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
#              * -  Copyright © 2024 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

import argparse
import os

TEMPLATES = {
    'controller': '''from core import BaseController

class {name}Controller(BaseController):
    def __init__(self):
        self.slot_map = {{
            # Add your slot mappings here
            # 'event_name': ['widget_name', 'signal_name']
        }}
        super().__init__()
        
    def setupUi(self):
        # Setup your UI components here
        pass
''',
    
    'handler': '''from core import Subscriber

class {name}Handler(Subscriber):
    def __init__(self, controller):
        self.controller = controller
        events = [
            # Add your events here
        ]
        super().__init__(events)
        
    # Add your event handlers here
    # def on_event_name(self, data=None):
    #     pass
''',
    
    'service': '''class {name}Service:
    def __init__(self):
        pass
    
    # Add your service methods here
''',
    
    'component': '''from core import BaseComponent

class {name}Component(BaseComponent):
    def __init__(self):
        super().__init__()
        
    def setupUi(self):
        # Setup your component UI here
        pass
'''
}


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created {path}")


def generate_controller(name, base_path):
    # Create controller
    controller_path = os.path.join(base_path, 'windows', name.lower(), f'{name}Controller.py')
    create_file(controller_path, TEMPLATES['controller'].format(name=name))
    
    # Create handler
    handler_path = os.path.join(base_path, 'windows', name.lower(), 'handlers', f'{name}Handler.py')
    create_file(handler_path, TEMPLATES['handler'].format(name=name))
    
    # Create UI directory
    ui_dir = os.path.join(base_path, 'windows', name.lower(), 'ui')
    os.makedirs(ui_dir, exist_ok=True)


def generate_service(name, base_path):
    service_path = os.path.join(base_path, 'services', f'{name}Service.py')
    create_file(service_path, TEMPLATES['service'].format(name=name))


def generate_component(name, base_path):
    component_path = os.path.join(base_path, 'windows', 'components', name.lower(), f'{name}Component.py')
    create_file(component_path, TEMPLATES['component'].format(name=name))
    
    # Create UI directory
    ui_dir = os.path.join(base_path, 'windows', 'components', name.lower(), 'ui')
    os.makedirs(ui_dir, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description='Generate Qt app components')
    parser.add_argument('type', choices=['controller', 'service', 'component'],
                        help='Type of component to generate')
    parser.add_argument('name', help='Name of the component')
    
    args = parser.parse_args()
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if args.type == 'controller':
        generate_controller(args.name, base_path)
    elif args.type == 'service':
        generate_service(args.name, base_path)
    elif args.type == 'component':
        generate_component(args.name, base_path)


if __name__ == '__main__':
    main()
