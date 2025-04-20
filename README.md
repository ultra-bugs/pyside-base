# Base Qt Application

Đây là một base application được xây dựng trên PySide6, sử dụng Observer Pattern và Qt Designer. Base app này giúp bạn
nhanh chóng khởi tạo một ứng dụng Qt mới với cấu trúc chuẩn và các công cụ hỗ trợ.

## Cấu trúc thư mục

```
base/
├── assets/           # Resources (images, sounds, translations)
│   └── icon.png     # Default application icon
├── core/            # Core classes and design patterns
├── data/            # User data and embedded app data
│   ├── config/     # Configuration files
│   └── logs/       # Log files
├── scripts/         # CLI tools
├── services/        # Service classes
├── vendor/          # Third-party resources
├── windows/         # Views, controllers and event handlers
│   ├── components/  # Reusable UI components
│   └── main/        # Main window
└── plugins/         # App plugins
```

## Các thành phần chính

### 1. Controller

- Kế thừa từ `BaseController`
- Quản lý UI và xử lý tương tác người dùng
- Sử dụng slot_map để kết nối signals và slots
- Được tạo tự động bằng CLI tool

### 2. Handler

- Kế thừa từ `Subscriber`
- Xử lý các events từ controller
- Được tạo tự động cùng với controller

### 3. Service

- Xử lý business logic
- Độc lập với UI
- Có thể được sử dụng bởi nhiều controllers

### 4. Component

- UI components có thể tái sử dụng
- Kế thừa từ `BaseComponent`
- Có thể được nhúng vào nhiều windows khác nhau

### 5. Widget Manager

- Quản lý widgets trong controllers và components
- Hỗ trợ truy cập widgets theo dot notation (ví dụ: 'parent.child')
- Lưu trữ widget state vào config
- Hỗ trợ thực thi actions với signal suppression

Ví dụ sử dụng Widget Manager:

```python
# Trong controller
self.widget_manager = WidgetManager(self)

# Truy cập widget
widget = self.widget_manager.get('myWidget')
nested_widget = self.widget_manager.get('parent.child')

# Set giá trị và lưu vào config
self.widget_manager.set('myWidget', value, save_to_config=True)

# Thực thi action với signal suppression
self.widget_manager.do_action_suppress_signal('myWidget', lambda w: w.setValue(100))
```

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

## Theme

App sử dụng QDarkTheme với 3 chế độ:

- `auto`: Tự động theo system theme (mặc định)
- `light`: Light theme
- `dark`: Dark theme

Thay đổi theme:

```python
from core import Config
import qdarktheme

config = Config()
config.set("ui.theme", "dark")  # hoặc "light" hoặc "auto"
config.save()
qdarktheme.setup_theme(config.get("ui.theme"))
```

## Observer Pattern

Base app sử dụng Observer Pattern để xử lý events:

1. **Publisher**: Phát ra events
    - Được implement như một singleton
    - Kết nối Qt signals với events system

2. **Subscriber**: Lắng nghe và xử lý events
    - Handlers kế thừa từ Subscriber
    - Định nghĩa các methods `on_event_name` để xử lý events

### Ví dụ về Event Handling

```python
# Trong controller
self.slot_map = {
    'button_clicked': ['myButton', 'clicked']
}

# Trong handler
def on_button_clicked(self, data=None):
    # Xử lý event
    pass
```

## Configuration & Logging

### Configuration

- Quản lý cấu hình qua JSON file
- Hỗ trợ nested config với dot notation
- Auto-save và auto-load

```python
from core import Config

config = Config()
config.set("app.name", "My App")
app_name = config.get("app.name")
```

### Logging

- Log ra console và file
- Rotation và retention cho log files
- Separate log files cho errors

```python
from core import logger

logger.info("Info message")
logger.error("Error message")
```

## Exception Handling

- Global exception handler
- Custom exception types
- Tự động logging errors
- UI-friendly error messages

```python
from core import AppException

try:
    # Some code
except AppException as e:
    # Handle error
```

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

## Quy ước đặt tên

- **Classes**: CapitalizeCase (ví dụ: `MainController`)
- **Methods/Variables**: camelCase (ví dụ: `buttonClicked`)
- **Files**: CapitalizeCase.py (ví dụ: `MainController.py`)
- **Directories**: lowercase với underscore (ví dụ: `main_window`)

## Bắt đầu một project mới

1. Sử dụng template:

```bash
gh repo create my-app --template=<repository-url>
```

2. Clone và setup:

```bash
git clone <your-new-repo-url>
cd my-app
pip install -r requirements.txt
```

3. Cấu hình app:

```bash
python scripts/set_app_info.py --name "My App" --version "1.0.0"
```

4. Generate main controller:

```bash
python scripts/generate.py controller Main
```

5. Thiết kế UI với Qt Designer:

- Tạo file .ui trong thư mục `windows/main/ui`
- Compile file .ui thành Python code

6. Implement business logic trong services

7. Kết nối UI với logic thông qua handlers

## Best Practices

1. **Separation of Concerns**
    - UI logic trong controllers
    - Business logic trong services
    - Event handling trong handlers

2. **Reusability**
    - Tạo components cho UI elements được sử dụng lại
    - Chia nhỏ services thành các chức năng độc lập

3. **Event-Driven**
    - Sử dụng Observer Pattern cho communication
    - Tránh tight coupling giữa các components

4. **Error Handling**
    - Xử lý exceptions trong handlers
    - Logging errors appropriately

## Contributing

Vui lòng đọc [CONTRIBUTING.md](CONTRIBUTING.md) để biết thêm chi tiết về quy trình đóng góp.

## License

Project này được phân phối dưới license [MIT](LICENSE). 
