QtAppContext — Application Context (Provided by Base)

Tổng quan
- Quản lý vòng đời ứng dụng (appBooting, appReady, appClosing)
- Bootstrap các lõi: Config, Publisher, ExceptionHandler
- Tùy chọn bật NetworkManager và TaskSystem qua biến môi trường (PSA_ENABLE_NETWORK, PSA_ENABLE_TASKS)
- Cung cấp Service Locator/DI: registerService, getService, registerScopedService, releaseScope
- Cho phép truy cập nhanh: .config, .publisher, .network, .taskManager
- Quản lý shared state thread-safe: setState/getState

Lifecycle & Bootstrap
- Dùng QtAppContext.globalInstance() để lấy singleton
- Gọi bootstrap() đúng 1 lần (idempotent)
- Gọi run() để chạy vòng lặp sự kiện Qt

Feature Flags (ENV)
- PSA_ENABLE_NETWORK (mặc định true)
- PSA_ENABLE_TASKS (mặc định true)

Dịch vụ được khởi tạo
- Config (core.Config)
- Publisher (core.Observer.Publisher)
- ExceptionHandler (core.Exceptions.ExceptionHandler)
- NetworkManager (core.NetworkManager) nếu bật
- TaskManagerService (core.taskSystem.TaskManagerService) nếu bật

Sử dụng trong main.py (mẫu rút gọn)
- Khởi tạo Config, ExceptionHandler
- ctx = QtAppContext.globalInstance(); ctx.bootstrap()
- Tạo MainController, show
- ctx.run()

Ghi chú
- QtAppContext tự tạo QApplication nếu chưa có
- Khi đóng app, QtAppContext phát appClosing và gửi sự kiện "app.shutdown" qua Publisher
- Nếu bật TaskSystem, nên gọi task_manager.shutdown() trong closeEvent của cửa sổ chính để lưu state
