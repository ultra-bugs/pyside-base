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
"""
Task Generator - Wrapper script to easily create new tasks and steps.
This script will:
1. Create a new task or step
2. Update the __init__.py files to include the new elements
"""

import argparse
import subprocess
from pathlib import Path


def generate_and_update(item_type, name, description):
    """Generate a task or step and update imports"""
    # Validate the name
    if not name[0].isupper():
        print(
            f"WARNING: Name should start with uppercase letter. Converting '{name}' to '{name[0].upper() + name[1:]}'")
        name = name[0].upper() + name[1:]
    
    # Get the base path
    base_path = Path(__file__).parent
    
    # Run the generate.py script
    generate_script = base_path / "generate.py"
    generate_cmd = ["python", str(generate_script), item_type, name, "--description", description]
    
    print(f"Creating new {item_type}: {name}")
    try:
        result = subprocess.run(generate_cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error generating {item_type}: {e}")
        print(e.stderr)
        return False
    
    # Update imports
    update_script = base_path / "update_task_imports.py"
    update_cmd = ["python", str(update_script)]
    
    print("Updating imports...")
    try:
        result = subprocess.run(update_cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error updating imports: {e}")
        print(e.stderr)
        return False
    
    # Show success message and next steps
    if item_type == "task":
        print("\nTask created successfully!")
        print(f"You can now use your task by importing it:")
        print(f"  from tasks import {name}Task")
        print(f"\nTo edit your task, open: tasks/{name}Task.py")
    else:  # task_step
        print("\nTask step created successfully!")
        print(f"You can now use your step by importing it:")
        print(f"  from tasks.steps import {name}Step")
        print(f"\nTo edit your step, open: tasks/steps/{name}Step.py")
    
    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate a task or task step')
    parser.add_argument('type', choices=['task', 'step'], help='Type of item to generate')
    parser.add_argument('name', help='Name of the task or step (will be converted to UpperCamelCase)')
    parser.add_argument('--description', '-d', help='Description', default='Custom implementation')
    
    args = parser.parse_args()
    
    # Map 'step' to 'task_step' for the generate.py script
    item_type = 'task_step' if args.type == 'step' else args.type
    
    # Generate and update
    generate_and_update(item_type, args.name, args.description)


if __name__ == '__main__':
    main()
