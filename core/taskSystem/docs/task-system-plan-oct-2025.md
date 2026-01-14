Tuyệt vời! Chúng ta đã có một kế hoạch vững chắc. Tôi sẽ bắt đầu cung cấp chi tiết từng thành phần, bao gồm các thuộc tính, phương thức, cách tương tác và cập nhật cấu trúc thư mục với quy ước `PascalCase` cho tên file.

### Cấu trúc thư mục cuối cùng (cập nhật PascalCase)

```
core/
└── taskSystem/
    ├── __init__.py
    ├── TaskManagerService.py
    ├── TaskQueue.py
    ├── TaskScheduler.py
    ├── TaskTracker.py
    ├── AbstractTask.py
    ├── TaskStatus.py
    ├── tasks/
    │   ├── __init__.py
    │   ├── AdbCommandTask.py
    │   └── RpaScriptTask.py
    └── Exceptions.py
```

### Chi tiết từng thành phần

Chúng ta sẽ sử dụng Pub/Sub cho giao tiếp giữa các service và controller. `QObject` và `Signal` vẫn được dùng trong nội bộ các lớp như `AbstractTask` để phát ra các sự kiện, và sau đó các service (ví dụ: `TaskQueue`, `TaskTracker`) sẽ lắng nghe các signals này, xử lý, và nếu cần, phát ra các event Pub/Sub tương ứng.

#### 1. `core.taskSystem.TaskStatus`

*   **Mục đích**: Định nghĩa các trạng thái chuẩn cho một tác vụ.
*   **File**: `core/taskSystem/TaskStatus.py`
*   **Chi tiết**:
    ```python
    from enum import Enum, auto

    class TaskStatus(Enum):
        PENDING = auto()    # Đang chờ trong hàng đợi
        RUNNING = auto()    # Đang thực thi
        COMPLETED = auto()  # Hoàn thành thành công
        FAILED = auto()     # Thất bại (có thể thử lại hoặc không)
        CANCELLED = auto()  # Bị hủy bởi người dùng/hệ thống
        PAUSED = auto()     # Tạm dừng
        RETRYING = auto()   # Đang chờ thử lại
    ```
*   **Tương tác**: Được sử dụng bởi tất cả các lớp liên quan đến tác vụ để thiết lập và kiểm tra trạng thái.

#### 2. `core.taskSystem.Exceptions`

*   **Mục đích**: Định nghĩa các exception tùy chỉnh cho hệ thống tác vụ.
*   **File**: `core/taskSystem/Exceptions.py`
*   **Chi tiết**:
    ```python
    from ..Exceptions import AppException # Giả sử core.Exceptions đã tồn tại

    class TaskSystemException(AppException):
        """Base exception for Task System."""
        pass

    class TaskNotFoundException(TaskSystemException):
        """Raised when a task with a given UUID is not found."""
        pass

    class InvalidTaskStateException(TaskSystemException):
        """Raised when an operation is performed on a task in an invalid state."""
        pass

    class TaskCancellationException(TaskSystemException):
        """Raised when a task is cancelled during execution."""
        pass
    ```
*   **Tương tác**: Các lớp sẽ raise các exception này khi có lỗi đặc thù của hệ thống tác vụ.

#### 3. `core.taskSystem.AbstractTask`

*   **Mục đích**: Định nghĩa giao diện, hành vi cơ bản và logic bao bọc cho mọi tác vụ.
*   **File**: `core/taskSystem/AbstractTask.py`
*   **Kế thừa**: `QtCore.QObject`, `QtCore.QRunnable`, `abc.ABC`.
*   **Thuộc tính**:
    *   `uuid` (str): ID duy nhất (uuid.uuid4().hex).
    *   `name` (str): Tên hiển thị.
    *   `description` (str): Mô tả chi tiết.
    *   `deviceSerial` (str, optional): Serial của thiết bị Android liên quan.
    *   `status` (TaskStatus): Trạng thái hiện tại.
    *   `progress` (int): Tiến độ (0-100%).
    *   `result` (any, optional): Kết quả trả về.
    *   `error` (str, optional): Thông báo lỗi.
    *   `createdAt` (datetime): Thời điểm tạo.
    *   `startedAt` (datetime, optional): Thời điểm bắt đầu chạy.
    *   `finishedAt` (datetime, optional): Thời điểm kết thúc.
    *   `isPersistent` (bool): `True` nếu cần lưu trữ qua các phiên.
    *   `maxRetries` (int): Số lần thử lại tối đa (mặc định 0).
    *   `retryDelaySeconds` (int): Thời gian chờ trước khi thử lại.
    *   `currentRetryAttempts` (int): Số lần đã thử lại.
    *   `failSilently` (bool): Nếu `True`, lỗi không được propagate ra ngoài.
    *   `_stopEvent` (`threading.Event`): Cờ để báo hiệu dừng tác vụ.
*   **Signals (từ `QtCore.QObject`)**:
    *   `statusChanged(str uuid, TaskStatus newStatus)`
    *   `progressUpdated(str uuid, int progressValue)`
    *   `taskFinished(str uuid, TaskStatus finalStatus, object result=None, str error=None)`
*   **Phương thức công khai (API)**:
    *   `__init__(self, name, description="", deviceSerial=None, isPersistent=False, maxRetries=0, retryDelaySeconds=5, failSilently=False)`
    *   `setStatus(self, newStatus: TaskStatus)`: Cập nhật `status` và phát `statusChanged`.
    *   `setProgress(self, value: int)`: Cập nhật `progress` và phát `progressUpdated`.
    *   `isStopped(self) -> bool`: Kiểm tra `_stopEvent.is_set()`.
    *   `cancel(self)`: Thiết lập `_stopEvent.set()`. Nếu tác vụ đang `PENDING` hoặc `PAUSED`, chuyển trạng thái sang `CANCELLED` ngay lập tức. Gọi `_performCancellationCleanup()`.
    *   `fail(self, reason: str = "Task failed by itself")`: Đánh dấu tác vụ là `FAILED` và thiết lập `self.error`.
    *   `serialize(self) -> dict`: Chuyển đổi tác vụ thành dictionary.
    *   `deserialize(cls, data: dict)`: Khôi phục tác vụ từ dictionary (classmethod, abstract).
*   **Phương thức trừu tượng (cần lớp con triển khai)**:
    *   `handle(self)`: Chứa logic nghiệp vụ chính của tác vụ.
    *   `_performCancellationCleanup(self)`: Dọn dẹp tài nguyên đặc thù khi hủy.
*   **Phương thức ghi đè (từ `QRunnable`)**:
    *   `run(self)`:
        *   Thiết lập `startedAt`, `setStatus(TaskStatus.RUNNING)`.
        *   Khối `try-except-finally` bao bọc `self.handle()`.
        *   Nếu `handle()` hoàn thành và `not self.isStopped()`, `setStatus(TaskStatus.COMPLETED)`.
        *   Nếu `self.isStopped()`, `setStatus(TaskStatus.CANCELLED)`.
        *   Nếu có exception, `self.error = str(e)`, `setStatus(TaskStatus.FAILED)`.
        *   Thiết lập `finishedAt`, phát `taskFinished` signal.
*   **Tương tác**:
    *   `TaskQueue` submit `AbstractTask` vào `QThreadPool` (sẽ gọi `AbstractTask.run()`).
    *   `TaskQueue` lắng nghe `taskFinished` signal để xử lý retry/fail/hoàn thành.
    *   `TaskTracker` lắng nghe `statusChanged` và `progressUpdated` để theo dõi.
    *   Các lớp con override `handle()` và `_performCancellationCleanup()`.
    *   Các lớp con gọi `self.isStopped()` để kiểm tra yêu cầu dừng.
    *   Sử dụng `core.logger` và `core.taskSystem.Exceptions`.

#### 4. `core.taskSystem.tasks.AdbCommandTask`

*   **Mục đích**: Triển khai một tác vụ chạy lệnh ADB trên một thiết bị Android.
*   **File**: `core/taskSystem/tasks/AdbCommandTask.py`
*   **Kế thừa**: `core.taskSystem.AbstractTask`.
*   **Thuộc tính**:
    *   `command` (str): Lệnh ADB cần chạy.
    *   `_adbProcess` (`subprocess.Popen` object, optional): Để giữ tham chiếu đến tiến trình ADB.
*   **Phương thức**:
    *   `__init__(self, name, command, ..., deviceSerial=None, ...)`
    *   `handle(self)`:
        *   Thực hiện các bước của lệnh ADB.
        *   **Trong mỗi bước**, kiểm tra `if self.isStopped(): return`.
        *   Sử dụng `AndroidManagerService` để thực thi lệnh.
        *   Cập nhật `progress` và `status`.
        *   Có thể gọi `self.fail("reason")` nếu có lỗi logic nghiệp vụ.
    *   `_performCancellationCleanup(self)`: Gửi tín hiệu `terminate()`/`kill()` cho tiến trình ADB nếu nó đang chạy.
    *   `serialize(self) -> dict` / `deserialize(cls, data: dict)`: Để lưu trữ và khôi phục tác vụ (bao gồm `command`).
*   **Tương tác**:
    *   Tương tác với `AndroidManagerService` (cần một cách để lấy instance của service này, có thể thông qua dependency injection hoặc singleton).

#### 5. `core.taskSystem.TaskTracker`

*   **Mục đích**: Theo dõi trạng thái, tiến độ và log của tất cả các tác vụ. Duy trì lịch sử các tác vụ thất bại.
*   **File**: `core/taskSystem/TaskTracker.py`
*   **Kế thừa**: `QtCore.QObject` (để có thể lắng nghe signals từ `AbstractTask` và `TaskQueue`, và phát ra signals cho `TaskManagerService`/UI).
*   **Thuộc tính**:
    *   `_activeTasks` (dict): `uuid` -> `AbstractTask` object (các tác vụ đang chạy/chờ/tạm dừng).
    *   `_failedTaskHistory` (list): Danh sách các dictionary chứa thông tin chi tiết về các tác vụ đã thất bại vĩnh viễn (không retry nữa).
    *   `_config` (`core.Config` instance): Để lưu/tải `_failedTaskHistory`.
*   **Signals (cho `TaskManagerService`/UI lắng nghe)**:
    *   `taskAdded(str uuid)`
    *   `taskRemoved(str uuid)`
    *   `taskUpdated(str uuid)` (chung cho status/progress/error)
    *   `failedTaskLogged(dict taskInfo)`
*   **Phương thức**:
    *   `__init__(self, config: Config)`: Khởi tạo, tải lịch sử failed tasks.
    *   `addTask(self, task: AbstractTask)`: Thêm tác vụ vào `_activeTasks`, kết nối với signals của task. Phát `taskAdded`.
    *   `removeTask(self, uuid: str)`: Xóa tác vụ khỏi `_activeTasks`. Phát `taskRemoved`.
    *   `getTaskInfo(self, uuid: str) -> dict`: Lấy thông tin hiện tại của task.
    *   `getAllTasksInfo(self) -> list`: Lấy thông tin tất cả active tasks.
    *   `logFailedTask(self, task: AbstractTask)`: Thêm chi tiết task vào `_failedTaskHistory`, lưu vào config. Phát `failedTaskLogged`.
    *   `getFailedTaskHistory(self) -> list`: Lấy lịch sử failed tasks.
    *   `loadState(self)`: Tải `_failedTaskHistory` từ config.
    *   `saveState(self)`: Lưu `_failedTaskHistory` vào config.
*   **Tương tác**:
    *   Lắng nghe `statusChanged`, `progressUpdated`, `taskFinished` signals từ `AbstractTask` để cập nhật `_activeTasks`.
    *   `TaskQueue` gọi `addTask` và `logFailedTask`.
    *   `TaskManagerService` query `getTaskInfo`, `getAllTasksInfo`, `getFailedTaskHistory`.
    *   Sử dụng `core.logger` và `core.Config`.

#### 6. `core.taskSystem.TaskQueue`

*   **Mục đích**: Quản lý hàng đợi FIFO các tác vụ, giới hạn số tác vụ chạy đồng thời, và xử lý logic retry/fail.
*   **File**: `core/taskSystem/TaskQueue.py`
*   **Kế thừa**: `QtCore.QObject`.
*   **Thuộc tính**:
    *   `_pendingTasks` (`collections.deque`): Hàng đợi các `AbstractTask` đang chờ.
    *   `_runningTasks` (dict): `uuid` -> `AbstractTask` object (các tác vụ đang chạy).
    *   `_threadPool` (`QtCore.QThreadPool`): Pool để thực thi tác vụ.
    *   `maxConcurrentTasks` (int): Số lượng tác vụ tối đa chạy đồng thời.
    *   `_taskTracker` (`TaskTracker` instance): Tham chiếu đến TaskTracker.
    *   `_config` (`core.Config` instance): Để lưu/tải các tác vụ pending.
*   **Signals (cho `TaskManagerService`/UI lắng nghe)**:
    *   `queueStatusChanged()` (khi số lượng pending/running thay đổi).
    *   `taskQueued(str uuid)`
    *   `taskDequeued(str uuid)`
*   **Phương thức**:
    *   `__init__(self, taskTracker: TaskTracker, config: Config, maxConcurrentTasks: int = 3)`:
        *   Khởi tạo `_threadPool`, kết nối `_threadPool.started` và `_threadPool.finished` (nếu cần).
        *   Tải `_pendingTasks` từ config.
    *   `addTask(self, task: AbstractTask)`:
        *   Thêm `task` vào `_pendingTasks`.
        *   `_taskTracker.addTask(task)`.
        *   Phát `taskQueued`.
        *   Gọi `_processQueue()`.
    *   `setMaxConcurrentTasks(self, count: int)`: Đặt `_threadPool.setMaxThreadCount(count)`.
    *   `_processQueue(self)`: (Phương thức nội bộ, gọi khi có sự kiện addTask hoặc taskFinished)
        *   Kiểm tra `_runningTasks` và `_pendingTasks`.
        *   Nếu có slot trống và tác vụ chờ:
            *   `task = _pendingTasks.popleft()`.
            *   `_runningTasks[task.uuid] = task`.
            *   Kết nối `task.taskFinished` với `_handleTaskCompletion`.
            *   Submit `task` vào `_threadPool`.
            *   Phát `taskDequeued`.
            *   Phát `queueStatusChanged`.
    *   `_handleTaskCompletion(self, uuid: str, finalStatus: TaskStatus, result: object, error: str)`:
        *   Lấy `task = _runningTasks.pop(uuid)`.
        *   **Xử lý Logic Retry**:
            *   Nếu `finalStatus == TaskStatus.FAILED` và `task.currentRetryAttempts < task.maxRetries`:
                *   `task.currentRetryAttempts += 1`.
                *   `task.setStatus(TaskStatus.RETRYING)`.
                *   Yêu cầu `TaskScheduler` lên lịch lại `task` sau `task.retryDelaySeconds`.
                *   `_taskTracker.logFailedTask` (lần thử lại này).
            *   Else (`COMPLETED`, `CANCELLED`, `FAILED` không retry, v.v.):
                *   Nếu `finalStatus == TaskStatus.FAILED`, `_taskTracker.logFailedTask(task)`.
                *   `_taskTracker.removeTask(uuid)` (nếu không cần theo dõi sau khi hoàn thành).
        *   Gọi `_processQueue()` để kiểm tra và chạy tác vụ tiếp theo.
        *   Phát `queueStatusChanged`.
    *   `loadState(self)`: Tải các tác vụ pending từ `_config`.
    *   `saveState(self)`: Lưu các tác vụ pending vào `_config`.
*   **Tương tác**:
    *   `TaskManagerService` gọi `addTask`, `setMaxConcurrentTasks`.
    *   `TaskScheduler` gọi `addTask` khi đến lịch.
    *   Gửi `AbstractTask` instances vào `_threadPool`.
    *   Gọi `_taskTracker` để quản lý `_activeTasks` và `_failedTaskHistory`.
    *   Sử dụng `core.logger` và `core.Config`.

#### 7. `core.taskSystem.TaskScheduler`

*   **Mục đích**: Lên lịch các tác vụ để chạy vào những thời điểm cụ thể hoặc định kỳ, sử dụng `APScheduler`.
*   **File**: `core/taskSystem/TaskScheduler.py`
*   **Kế thừa**: `QtCore.QObject`.
*   **Thuộc tính**:
    *   `_scheduler` (`APScheduler` instance): Core scheduler engine.
    *   `_taskQueue` (`TaskQueue` instance): Tham chiếu đến TaskQueue.
    *   `_config` (`core.Config` instance): Để cấu hình job store.
*   **Signals (cho `TaskManagerService`/UI lắng nghe)**:
    *   `jobScheduled(str jobId, str taskUuid)`
    *   `jobUnscheduled(str jobId)`
*   **Phương thức**:
    *   `__init__(self, taskQueue: TaskQueue, config: Config)`:
        *   Cấu hình `APScheduler` với `SQLiteJobStore` (hoặc khác) và `threadpool` executor.
        *   Khởi động `_scheduler.start()`.
    *   `addScheduledTask(self, task: AbstractTask, trigger: str, runDate: datetime = None, intervalSeconds: int = None, **kwargs)`:
        *   Tạo một hàm wrapper để gọi `self._taskQueue.addTask(task)`.
        *   Thêm job vào `_scheduler`.
        *   Phát `jobScheduled`.
        *   Lưu ý: `APScheduler` sẽ tự quản lý persistence cho jobs thông qua job store.
    *   `removeScheduledTask(self, jobId: str)`: Xóa job khỏi `_scheduler`. Phát `jobUnscheduled`.
    *   `getScheduledJobs(self) -> list`: Lấy danh sách các job đang được lên lịch từ `_scheduler`.
*   **Tương tác**:
    *   `TaskManagerService` gọi `addScheduledTask`, `removeScheduledTask`.
    *   Khi đến lịch, gọi `_taskQueue.addTask()`.
    *   Sử dụng `core.logger` và `core.Config`.

#### 8. `core.taskSystem.TaskManagerService`

*   **Mục đích**: Điểm truy cập chính cho các phần khác của ứng dụng. Điều phối giữa `TaskQueue`, `TaskTracker`, `TaskScheduler`. Tổng hợp các event cho UI.
*   **File**: `core/taskSystem/TaskManagerService.py`
*   **Kế thừa**: `QtCore.QObject` và `core.Observer.Subscriber`.
*   **Thuộc tính**:
    *   `_taskQueue` (`TaskQueue` instance)
    *   `_taskTracker` (`TaskTracker` instance)
    *   `_taskScheduler` (`TaskScheduler` instance)
    *   `_config` (`core.Config` instance)
    *   `_publisher` (`core.Observer.Publisher` instance): Để lắng nghe và phát lại event.
*   **Signals (cho UI/Observer lắng nghe)**:
    *   `taskAdded(str uuid)`
    *   `taskRemoved(str uuid)`
    *   `taskStatusUpdated(str uuid, TaskStatus newStatus)`
    *   `taskProgressUpdated(str uuid, int progress)`
    *   `failedTaskLogged(dict taskInfo)`
    *   `systemReady()` (khi tất cả services đã khởi tạo và tải trạng thái).
*   **Phương thức**:
    *   `__init__(self, publisher: Publisher, config: Config)`:
        *   Khởi tạo `_taskTracker`, `_taskQueue`, `_taskScheduler`.
        *   **Đăng ký lắng nghe (subscribe)** các signals từ `_taskQueue` và `_taskTracker` để phát ra signals aggregate của chính nó.
        *   Có thể lắng nghe các event pub/sub từ `publisher` (ví dụ: `TaskRequestEvent`) để thêm task.
        *   `loadState()`.
    *   `addTask(self, task: AbstractTask, scheduleInfo: dict = None)`:
        *   Nếu `scheduleInfo` có: gọi `_taskScheduler.addScheduledTask(task, ...)`.
        *   Nếu không: gọi `_taskQueue.addTask(task)`.
        *   Phát `taskAdded` signal.
    *   `cancelTask(self, uuid: str)`: Tìm task và gọi `task.cancel()`.
    *   `pauseTask(self, uuid: str)` / `resumeTask(self, uuid: str)`: Tương tự cancel, nhưng đặt trạng thái `PAUSED` / `PENDING` và gọi `_taskQueue._processQueue()`.
    *   `getTaskStatus(self, uuid: str) -> TaskStatus`: Từ `_taskTracker`.
    *   `getAllTasks(self) -> list`: Từ `_taskTracker`.
    *   `getFailedTasks(self) -> list`: Từ `_taskTracker`.
    *   `setMaxConcurrentTasks(self, count: int)`: Gọi `_taskQueue.setMaxConcurrentTasks(count)`.
    *   `loadState(self)`: Gọi `_taskQueue.loadState()` và `_taskTracker.loadState()`.
    *   `saveState(self)`: Gọi `_taskQueue.saveState()` và `_taskTracker.saveState()`.
    *   `onTaskRequestEvent(self, event: TaskRequestEvent)` (ví dụ từ `core.Observer.Subscriber`): Xử lý event yêu cầu thêm task.
*   **Tương tác**:
    *   Là trung tâm điều phối.
    *   Nhận yêu cầu từ `Publisher` (UI/Other Services).
    *   Lắng nghe signals từ `TaskQueue` và `TaskTracker` và phát lại dưới dạng signals của chính nó (hoặc events Pub/Sub) cho UI.
    *   Sử dụng `core.logger`, `core.Config`.

Với kế hoạch chi tiết này, chúng ta có thể bắt đầu triển khai từng phần một cách có hệ thống. Bạn muốn tôi bắt đầu với `TaskStatus.py` và `Exceptions.py` trước không?
