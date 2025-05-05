# UltraBugz pyside_base - Desktop application ship faster

**Base Qt Application với PySide6 — Mindset Truyền Cảm Hứng**
Codebase này không chỉ là một bộ khung code, mà còn là cách tư duy trong phát triển phần mềm: phân tách rõ ràng trách
nhiệm, tận dụng sức mạnh của Observer Pattern, và tự động hóa quy trình để bạn tập trung vào sáng tạo. Mỗi dòng code ở
đây được xây dựng để khuyến khích sự linh hoạt, tái sử dụng và mở rộng về lâu dài.

---

## 1. Mục lục

1. [Tư duy & Triết lý](#tu-duy--triet-ly)
2. [Khởi tạo dự án](#khoi-tao-du-an)
3. [Cấu trúc & Tinh thần Modular](#cau-truc--tinh-than-modular)
4. [Các thành phần chính & Mindset](#cac-thanh-phan-chinh--mindset)

    * Controller & Handler: Tách UI và sự kiện
    * Service: Logic thuần, không vướng UI
    * Component & Widget Manager: Tái sử dụng, duy trì trạng thái
    * Task System & Middleware: Tự động hóa, không block UI
5. [CLI Scaffolding: Tốc độ & Nhất quán](#cli-scaffolding-toc-do--nhat-quan)
6. [Theme & Cấu hình: Tự phục vụ](#theme--cau-hinh-tu-phuc-vu)
7. [Observer Pattern: Giao tiếp không coupling](#observer-pattern-giao-tiep-khong-coupling)
8. [Best Practices & Triết lý Coding](#best-practices--triet-ly-coding)
9. [Đóng góp](#dong-gop)
10. [License](#license)

Ngoài ra cũng còn những phần khác cũng có tài liệu. Xem ở [docs](./docs).

---

## Tư duy & Triết lý

1. **Separation of Concerns**: Mỗi module chỉ làm một việc duy nhất — UI chỉ hiển thị, Service chỉ xử lý logic, Handler
   chỉ phản hồi sự kiện. Giúp code dễ bảo trì và mở rộng.
2. **Automation First**: Task System và CLI scaffolding giúp bạn đẩy nhanh tiến độ, giảm lỗi thủ công và tập trung vào
   giải thuật chính.
3. **Observer Pattern**: Giảm coupling giữa các lớp, các component giao tiếp qua sự kiện, đảm bảo tính mở rộng và khả
   năng thay đổi linh hoạt.
4. **Modularity & Reusability**: Tất cả đều là plugin hoặc component nhỏ, dễ thay thế, dễ test, và có thể tái sử dụng ở
   các dự án khác.

---

## Khởi tạo dự án

Nhanh chóng tạo dựng khung ứng dụng với mindset:

1. **Clone & Cài đặt**

   ```bash
   git clone https://github.com/MyL1nk/ccpy.git my-app
   cd my-app
   pip install -r requirements.txt
   ```

2. **Cấu hình thông tin cơ bản**

   ```bash
   python scripts/set_app_info.py --name "My App" --version "1.0.0"
   ```

3. **Tạo Controller chính và UI**

   ```bash
   python scripts/generate.py controller Main
   python scripts/compile_ui.py
   ```

> **Mindset**: Tự động hoá quy trình thiết lập, tiết kiệm thời gian, đảm bảo mọi dự án bắt đầu với cấu trúc chuẩn.

---

## Cấu trúc & Tinh thần Modular

```
base/
├── core/             # Nền tảng, template pattern
├── windows/          # Controller + UI (.ui + handlers)
├── services/         # Business logic độc lập
├── components/       # UI components tái sử dụng
├── scripts/          # CLI scaffolding & công cụ
├── plugins/          # Mở rộng năng lực ứng dụng
└── data/             # Cấu hình, logs, resources
```

> **Mindset**: Mỗi thư mục là một thành phần độc lập, dễ test, dễ phát triển song song, và có thể được thay thế mà không
> ảnh hưởng hệ thống.

---

## Các thành phần chính & Mindset

### Controller & Handler: Tách UI và sự kiện

* **Controller** chỉ kết nối UI và map các signal đến handler qua `slot_map`. Giao tiếp giản lược, không trực tiếp gọi
  logic.
* **Handler (Subscriber)** lắng nghe sự kiện, xử lý và phản hồi, hoàn toàn tách rời với câu chuyện UI.

```python
self.slot_map = {
    'open_btn_click': ['pushButton', 'clicked']
}
```

> **Mindset**: Không viết code xử lý business trong sự kiện UI, giữ cho Controller gọn, chỉ chuyển tiếp sự kiện.

---

### Service: Logic thuần

* Nhận đầu vào, xử lý, trả kết quả, không biết gì về giao diện.
* Có thể test riêng bằng unit test, reuse ở nhiều nơi.

```python
class MyService:
    def fetch_data(self) -> List[Dict]:
        # Xử lý dữ liệu
        return []
```

> **Mindset**: Xây dựng service như microservice nhỏ trong repo, độc lập, dễ bảo trì.

---

### Component & Widget Manager: Tái sử dụng, duy trì trạng thái

* **BaseComponent**: Đóng gói UI fragment thành component riêng biệt.
* **WidgetManager**: Dot-notation truy cập widget, suppress signals khi cập nhật, lưu cấu hình tự động.

```python
widget_manager.set('slider.value', 50, save_to_config=True)
```

> **Mindset**: Mỗi component phải có trách nhiệm rõ ràng, state quản lý tập trung, tránh side-effect.

---

### Task System & Middleware: Tự động hóa, không block UI

* Hỗ trợ đa luồng, scheduling, middleware chainable.
* Tách các bước công việc thành `TaskStep`, dễ theo dõi, retry, captcha, logging.

```python
task = task_manager.create_task("SyncData")
task.add_step(FetchStep())
task.add_step(ProcessStep())
task_manager.run_task(task)
```

> **Mindset**: Tất cả tác vụ nặng kéo dài đều chạy nền, UI luôn phản hồi nhanh.

---

## CLI Scaffolding: Tốc độ & Nhất quán

Tạo nhanh Controller, Service, Component, Task/Step chỉ với một lệnh:

```bash
python scripts/generate.py controller MyController
python scripts/generate.py service MyService
```

> **Mindset**: Đồng bộ cách đặt tên, cấu trúc folder, giảm thời gian boilerplate.

---

## Theme & Cấu hình: Tự phục vụ

Sử dụng `qdarktheme` với lựa chọn `auto | light | dark`. Cấu hình dễ dàng qua `Config`.

```python
config.set('ui.theme', 'dark')
qdarktheme.setup_theme(config.get('ui.theme'))
```

> **Mindset**: Người dùng cuối và developer đều có quyền tuỳ chỉnh, không hardcode giao diện.

---

## Observer Pattern: Giao tiếp không coupling

* **Publisher**: Singleton, kết nối Qt signals vào hệ thống event chung.
* **Subscriber (Handler)**: Đăng ký `on_<event_name>`, dễ thêm/xóa listener mà không sửa controller.

```python
def on_button_clicked(self, data = None):
    # Xử lý sự kiện
    pass
```

> **Mindset**: Module không biết về nhau, chỉ biết giao tiếp qua event, giúp hệ thống mở rộng dễ dàng.

---

## Best Practices & Triết lý Coding

1. **Single Responsibility**: Mỗi file, mỗi class chỉ có một lý do để thay đổi.
2. **Testable**: Service và Middleware nên có unit test riêng.
3. **Config-driven**: Thay đổi behavior qua config, không sửa code.
4. **Logging & Error Handling**: Middleware bắt lỗi, retry logic, log rõ context.
5. **Documentation**: Mỗi component, service, CLI command đều có help rõ ràng.

---

## Đóng góp

Rất hoan nghênh PR và Issue! Vui lòng đọc `CONTRIBUTING.md` để hiểu quy trình.

---

## License

Bản quyền dưới MIT License. Xin trích nguyên văn `LICENSE` để xem chi tiết.
