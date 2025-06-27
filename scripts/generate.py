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
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

#
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
    def __init__(self, widget_manager, events):
        self.widget_manager = widget_manager
        self.controller = widget_manager.controller
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
''',
    
    'task': '''from core import Task, TaskStep, PrintStep

class {name}Task(Task):
    """
    {description}
    """
    def __init__(self, name="{name}", description="{description}"):
        super().__init__(name, description)
        
        # Initialize task steps
        self._setup_steps()
        
    def _setup_steps(self):
        """Set up the task steps"""
        # Example step
        self.add_step(PrintStep("Starting {name} task"))
        
        # TODO: Add your task steps here
        
        # Final step
        self.add_step(PrintStep("{name} task completed"))
''',
    
    'task_step': '''from core import TaskStep

class {name}Step(TaskStep):
    """
    {description}
    
    Attributes:
        output_variable (str): Name of the variable to store the step result in
    """
    def __init__(self, param1=None, param2=None, output_var=None):
        super().__init__("{name}", "{description}")
        self.param1 = param1
        self.param2 = param2
        self.output_variable = output_var
        
    def execute(self, context, variables):
        """
        Execute the task step
        
        Args:
            context (dict): Execution context
            variables (dict): Task variables
            
        Returns:
            Any: Result of the step execution
        """
        # TODO: Implement your step logic here
        result = f"Executed {self.__class__.__name__} with params: {self.param1}, {self.param2}"
        
        # You can access task variables
        # existing_value = variables.get("some_key", "default")
        
        # You can also access task object if provided in context
        # task = context.get('task')
        # if task:
        #     task.signals.progress.emit(task.id, 50)  # Report 50% progress
        
        return result
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


def generate_task(name, description, base_path):
    # Create tasks directory if it doesn't exist
    tasks_dir = os.path.join(base_path, 'tasks')
    os.makedirs(tasks_dir, exist_ok=True)
    
    # Create task file
    task_path = os.path.join(tasks_dir, f'{name}Task.py')
    create_file(task_path, TEMPLATES['task'].format(name=name, description=description))
    
    # Create __init__.py if it doesn't exist
    init_path = os.path.join(tasks_dir, '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write('# Tasks package\n')


def generate_task_step(name, description, base_path):
    # Create task_steps directory if it doesn't exist
    steps_dir = os.path.join(base_path, 'tasks', 'steps')
    os.makedirs(steps_dir, exist_ok=True)
    
    # Create task step file
    step_path = os.path.join(steps_dir, f'{name}Step.py')
    create_file(step_path, TEMPLATES['task_step'].format(name=name, description=description))
    
    # Create __init__.py if it doesn't exist
    init_path = os.path.join(steps_dir, '__init__.py')
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write('# Task steps package\n')


def main():
    parser = argparse.ArgumentParser(description='Generate Qt app components')
    parser.add_argument('type', choices=['controller', 'service', 'component', 'task', 'task_step'],
                        help='Type of component to generate')
    parser.add_argument('name', help='Name of the component')
    parser.add_argument('--description', '-d',
                        help='Description (used for tasks and task steps)',
                        default='Custom implementation')
    
    args = parser.parse_args()
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if args.type == 'controller':
        generate_controller(args.name, base_path)
    elif args.type == 'service':
        generate_service(args.name, base_path)
    elif args.type == 'component':
        generate_component(args.name, base_path)
    elif args.type == 'task':
        generate_task(args.name, args.description, base_path)
    elif args.type == 'task_step':
        generate_task_step(args.name, args.description, base_path)


if __name__ == '__main__':
    main()
