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
