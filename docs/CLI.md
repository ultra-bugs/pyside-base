## Công cụ CLI

### Generate Components

```bash
python scripts/generate.py controller MyController  # Tạo controller mới
python scripts/generate.py service MyService       # Tạo service mới
python scripts/generate.py component MyComponent   # Tạo component mới
```

### Generate Tasks and Steps

```bash
# Tạo task tùy chỉnh (cách 1 - trực tiếp)
python scripts/generate.py task MyCustom --description "Task mô tả chức năng tùy chỉnh"

# Tạo task step tùy chỉnh (cách 1 - trực tiếp)
python scripts/generate.py task_step MyCustom --description "Step thực hiện chức năng tùy chỉnh"

# Sử dụng task_generator.py (cách 2 - được khuyến nghị)
python scripts/task_generator.py task MyTask --description "Task mô tả"
python scripts/task_generator.py step MyStep --description "Step mô tả"

# Sau khi tạo task/step mới, cập nhật imports
python scripts/update_task_imports.py
```

Khi sử dụng `task_generator.py`, các imports sẽ tự động được cập nhật. Bạn có thể sử dụng các task và step mới:

```python
# Sử dụng task
from tasks import MyTaskTask

task = MyTaskTask()
task_manager.run_task(task)

# Sử dụng step
from tasks.steps import MyStepStep

task.add_step(MyStepStep(param1="value", param2=123))
```

### Compile UI Files

```bash
python scripts/compile_ui.py  # Compile tất cả UI và QRC files
```

### Set App Info

```bash
python scripts/set_app_info.py --name "My App"     # Set tên ứng dụng
python scripts/set_app_info.py --version "2.0.0"   # Set version
python scripts/set_app_info.py --name "My App" --version "2.0.0"  # Set cả hai
```
