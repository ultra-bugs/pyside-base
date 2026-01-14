# **Tài liệu thiết kế cuối cùng: Tính năng Chuỗi Tác vụ (Task Chaining)**

## 1. Tổng quan & Triết lý thiết kế

Tài liệu này mô tả việc bổ sung khả năng liên kết các tác vụ (task chaining) vào TaskSystem. Tính năng này cho phép nhiều tác vụ thực thi tuần tự như một quy trình công việc (workflow) thống nhất, với khả năng chia sẻ dữ liệu và logic xử lý lỗi tùy chỉnh.

### Triết lý thiết kế cốt lõi

1.  **`TaskChain` là một "Meta-Task"**: Đối với `TaskQueue` và `TaskScheduler`, `TaskChain` chỉ là một `AbstractTask` bình thường. Mọi sự phức tạp về thực thi tuần tự, chia sẻ context và quản lý lỗi đều được đóng gói hoàn toàn bên trong.
2.  **State is Serializable & Recoverable**: Toàn bộ trạng thái của một `TaskChain`—bao gồm `ChainContext` (dữ liệu nghiệp vụ) và `taskStates` (trạng thái thực thi)—phải có thể tuần tự hóa thành JSON. Đây là yếu tố cốt lõi để đảm bảo tính bền bỉ và khả năng phục hồi sau khi khởi động lại.
3.  **Single Source of Truth**: `TaskChain` là nơi duy nhất quản lý và quyết định trạng thái của chuỗi. `TaskTracker` chỉ theo dõi và hiển thị thông tin này cho UI.
4.  **Dependency Injection for Context**: `ChainContext` sẽ được *tiêm* (inject) vào các task con bởi `TaskChain`, giúp giảm sự phụ thuộc ngầm và làm cho các task dễ kiểm thử hơn.
5.  **Task is Responsible for its Status**: Task con tự quyết định trạng thái cuối cùng của nó (`COMPLETED`, `FAILED`). `TaskChain` (Runner) chỉ dựa vào trạng thái này để đưa ra quyết định tiếp theo (tiếp tục, dừng, thử lại).

---


## 2. Các thành phần kiến trúc

### 2.1. Sửa đổi `AbstractTask`
Để một task có thể hoạt động trong một chuỗi, nó cần có khả năng nhận biết về chuỗi cha và context dùng chung.

**File cần sửa**: `core/taskSystem/AbstractTask.py`

```python
class AbstractTask(QtCore.QObject, QtCore.QRunnable, abc.ABC):
    # ... các thuộc tính hiện có ...
    
    def __init__(self, name, ..., chainUuid=None):
        # ...
        self.chainUuid = chainUuid # ID của chain cha
        self._chainContext = None # Sẽ được inject bởi TaskChain

    def setChainContext(self, context: 'ChainContext'):
        """Được gọi bởi TaskChain để inject context.
           Không gọi trực tiếp từ bên ngoài.
        """
        self._chainContext = context

    def serialize(self) -> dict:
        """Chuyển task thành dictionary. Subclass PHẢI gọi super().serialize()."""
        data = {
            'uuid': self.uuid,
            'className': f"{self.__class__.__module__}.{self.__class__.__name__}",
            'name': self.name,
            # ... các trường cơ bản khác ...
            'chainUuid': self.chainUuid,
        }
        return data

    # Subclass khi implement deserialize cần gọi super() hoặc tự xử lý các trường base
```

### 2.2. `ChainContext` (Mới)
Quản lý tập trung dữ liệu được chia sẻ giữa các task trong chuỗi. Nó chỉ chứa dữ liệu nghiệp vụ, không chứa trạng thái của các task.

**File mới**: `core/taskSystem/ChainContext.py`

```python
class ChainContext:
    def __init__(self, chainUuid: str, initialData: dict = None):
        self._chainUuid = chainUuid
        self._data = initialData if initialData is not None else {}
        self._lock = threading.Lock()  # Đảm bảo thread-safe

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Lưu trữ giá trị. Giá trị phải là JSON serializable."""
        with self._lock:
            self._data[key] = value
            
    def serialize(self) -> dict:
        with self._lock:
            return {'chainUuid': self._chainUuid, 'data': self._data}

    @classmethod
    def deserialize(cls, data: dict) -> 'ChainContext':
        return cls(chainUuid=data['chainUuid'], initialData=data.get('data', {}))
```

### 2.3. `ChainRetryBehavior` (Mới)
**File mới**: `core/taskSystem/ChainRetryBehavior.py`
```python
from enum import Enum, auto

class ChainRetryBehavior(Enum):
    STOP_CHAIN = auto()    # Dừng toàn bộ chuỗi ngay lập tức
    SKIP_TASK = auto()     # Bỏ qua task lỗi và tiếp tục với task tiếp theo
    RETRY_TASK = auto()    # Thử lại chỉ task bị lỗi (đây là hành vi mặc định)
    RETRY_CHAIN = auto()   # Thử lại toàn bộ chuỗi từ đầu
```

### 2.4. `TaskChain` (Mới, chi tiết hơn)
Đây là "Nhạc trưởng", điều phối chính, đóng gói và thực thi các task con.

**File mới**: `core/taskSystem/TaskChain.py`
```python
# Cần import: AbstractTask, Subscriber, publisher, logger, time, v.v...

class TaskChain(AbstractTask, Subscriber): # Kế thừa đúng từ cả hai lớp cha
    def __init__(self, name: str, tasks: List[AbstractTask], 
                 retryBehaviorMap: Optional[Dict[str, ChainRetryBehavior]] = None, **kwargs):
        
        # Gọi __init__ của cả hai lớp cha
        AbstractTask.__init__(self, name=name, **kwargs)
        Subscriber.__init__(self, events=['ChainProgressUpdateRequest'])
        
        # Đăng ký với publisher toàn cục
        publisher.subscribe(self, event='ChainProgressUpdateRequest')

        # Các thuộc tính của TaskChain
        for task in tasks:
            task.chainUuid = self.uuid
        self._tasks = tasks
        self._currentTaskIndex = 0
        self._chainContext = ChainContext(self.uuid)
        self._taskStates = {task.uuid: {'status': TaskStatus.PENDING, 'result': None, 'error': ''} for task in tasks}
        self.retryBehaviorMap = retryBehaviorMap if retryBehaviorMap is not None else {}
        self._chainRetryAttempts = 0
        self._progress_updated_externally = False

    def onChainProgressUpdateRequest(self, data=None):
        """
        Handler cho sự kiện cập nhật tiến trình. Chỉ phản hồi nếu chainUuid khớp.
        """
        if data and data.get('chainUuid') == self.uuid:
            progress = data.get('progress')
            if isinstance(progress, int) and 0 <= progress <= 100:
                self.setProgress(progress)
                self._progress_updated_externally = True

    def _updateDefaultProgress(self):
        """Tính toán và cập nhật tiến trình mặc định (phân bổ đều)."""
        progress = int(((self._currentTaskIndex + 1) / len(self._tasks)) * 100)
        self.setProgress(progress)

    def cancel(self):
        """Ghi đè hàm cancel để đảm bảo unsubscribe."""
        super().cancel()
        publisher.unsubscribe(self, event='ChainProgressUpdateRequest')
        self._performCancellationCleanup() # Đảm bảo task con cũng được hủy

    def handle(self):
        """Vòng lặp chính, thực thi tuần tự các task trong chuỗi."""
        while self._currentTaskIndex < len(self._tasks):
            if self.isStopped():
                self.setStatus(TaskStatus.CANCELLED)
                return
            # Reset cờ trước khi chạy task con
            self._progress_updated_externally = False
            task = self._tasks[self.currentTaskIndex]
            task.setChainContext(self._chainContext)
            
            # --- LOGIC THỰC THI & RETRY CỦA TASK CON ---
            isTaskSuccess = self._executeSubTaskWithRetry(task)

            if not isTaskSuccess:
                # Tìm hành vi xử lý lỗi cho chain
                taskClassName = task.__class__.__name__
                chainBehavior = self.retryBehaviorMap.get(taskClassName, ChainRetryBehavior.STOP_CHAIN)
                
                if chainBehavior == ChainRetryBehavior.STOP_CHAIN:
                    self.fail(f"Sub-task '{task.name}' failed and chain is configured to stop.")
                    return
                elif chainBehavior == ChainRetryBehavior.SKIP_TASK:
                    # Bỏ qua task này, log lại và tiếp tục vòng lặp
                    logger.warning(f"Skipping failed sub-task '{task.name}' as per chain configuration.")
                    self._currentTaskIndex += 1
                    continue
                elif chainBehavior == ChainRetryBehavior.RETRY_CHAIN:
                    # Logic để retry toàn bộ chain
                    if self._chainRetryAttempts < self.maxRetries:
                        self._chainRetryAttempts += 1
                        logger.info(f"Retrying entire chain (Attempt {self._chainRetryAttempts}/{self.maxRetries}).")
                        self._currentTaskIndex = 0
                        # Tùy chọn: Xóa một phần context trước khi retry
                        # self._chainContext.clear_sensitive_data()
                        continue
                    else:
                        self.fail(f"Chain failed after {self.maxRetries} retry attempts.")
                        return

            # Chỉ tính progress mặc định nếu không có sự kiện nào được phát
            if not self._progress_updated_externally:
                self._updateDefaultProgress()
            self._currentTaskIndex += 1
        
        self.result = self._chainContext.serialize()['data']
        # Hủy đăng ký khi chain kết thúc để tránh memory leak
        publisher.unsubscribe(self, event='ChainProgressUpdateRequest')

    def _executeSubTaskWithRetry(self, task: AbstractTask) -> bool:
        """
        Thực thi một task con, tự quản lý việc retry task đó.
        Trả về True nếu task thành công, False nếu thất bại sau khi hết số lần thử.
        """
        attempts = 0
        while attempts <= task.maxRetries:
            if attempts > 0:
                self.setStatus(TaskStatus.RETRYING)
                logger.info(f"Retrying sub-task '{task.name}' (Attempt {attempts}/{task.maxRetries}).")
                time.sleep(task.retryDelaySeconds)
                self.setStatus(TaskStatus.RUNNING)
            
            # Reset lại trạng thái task trước mỗi lần chạy
            task.setStatus(TaskStatus.PENDING)
            
            try:
                task.run() # Thực thi
                if task.status == TaskStatus.COMPLETED:
                    self._taskStates[task.uuid]['status'] = task.status
                    return True # Thành công!
            except Exception as e:
                task.fail(str(e))
                logger.error(f"Sub-task '{task.name}' crashed with exception.", exc_info=True)
            
            # Nếu chạy đến đây, task đã thất bại
            attempts += 1

        # Hết số lần thử, ghi nhận thất bại cuối cùng
        self._taskStates[task.uuid]['status'] = task.status
        self._taskStates[task.uuid]['error'] = task.error
        return False # Thất bại!
    
    # ... (các hàm serialize, deserialize, updateProgress giữ nguyên) ...
```

### 2.5. Cập nhật `TaskTracker`
Nâng cấp `TaskTracker` để có thể hiển thị cấu trúc cha-con của chuỗi.

**File cần sửa**: `core/taskSystem/TaskTracker.py`
-   **Trong `addTask`**: Khi nhận một `TaskChain`, duyệt qua các task con (`sub_task in task._tasks`) và cũng thêm chúng vào danh sách theo dõi với một cờ đặc biệt, ví dụ `{'isChainChild': True, 'chainUuid': task.uuid}`.
-   **Trong `getTaskInfo`**: Nếu `uuid` được yêu cầu là của một `TaskChain`, trả về thông tin của chain kèm theo một mảng `subTasks` chứa thông tin của từng task con.

### 2.6. Cập nhật `TaskManagerService`
Thêm phương thức tiện ích để đơn giản hóa việc tạo và chạy một chuỗi.

**File cần sửa**: `core/taskSystem/TaskManagerService.py`
```python
# trong class TaskManagerService
def addChainTask(self, name: str, tasks: List[AbstractTask], scheduleInfo=None, **kwargs) -> TaskChain:
    """Tạo và thêm một TaskChain vào hệ thống."""
    chain = TaskChain(name=name, tasks=tasks, **kwargs)
    self.addTask(chain, scheduleInfo=scheduleInfo)
    return chain
```

### 2.7. Cập nhật `TaskQueue`
**Không cần thay đổi.** `TaskChain` kế thừa từ `AbstractTask`, nên `TaskQueue` có thể xử lý nó như một task thông thường.

----


## 3. Luồng hoạt động và các chi tiết triển khai

### 3.1 Luồng thực thi
1.  Người dùng gọi `taskManager.addChainTask(...)`.
2.  `TaskManagerService` tạo một instance `TaskChain` và đưa vào `TaskQueue`.
3.  `QThreadPool` bắt đầu thực thi `TaskChain.run()`, gọi đến `TaskChain.handle()`.
4.  Vòng lặp `handle()` của `TaskChain` bắt đầu.
5.  Với mỗi task con:
    a. Inject `ChainContext` vào task con.
    b. Gọi `task.run()` một cách đồng bộ (blocking call).
    c. Sau khi task con hoàn thành, kiểm tra trạng thái (`COMPLETED`, `FAILED`).
    d. Nếu `FAILED`, áp dụng logic từ `retryBehaviorMap`.
    e. Cập nhật tiến trình tổng thể của chuỗi.
    f. Chuyển sang task tiếp theo.
6.  Khi tất cả các task con hoàn thành, `TaskChain` tự đánh dấu là `COMPLETED`.

### 3.2 Luồng phục hồi sau khi khởi động lại
1.  Ứng dụng tắt trong khi một `TaskChain` `isPersistent` đang chạy dở.
2.  `TaskChain.serialize()` được gọi, lưu lại toàn bộ trạng thái: `_currentTaskIndex`, `_chainContext`, và trạng thái của tất cả task con.
3.  Khi ứng dụng khởi động lại, `TaskSystem` đọc lại dữ liệu đã lưu.
4.  `TaskChain.deserialize()` được gọi, tái tạo lại đối tượng `TaskChain` y hệt như trạng thái trước khi tắt.
5.  Khi chuỗi được đưa vào `TaskQueue` và thực thi lại, `handle()` của nó sẽ bắt đầu từ `_currentTaskIndex` đã được khôi phục, bỏ qua các task con đã hoàn thành trước đó.

### 3.3 Mẫu sử dụng `ChainContext`
```python
# Trong file task con, ví dụ LoginTask.py
class LoginTask(AbstractTask):
    def handle(self):
        # ... logic đăng nhập ...
        auth_token = "some_generated_token"
        
        # Lưu token vào context dùng chung
        if self._chainContext:
            self._chainContext.set("auth_token", auth_token)

# Trong file GetDataTask.py
class GetDataTask(AbstractTask):
    def handle(self):
        if self._chainContext:
            auth_token = self._chainContext.get("auth_token")
            # ... Dùng token để gọi API lấy dữ liệu ...
```
### 3.4. Luồng xử lý lỗi và Retry (CHI TIẾT)
Hệ thống xử lý lỗi theo một cấu trúc có thứ tự rõ ràng, đáp ứng yêu cầu tùy chỉnh cao.

1.  **Thực thi Task con**: `TaskChain` gọi hàm nội bộ `_executeSubTaskWithRetry()` để chạy một task con.
2.  **Retry cấp Task**: Hàm này tự chứa một vòng lặp `while` để thực hiện lại task con nếu nó thất bại, dựa trên chính các thuộc tính `task.maxRetries` và `task.retryDelaySeconds`. Đây là hành vi retry **mặc định và cấp thấp nhất**.
3.  **Quyết định cấp Chain**:
    *   Nếu sau tất cả các lần thử lại mà task con vẫn thất bại (`_executeSubTaskWithRetry` trả về `False`), `TaskChain` sẽ can thiệp.
    *   Nó sẽ tra cứu lớp của task con trong `self.retryBehaviorMap`.
    *   **Mặc định (nếu không được cấu hình)**: Nếu task con thất bại vĩnh viễn, `TaskChain` sẽ dừng lại (`STOP_CHAIN`).
    *   **Hành vi tùy chỉnh**: Dựa trên giá trị tìm thấy trong map, `TaskChain` sẽ thực hiện một trong các hành động: `STOP_CHAIN`, `SKIP_TASK`, hoặc `RETRY_CHAIN`.

**Sơ đồ luồng:**
`TaskChain.handle()` -> `_executeSubTaskWithRetry(task)`
    -> Bắt đầu vòng lặp retry cho `task` (dựa trên `task.maxRetries`)
        -> `task.run()`
        -> Nếu thành công -> thoát vòng lặp, trả về `True`.
        -> Nếu thất bại -> tiếp tục vòng lặp retry.
    -> Nếu hết số lần retry vẫn thất bại -> thoát vòng lặp, trả về `False`.
-> `TaskChain.handle()` nhận `False`
    -> Tra cứu `retryBehaviorMap`
    -> Thực hiện hành vi cấp Chain (STOP, SKIP, RETRY_CHAIN).

### 3.5. Thoát có điều kiện (Conditional Exit)
Theo triết lý thiết kế, `TaskChain` (Runner) không tự suy diễn logic nghiệp vụ.
-   Một task con, ví dụ `CheckLoginStatusTask`, có thể kiểm tra và thấy người dùng đã đăng nhập.
-   Thay vì thực hiện lại luồng đăng nhập, task này sẽ tự động kết thúc và set trạng thái của nó là `TaskStatus.COMPLETED`.
-   Đối với `TaskChain`, `COMPLETED` là tín hiệu để tiếp tục thực thi task tiếp theo trong chuỗi.
-   Do đó, **trách nhiệm xác định một "self-exit" là thành công hay thất bại thuộc về người lập trình task con thông qua trạng thái cuối cùng của nó.**


---

## 4. Danh sách các file cần thay đổi

#### File cần tạo mới:
1.  `core/taskSystem/ChainContext.py` - Lớp quản lý context.
2.  `core/taskSystem/ChainRetryBehavior.py` - Enum định nghĩa hành vi retry.
3.  `core/taskSystem/TaskChain.py` - Lớp triển khai `TaskChain`.

#### File cần chỉnh sửa:
1.  `core/taskSystem/AbstractTask.py` - Thêm `chainUuid` và `_chainContext`.
2.  `core/taskSystem/TaskTracker.py` - Thêm logic để nhận diện và hiển thị chuỗi.
3.  `core/taskSystem/TaskManagerService.py` - Thêm phương thức tiện ích `addChainTask`.
4.  `docs/task-system-api.md` - Cập nhật tài liệu API.
5.  `docs/diagrams/task-system-architect-design.mermaid` - Thêm `TaskChain` vào sơ đồ kiến trúc.

## 5. Các điểm cần kiểm thử (Testing Considerations)
-   Kiểm thử đơn vị (Unit tests) cho `ChainContext` (tính thread-safe, serialization).
-   Kiểm thử đơn vị cho `TaskChain` (luồng thực thi, các hành vi retry, tính toán tiến trình).
-   Kiểm thử tích hợp (Integration tests) một chuỗi hoàn chỉnh với các task thật.
-   Kiểm thử kịch bản một task con thất bại và các hành vi retry (`STOP`, `SKIP`, `RETRY_TASK`).
-   Kiểm thử việc chia sẻ dữ liệu qua `ChainContext` giữa các task con.
-   **Kiểm thử quan trọng nhất**: Chạy một chuỗi, tắt ứng dụng giữa chừng, khởi động lại và xác minh rằng chuỗi tiếp tục chạy từ đúng vị trí.
-   Kiểm thử việc hủy một `TaskChain` và xác minh task con đang chạy cũng bị hủy.
-   Kiểm thử một task con thất bại 1 lần rồi thành công trong lần retry tiếp theo; xác minh chain vẫn tiếp tục.
-   Kiểm thử một task con thất bại hết `maxRetries`; xác minh chain dừng lại (hành vi mặc định).
-   Kiểm thử cấu hình `retryBehaviorMap` với `SKIP_TASK`: xác minh chain bỏ qua task lỗi và hoàn thành các task sau đó.
-   Kiểm thử cấu hình `retryBehaviorMap` với `RETRY_CHAIN`: xác minh `_currentTaskIndex` được reset về 0 và chuỗi bắt đầu lại.
-   Kiểm thử tính năng phục hồi (Serialization/Deserialization) khi ứng dụng tắt trong lúc một task con đang trong trạng thái `RETRYING`.
