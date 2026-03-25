# Phase 1: Defer Startup Loading + Fix GetRaffleIdTask

> [!NOTE]
> Phase 2 (TasksTable/ScheduleTable components, MoveToResult, new columns) và Phase 3 (ScheduleTable inline edit, interval display) sẽ xử lý trong các conversations tiếp theo.

## Mục tiêu

Bootstrap hiện tại bị chậm do:
1. `TaskManagerService.__init__()` → [loadState()](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskManagerService.py#337-348) (file I/O)
2. `TaskScheduler.__init__()` → [_loadJobs()](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskScheduler.py#314-418) (file I/O + reconstruct timers)
3. `ProxyManagerProvider.register()` → [ProxyManager()](file:///d:/personal_git/bvmigrate/new/app/services/proxy/ProxyManagerService.py#83-550) → [_bootstrapConnection()](file:///d:/personal_git/bvmigrate/new/app/services/proxy/ProxyManagerService.py#165-181) → kiểm tra/start 9Proxy process + `time.sleep()`

Giải pháp: defer tất cả sang sau `appReady` signal, cho QMainWindow hiển thị trước.

---

# Phase 1: Optimize Bootstrap — Post-Boot Heavy Init

## Background

Bootstrap lifecycle (Laravel-inspired):
```
register() → boot() → appReady → [event loop starts → UI visible] → post-boot
        ↑ light init    ↑ wire services    ↑ app.ready signal        ↑ heavy I/O
```

Hiện tại, heavy I/O đang chạy trong [register()](file:///d:/personal_git/bvmigrate/new/core/contracts/ServiceProvider.py#58-65):
- `TaskScheduler.__init__()` → [_loadJobs()](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskScheduler.py#314-418) (file I/O + reconstruct timers)
- `TaskManagerService.__init__()` → [loadState()](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskManagerService.py#337-348) (file I/O)
- `ProxyManager.__init__()` → [_bootstrapConnection()](file:///d:/personal_git/bvmigrate/new/app/services/proxy/ProxyManagerService.py#165-181) → [check9ProxyProcess()](file:///d:/personal_git/bvmigrate/new/app/services/proxy/ProxyManagerService.py#458-473) + `start9ProxyProcess()` + `time.sleep()`

**Mục tiêu**: chuyển tất cả vào **post-boot** — sau khi UI đã visible.

---

## Proposed Changes

### 1. TaskSystem — Post-boot state loading

#### [MODIFY] [TaskScheduler.py](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskScheduler.py)

Remove `self._loadJobs()` from [__init__()](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskScheduler.py#104-117) — sẽ được gọi bởi TaskManagerService

#### [MODIFY] [TaskManagerService.py](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskManagerService.py)

- Remove `self.loadState()` from [__init__()](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskScheduler.py#104-117) 
- Add `postBootInit()`: gọi [loadState()](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskManagerService.py#337-348) + `_taskScheduler._loadJobs()`
- Add `setLoggingEnabled(enabled: bool)` + `_isLoggingEnabled` flag cho runtime log toggle
- Suppress log trong `postBootInit()` bằng cách tạm disable → load → re-enable

#### [MODIFY] [AbstractTask.py](file:///d:/personal_git/bvmigrate/new/core/taskSystem/AbstractTask.py)

Trong [run()](file:///d:/personal_git/bvmigrate/new/core/QtAppContext.py#265-272), set `threading.current_thread().name = self.uuid` trước khi chạy, restore lại sau:

```python
def run(self) -> None:
    originalThreadName = threading.current_thread().name
    threading.current_thread().name = self.uuid[:12]  # short uuid for readability
    try:
        # ... existing run logic ...
    finally:
        threading.current_thread().name = originalThreadName
```

> [!NOTE]
> Loguru format dùng `{thread.name}` → sẽ tự hiện task UUID thay vì `Dummy-N`

---

### 2. ProxyManager — Post-boot connection

#### [MODIFY] [ProxyManagerService.py](file:///d:/personal_git/bvmigrate/new/app/services/proxy/ProxyManagerService.py)

- Remove [_bootstrapConnection()](file:///d:/personal_git/bvmigrate/new/app/services/proxy/ProxyManagerService.py#165-181), [_setupSyncTodayInterval()](file:///d:/personal_git/bvmigrate/new/app/services/proxy/ProxyManagerService.py#143-152), [_setupStorageClearingTimer()](file:///d:/personal_git/bvmigrate/new/app/services/proxy/ProxyManagerService.py#153-160) from [__init__()](file:///d:/personal_git/bvmigrate/new/core/taskSystem/TaskScheduler.py#104-117)
- Add `postBootInit()` method (idempotent, guarded by `_isBootstrapped`)

#### [MODIFY] [ProxyManagerProvider.py](file:///d:/personal_git/bvmigrate/new/app/providers/ProxyManagerProvider.py)

Add [boot()](file:///d:/personal_git/bvmigrate/new/core/contracts/ServiceProvider.py#66-73) override: schedule `pm.postBootInit` via `QTimer.singleShot(0, ...)`

---

### 3. QtAppContext — Wire post-boot

#### [MODIFY] [QtAppContext.py](file:///d:/personal_git/bvmigrate/new/core/QtAppContext.py)

After `appReady.emit()`, call `_schedulePostBootInit()`:
- `QTimer.singleShot(0, taskManager.postBootInit)` — runs after event loop processes UI

---

### 4. GetRaffleIdTask — Validate raffle time

#### [MODIFY] [GetRaffleIdTask.py](file:///d:/personal_git/bvmigrate/new/app/tasks/claim/GetRaffleIdTask.py)

Add `_isRaffleTimeValid(promoTimestampMs)` — accept only future or ±30min window. Reject stale cached data.

---

## Verification Plan

### Manual
1. App startup → QMainWindow shows BEFORE `postBootInit` logs appear
2. Log output: thread name shows task UUID (e.g. `T:af7291e9b8cd`) thay vì `T:Dummy-1`
3. Watch Raffle → stale raffle data rejected with warning log

### Unit Test
- `_isRaffleTimeValid()` edge cases


---

### 4. GetRaffleIdTask — Validate raffle start time

#### [MODIFY] [GetRaffleIdTask.py](file:///d:/personal_git/bvmigrate/new/app/tasks/claim/GetRaffleIdTask.py)

Sau khi lấy `raffleId` + `redRainData`, validate `promotionSchedule`:

```python
def _isRaffleTimeValid(self, promoTimestampMs: str) -> bool:
    '''Start time must be future or within ±30 min of now.'''
    if not promoTimestampMs:
        return False
    now = datetime.now()
    startDt = datetime.fromtimestamp(int(promoTimestampMs) / 1000)
    isFuture = startDt > now
    deltaSeconds = abs((startDt - now).total_seconds())
    isInWindow = deltaSeconds <= 30 * 60
    return isFuture or isInWindow
```

Trong [handle()](file:///d:/personal_git/bvmigrate/new/app/tasks/claim/GetRaffleIdTask.py#72-166), wrap Step 3-4 trong retry loop:
- Nếu time **invalid** → log warning, `tab.wait(30)`, retry
- Nếu time **valid** → proceed tới save + emit

---

## Verification Plan

### Manual Verification
1. Chạy app → quan sát log: `TaskManagerService deferred init` và `ProxyManager Deferred bootstrap` xuất hiện SAU `Application Context Ready`
2. QMainWindow phải show TRƯỚC khi deferred init chạy
3. Watch Raffle → nếu raffle data cũ → log `[GetRaffleIdTask] Start time invalid`

### Unit Test
- `_isRaffleTimeValid()` — test future, past, within window, edge cases
