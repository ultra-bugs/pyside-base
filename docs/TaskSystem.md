## Task System

Base app cung cấp hệ thống quản lý task mạnh mẽ với khả năng thực thi đồng thời và theo lịch trình. Hệ thống này lý
tưởng cho các ứng dụng cần thực hiện các hoạt động tốn thời gian mà không block UI.

### Các thành phần chính

1. **TaskManager**: Quản lý việc thực thi các task và điều phối thread pool
2. **Task**: Đại diện cho một công việc cần thực hiện, bao gồm một chuỗi các steps
3. **TaskStep**: Đơn vị xử lý cơ bản trong một task
4. **TaskStatus**: Enum định nghĩa trạng thái của task (PENDING, RUNNING, COMPLETED, FAILED)
5. **TaskSignals**: Signals Qt để báo cáo tiến trình và kết quả
6. **TaskSchedulerService**: Dịch vụ lập lịch cho các task

### Các loại TaskStep có sẵn

- **PrintStep**: In thông báo (hữu ích cho debugging)
- **SetVariableStep**: Thiết lập biến trong context của task
- **ConditionStep**: Thực hiện các steps khác nhau dựa trên điều kiện
- **LoopStep**: Lặp lại một tập hợp các steps
- **SleepStep**: Giả lập một task tốn thời gian bằng cách ngủ
- **ComputeIntensiveStep**: Giả lập một task tiêu tốn CPU

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

### Cách sử dụng Task System

#### 1. Tạo và chạy một task đơn giản:

```python
from core import TaskManager, Task, PrintStep, SetVariableStep

# Khởi tạo TaskManager
task_manager = TaskManager()

# Tạo task
task = task_manager.create_task("My Task", "Task description")

# Thêm các steps
task.add_step(PrintStep("Task is running..."))
task.add_step(SetVariableStep("result", "Complete"))
task.add_step(PrintStep("Result: {result}"))

# Đăng ký signals để theo dõi tiến trình
task.signals.started.connect(lambda task_id: print(f"Task {task_id} started"))
task.signals.progress.connect(lambda task_id, progress: print(f"Task {task_id}: {progress}%"))
task.signals.completed.connect(lambda task_id, result: print(f"Task {task_id} completed"))
task.signals.failed.connect(lambda task_id, error: print(f"Task {task_id} failed: {error}"))

# Chạy task
task_manager.run_task(task)
```

#### 2. Sử dụng điều kiện trong task:

```python
from core import ConditionStep

# Tạo steps cho điều kiện true và false
true_steps = [
    PrintStep("Condition is TRUE"),
    SetVariableStep("status", "Success")
]

false_steps = [
    PrintStep("Condition is FALSE"),
    SetVariableStep("status", "Failed")
]

# Thiết lập biến điều kiện
task.add_step(SetVariableStep("test_condition", True))

# Thêm conditional step
task.add_step(ConditionStep("test_condition", true_steps, false_steps))
```

#### 3. Sử dụng vòng lặp trong task:

```python
from core import LoopStep

# Tạo steps cho vòng lặp
loop_steps = [
    PrintStep("Loop iteration {loop_index}"),
    SetVariableStep("temp", "Value {loop_index}")
]

# Thêm loop step (lặp lại 5 lần)
task.add_step(LoopStep(5, loop_steps))
```

#### 4. Chạy nhiều task đồng thời:

```python
# Tạo nhiều task
tasks = []
for i in range(5):
    task = task_manager.create_task(f"Task {i}", f"Description {i}")
    task.add_step(SleepStep(3))  # Giả lập task tốn thời gian
    tasks.append(task)

# Chạy tất cả task đồng thời
task_manager.run_tasks(tasks)

# Kiểm tra số lượng task đang chạy
active_count = task_manager.get_active_tasks_count()
print(f"Active tasks: {active_count}")
```

#### 5. Lập lịch chạy task:

```python
from services.TaskSchedulerService import TaskSchedulerService
import time

# Khởi tạo TaskSchedulerService
scheduler_service = TaskSchedulerService(task_manager)
scheduler_service.start()

# Tạo task
task = task_manager.create_task("Scheduled Task", "Runs after 10 seconds")
task.add_step(PrintStep("Scheduled task running"))

# Lập lịch để chạy sau 10 giây
run_at = time.time() + 10
scheduler_service.add_schedule(task, run_at)

# Lập lịch để chạy lặp lại mỗi 60 giây
repeat_task = task_manager.create_task("Repeating Task", "Runs every minute")
repeat_task.add_step(PrintStep("Repeating task running"))
scheduler_service.add_schedule(repeat_task, time.time() + 5, 60)
```

### Custom TaskStep

Bạn có thể tạo TaskStep tùy chỉnh bằng cách kế thừa từ lớp TaskStep:

```python
from core import TaskStep


class MyCustomStep(TaskStep):
    def __init__(self, param1, param2):
        super().__init__("CustomStep", f"Custom step with {param1} and {param2}")
        self.param1 = param1
        self.param2 = param2
    
    def execute(self, context, variables):
        # Logic xử lý
        result = self.param1 + self.param2
        # Có thể sử dụng variables để truy cập biến trong task
        if "existing_var" in variables:
            result += variables["existing_var"]
        return result
```
