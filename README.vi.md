# UltraBugz pyside_base - Desktop application ship faster

> Cũng có bản English cho [README](./README.md) này. Bản Tiếng Việt này được dịch  động.
> 

## Tư Duy Truyền Cảm Hứng

Ứng dụng Qt cơ bản này không chỉ là một bộ khung mã nguồn mà còn là một tư duy trong phát triển phần mềm: phân tách rõ ràng trách nhiệm, tận dụng Mẫu Thiết Kế Observer, và tự động hóa quy trình làm việc để bạn có thể tập trung vào sự sáng tạo. Mỗi dòng mã đều được thiết kế để khuyến khích sự linh hoạt, tái sử dụng và khả năng mở rộng lâu dài.

---

## 1. Mục Lục

1. [Triết Lý & Tư Duy](#philosophy--mindset)
2. [Khởi Tạo Dự Án](#project-initialization)
3. [Cấu Trúc & Tinh Thần Module](#structure--modular-spirit)
4. [Thành Phần Cốt Lõi & Tư Duy](#core-components--mindset)

   * Controller & Handler: Tách biệt UI và sự kiện
   * Service: Logic thuần, không phụ thuộc UI
   * Component & Quản lý Widget: Có trạng thái, tái sử dụng
   * Hệ thống Task: Tự động hóa, không chặn UI
5. [CLI Scaffolding: Nhanh & Đồng Nhất](#cli-scaffolding-speed--consistency)
6. [Giao Diện & Cấu Hình: Tự Điều Chỉnh](#theme--configuration-self-service)
7. [Observer Pattern: Giao Tiếp Tách Biệt](#observer-pattern-decoupled-communication)
8. [Thực Hành Tốt & Triết Lý Code](#best-practices--coding-philosophy)
9. [Đóng Góp](#contributing)
10. [Giấy Phép](#license-1)

Các thành phần khác cũng được tài liệu hóa thêm. Xem tại [Docs](./docs).

---

## Triết Lý & Tư Duy

1. **Phân Tách Nhiệm Vụ Rõ Ràng**: Mỗi module có một nhiệm vụ duy nhất — UI hiển thị, Service xử lý logic, Handler phản hồi sự kiện. Điều này giúp mã dễ bảo trì và mở rộng.
2. **Tự Động Hóa Là Ưu Tiên**: Hệ thống Task và công cụ CLI giúp tăng tốc phát triển, giảm lỗi thủ công, và tập trung vào thuật toán cốt lõi.
3. **Mẫu Observer**: Giảm liên kết giữa các lớp; các thành phần giao tiếp qua sự kiện, dễ mở rộng và thay đổi linh hoạt.
4. **Module Hóa & Tái Sử Dụng**: Mọi thứ là plugin hoặc component nhỏ — dễ thay thế, kiểm thử và sử dụng lại giữa các dự án.

---

## Khởi Tạo Dự Án

Chuẩn bị khung ứng dụng với tư duy đúng:

1. Sử dụng template:

   ```bash
   gh repo create my-app --template=https://github.com/ultra-bugs/pyside-base
   ```

2. **Clone & Cài đặt**

   ```bash
   git clone <your-new-repo-url> my-app
   cd my-app
   pixi install
   ```

   > Xem hướng dẫn chi tiết Pixi tại docs/provided-by-base/pixi-usage.md

3. **Cài Đặt Thông Tin Cơ Bản**

   ```bash
   python scripts/set_app_info.py --name "My App" --version "1.0.0"
   ```

4. **Tạo Controller Chính & UI**

   ```bash
   python scripts/generate.py controller YourController
   python scripts/compile_ui.py
   ```

> **Tư Duy**: Tự động hóa khởi tạo, tiết kiệm thời gian, đảm bảo cấu trúc đồng nhất cho mọi dự án.

---

## Cấu Trúc & Tinh Thần Module

```
base/
├── core/             # Framework & mẫu thiết kế
│   └── taskSystem/   # Hệ thống quản lý tác vụ
├── windows/          # View, controller và xử lý sự kiện
│   ├── components/   # Thành phần UI có thể tái sử dụng (widget)
│   └── main/         # Cửa sổ chính
├── services/         # Logic nghiệp vụ độc lập
├── models/           # Mô hình dữ liệu UI tái sử dụng
├── scripts/          # Công cụ CLI & scaffolding
├── assets/           # Tài nguyên (ảnh, âm thanh, bản dịch)
│   └── icon.png      # Biểu tượng mặc định
├── data/             # Dữ liệu người dùng và dữ liệu nhúng của ứng dụng
│   ├── config/       # Tập tin cấu hình
│   ├── tasks/        # Lưu trữ tác vụ
│   └── logs/         # Tập tin log
├── vendor/           # Tài nguyên bên thứ ba
└── plugins/          # Plugin cho ứng dụng
```

> **Tư Duy**: Mỗi thư mục là một module độc lập, dễ kiểm thử, phát triển song song, và thay thế mà không ảnh hưởng hệ thống.

---

## Thành Phần Cốt Lõi & Tư Duy

### Controller & Handler: Tách UI và Sự Kiện

* **Controller** kết nối UI với sự kiện qua `slot_map`, không chứa logic nghiệp vụ.
* **Handler (Subscriber)** lắng nghe sự kiện, xử lý và phản hồi, tách biệt hoàn toàn khỏi UI.

```python
# trong controller
class MyController(BaseController):
   # Bản ánh xạ hiển thị: khi `pushButton` được `clicked`
   # phương thức có tên `on_open_btn_click` trong handler sẽ được gọi

   slot_map = {
      'open_btn_click': ['pushButton', 'clicked']
   }

# trong handler
class MyControllerHandler(Subscriber):
   def on_open_btn_click(self, data = None):
      pass
```

> **Tư Duy**: Không đưa logic nghiệp vụ vào sự kiện UI — Controller chỉ làm cầu nối.

---

### Service: Logic Thuần

* Nhận đầu vào, xử lý và trả kết quả — không biết gì về UI.
* Có thể kiểm thử đơn vị và tái sử dụng.

```python
class MyService:
   def fetch_data(self) -> List[Dict]:
      return []
```

> **Tư Duy**: Mỗi service là một microservice — độc lập và dễ bảo trì.

---

### Quản Lý Widget: Có Trạng Thái & Tái Sử Dụng

* **WidgetManager** truy cập bằng dấu chấm, ngăn chặn tín hiệu khi cập nhật, và tự lưu cấu hình.

```python
widget_manager.set('slider.value', 50, save_to_config=True)
```

> **Tư Duy**: Mỗi component có trách nhiệm rõ ràng, trạng thái được quản lý tập trung để tránh tác dụng phụ.

---

### Hệ Thống Task: Tự Động Hóa & Không Chặn UI

* Hỗ trợ đa luồng, lập lịch, và chuỗi tác vụ (task chaining).
* Cung cấp logic thử lại mạnh mẽ, lưu trữ bền vững, và theo dõi tiến độ.

```python
# Thêm một tác vụ
task = AdbCommandTask(name="Install APK", command="install app.apk")
taskManager.addTask(task)

# Tạo một chuỗi tác vụ
chain = taskManager.addChainTask(
    name="Workflow",
    tasks=[task1, task2],
    retryBehaviorMap={'Task1': ChainRetryBehavior.SKIP_TASK}
)
```

> **Tư Duy**: Đưa tác vụ nặng ra nền; giữ UI luôn mượt mà.

---

## CLI Scaffolding: Nhanh & Đồng Nhất

Tạo nhanh Controller, Service, Component, Task, và Step chỉ với một lệnh:

```bash
python scripts/generate.py controller MyController
python scripts/generate.py service MyService
```

> **Tư Duy**: Cưỡng chế quy tắc đặt tên và cấu trúc, giảm thời gian viết mã mẫu.

Xem thêm tại [CLI.md](docs/provided-by-base/CLI.md)

---

## Giao Diện & Cấu Hình: Tự Điều Chỉnh

Sử dụng `qdarktheme` với các chế độ `auto | light | dark`. Cấu hình qua lớp `Config`.

```python
config.set('ui.theme', 'dark')
qdarktheme.setup_theme(config.get('ui.theme'))
```

> **Tư Duy**: Cho phép người dùng và lập trình viên tự tùy chỉnh, không cần mã hóa cứng.

---

## Mẫu Observer: Giao Tiếp Tách Biệt

* **Publisher**: Singleton kết nối Qt signals vào hệ thống sự kiện thống nhất.
* **Subscriber (Handler)**: Đăng ký các phương thức `on_<event_name>` — thêm/xóa listener mà không chạm vào Controller.

```python
def on_button_clicked(self, data = None):
   pass
```

> **Tư Duy**: Module chỉ biết sự kiện, không biết nhau — dễ mở rộng hệ thống.

---

## Thực Hành Tốt & Triết Lý Code

1. **Trách Nhiệm Duy Nhất**: Mỗi file và lớp chỉ có một lý do để thay đổi.
2. **Có Thể Kiểm Thử**: Viết test đơn vị cho Service và Middleware.
3. **Cấu Hình Điều Khiển**: Thay đổi hành vi qua cấu hình, không chỉnh mã nguồn.
4. **Ghi Log & Xử Lý Lỗi**: Dùng middleware để ghi lỗi, thử lại và log theo ngữ cảnh.
5. **Tài Liệu**: Cung cấp hướng dẫn rõ ràng cho mỗi component, service và lệnh CLI.

---

## Đóng Góp

Hoan nghênh đóng góp! Vui lòng đọc `CONTRIBUTING.md` để biết hướng dẫn.

---

## Giấy Phép

Phát hành theo giấy phép MIT. Xem file `LICENSE` để biết chi tiết.
