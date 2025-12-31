"""Quick demo of Todo App functionality."""

import sys
sys.path.insert(0, 'src')

from services.storage import add_task, get_all_tasks, toggle_complete
from cli.display import display_tasks, display_success_message

print("=== Todo App Demo ===\n")

# Add some tasks
task1 = add_task("Buy groceries", "Milk, eggs, bread")
display_success_message(f"Added: '{task1.title}'")

task2 = add_task("Finish project", "Complete the todo app")
display_success_message(f"Added: '{task2.title}'")

task3 = add_task("Go for a run", "5k around the park")
display_success_message(f"Added: '{task3.title}'")

# Display all tasks
print("\n=== All Tasks ===")
display_tasks(get_all_tasks())

# Mark one as complete
toggle_complete(1)
toggle_complete(3)

print("\n=== After Marking Complete ===")
display_tasks(get_all_tasks())
