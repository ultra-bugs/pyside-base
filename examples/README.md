# Task System Examples

Thư mục này chứa các ví dụ về cách sử dụng Task System trong ứng dụng Base Qt. Các ví dụ này minh họa các tính năng và
khả năng của hệ thống quản lý tác vụ.

## Danh sách ví dụ

### 1. task_usage_example.py

Ví dụ này minh họa cách:

- Tạo một lớp Task tùy chỉnh thông qua mã thủ công
- Tạo các lớp TaskStep tùy chỉnh thông qua mã thủ công
- Kết nối các signal handlers để theo dõi tiến trình của task
- Chạy task với TaskManager và truyền context

Để chạy ví dụ này:

```bash
python examples/task_usage_example.py
```

## Cách tạo Task và Step mới

### Sử dụng generator CLI

Bạn có thể tạo các Task và TaskStep mới bằng công cụ CLI cung cấp:

```bash
# Tạo task mới
python scripts/task_generator.py task MyTask --description "Mô tả task của tôi"

# Tạo step mới
python scripts/task_generator.py step MyStep --description "Mô tả step của tôi"
```

Sau khi tạo, bạn có thể import và sử dụng chúng:

```python
from tasks import MyTaskTask
from tasks.steps import MyStepStep

# Sử dụng task
task = MyTaskTask()

# Sử dụng step trong task
task.add_step(MyStepStep(param1="value", param2=123))
```

### Tạo thủ công

Bạn cũng có thể tạo Task và TaskStep thủ công như trong ví dụ `task_usage_example.py`:

```python
# Tạo Task tùy chỉnh
class MyCustomTask(Task):
    def __init__(self):
        super().__init__("My Task", "My task description")
        self._setup_steps()
    
    def _setup_steps(self):
        self.add_step(PrintStep("Task is running"))
        self.add_step(MyCustomStep())


# Tạo TaskStep tùy chỉnh
class MyCustomStep(TaskStep):
    def __init__(self):
        super().__init__("CustomStep", "My custom step")
    
    def execute(self, context, variables):
        # Thực hiện tác vụ
        return "Result"
```

## Mô hình luồng dữ liệu trong TaskStep

1. **Input**: Dữ liệu vào từ `variables` (được truyền từ Task)
2. **Xử lý**: Thực hiện trong phương thức `execute()`
3. **Output**: Giá trị trả về từ `execute()` được lưu vào biến được chỉ định bởi `self.output_variable`
4. **Báo cáo tiến trình**: Thông qua `task.signals.progress.emit(task.id, percentage)`

## Tài liệu tham khảo thêm

Xem mã nguồn trong `core/TaskSystem.py`. 
