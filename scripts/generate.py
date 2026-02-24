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

import argparse
import os

TEMPLATES = {
    'controller': "from core import BaseController\n\nclass {name}Controller(BaseController):\n    def __init__(self):\n        self.slot_map = {{\n            # Add your slot mappings here\n            # 'event_name': ['widget_name', 'signal_name']\n        }}\n        super().__init__()\n        \n    def setupUi(self):\n        # Setup your UI components here\n        pass\n",
    'handler': 'from core import Subscriber\n\nclass {name}Handler(Subscriber):\n    def __init__(self, widgetManager, events):\n        self.widgetManager = widgetManager\n        self.controller = widgetManager.controller\n        super().__init__(events)\n    # Add your event handlers here\n    # def on_event_name(self, data=None):\n    #     pass\n',
    'service': 'class {name}Service:\n    def __init__(self):\n        pass\n    \n    # Add your service methods here\n',
    'component': 'from core import BaseComponent\n\nclass {name}Component(BaseComponent):\n    def __init__(self):\n        super().__init__()\n        \n    def setupUi(self):\n        # Setup your component UI here\n        pass\n',
    'task': 'from core import Task, TaskStep, PrintStep\n\nclass {name}Task(Task):\n    """\n    {description}\n    """\n    def __init__(self, name="{name}", description="{description}"):\n        super().__init__(name, description)\n        \n        # Initialize task steps\n        self._setup_steps()\n        \n    def _setup_steps(self):\n        """Set up the task steps"""\n        # Example step\n        self.add_step(PrintStep("Starting {name} task"))\n        \n        # TODO: Add your task steps here\n        \n        # Final step\n        self.add_step(PrintStep("{name} task completed"))\n',
    'task_step': 'from core import TaskStep\n\nclass {name}Step(TaskStep):\n    """\n    {description}\n    \n    Attributes:\n        output_variable (str): Name of the variable to store the step result in\n    """\n    def __init__(self, param1=None, param2=None, output_var=None):\n        super().__init__("{name}", "{description}")\n        self.param1 = param1\n        self.param2 = param2\n        self.output_variable = output_var\n        \n    def execute(self, context, variables):\n        """\n        Execute the task step\n        \n        Args:\n            context (dict): Execution context\n            variables (dict): Task variables\n            \n        Returns:\n            Any: Result of the step execution\n        """\n        # TODO: Implement your step logic here\n        result = f"Executed {self.__class__.__name__} with params: {self.param1}, {self.param2}"\n        \n        # You can access task variables\n        # existing_value = variables.get("some_key", "default")\n        \n        # You can also access task object if provided in context\n        # task = context.get(\'task\')\n        # if task:\n        #     task.signals.progress.emit(task.id, 50)  # Report 50% progress\n        \n        return result\n',
}

TEMPLATES['provider'] = '''from core.contracts.ServiceProvider import ServiceProvider


class {name}Provider(ServiceProvider):
    """{description}"""

    def register(self):
        # self.ctx.registerService('serviceName', ServiceInstance())
        pass
'''


def createFile(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f'Created {path}')


def generateController(name, base_path):
    controller_path = os.path.join(base_path, 'windows', name.lower(), f'{name}Controller.py')
    createFile(controller_path, TEMPLATES['controller'].format(name=name))
    handler_path = os.path.join(base_path, 'windows', name.lower(), 'handlers', f'{name}Handler.py')
    createFile(handler_path, TEMPLATES['handler'].format(name=name))
    uiDir = os.path.join(base_path, 'windows', name.lower(), 'ui')
    os.makedirs(uiDir, exist_ok=True)


def generateService(name, base_path):
    servicePath = os.path.join(base_path, 'services', f'{name}Service.py')
    createFile(servicePath, TEMPLATES['service'].format(name=name))


def generateComponent(name, base_path):
    componentPath = os.path.join(base_path, 'windows', 'components', name.lower(), f'{name}Component.py')
    createFile(componentPath, TEMPLATES['component'].format(name=name))
    uiDir = os.path.join(base_path, 'windows', 'components', name.lower(), 'ui')
    os.makedirs(uiDir, exist_ok=True)


def generateTask(name, description, base_path):
    tasksDir = os.path.join(base_path, 'tasks')
    os.makedirs(tasksDir, exist_ok=True)
    taskPath = os.path.join(tasksDir, f'{name}Task.py')
    createFile(taskPath, TEMPLATES['task'].format(name=name, description=description))
    initPath = os.path.join(tasksDir, '__init__.py')
    if not os.path.exists(initPath):
        with open(initPath, 'w') as f:
            f.write('# Tasks package\n')


def generateTaskStep(name, description, base_path):
    stepsDir = os.path.join(base_path, 'tasks', 'steps')
    os.makedirs(stepsDir, exist_ok=True)
    stepPath = os.path.join(stepsDir, f'{name}Step.py')
    createFile(stepPath, TEMPLATES['task_step'].format(name=name, description=description))
    initPath = os.path.join(stepsDir, '__init__.py')
    if not os.path.exists(initPath):
        with open(initPath, 'w') as f:
            f.write('# Task steps package\n')


def generateProvider(name, description, base_path):
    providersDir = os.path.join(base_path, 'providers')
    os.makedirs(providersDir, exist_ok=True)
    providerPath = os.path.join(providersDir, f'{name}Provider.py')
    createFile(providerPath, TEMPLATES['provider'].format(name=name, description=description))
    initPath = os.path.join(providersDir, '__init__.py')
    if not os.path.exists(initPath):
        with open(initPath, 'w') as f:
            f.write('# Providers package\n')
    print(f'\nNext: run "pixi run compile-providers" to update the manifest.')


def main():
    parser = argparse.ArgumentParser(description='Generate Qt app components')
    parser.add_argument('type', choices=['controller', 'service', 'component', 'task', 'task_step', 'provider'], help='Type of component to generate')
    parser.add_argument('name', help='Name of the component')
    parser.add_argument('--description', '-d', help='Description (used for tasks, task steps, and providers)', default='Custom implementation')
    args = parser.parse_args()
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app')
    if args.type == 'controller':
        generateController(args.name, base_path)
    elif args.type == 'service':
        generateService(args.name, base_path)
    elif args.type == 'component':
        generateComponent(args.name, base_path)
    elif args.type == 'task':
        generateTask(args.name, args.description, base_path)
    elif args.type == 'task_step':
        generateTaskStep(args.name, args.description, base_path)
    elif args.type == 'provider':
        generateProvider(args.name, args.description, base_path)


if __name__ == '__main__':
    main()
