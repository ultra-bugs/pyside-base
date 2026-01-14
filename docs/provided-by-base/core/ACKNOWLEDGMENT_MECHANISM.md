# Acknowledgment Mechanism - Hướng dẫn sử dụng

**Version:** 1.0
**Created:** 2025-10-03
**Status:** Production Ready

## Tổng quan

Acknowledgment Mechanism là hệ thống điều phối bất đồng bộ (async coordination) cho phép Task Service biết khi nào
Handler Service đã hoàn thành xử lý event, để có thể cleanup resources (browser, connections) một cách an toàn.

### Vấn đề giải quyết

**Trước khi có ACK mechanism:**

```python
# VndAuthService
def get_raffle_id(self):
    raffle_id = self._scrape_raffle()
    Publisher().notify('vndRaffleIdFound', raffleId=raffle_id)  # Emit event
    self.cleanup_browser()  # ❌ NGAY LẬP TỨC cleanup!


# VndAutomationService (handler)
def on_vndRaffleIdFound(self, raffleId):
    # ❌ Browser đã bị close, không thể xử lý tiếp!
    self.api_client.create_job(raffleId)  # Có thể bị lỗi
```

**Sau khi có ACK mechanism:**

```python
# VndAuthService
def get_raffle_id_with_ack(self):
    raffle_id = self._scrape_raffle()
    ack_id = self.emit_event_with_ack('vndRaffleIdFound', raffleId=raffle_id)
    
    # ✓ ĐỢI handler xử lý xong
    self.wait_for_acknowledgments(timeout=60.0)
    
    # ✓ Chỉ cleanup sau khi nhận ACK
    self.cleanup_browser()


# VndAutomationService (handler)
def on_vndRaffleIdFound(self, ack_id, raffleId):
    def process():
        self.api_client.create_job(raffleId)
        return {'job_id': 123}
    
    # ✓ Tự động gửi ACK sau khi xử lý xong
    self.handle_with_ack(ack_id, process)
```

## Kiến trúc 3 tầng

### Layer 1: Core ACK/NACK Protocol

Generic, reusable, không phụ thuộc vào domain cụ thể.

**Components:**

- `AcknowledgmentTracker` - Điều phối ack/nack giữa sender và receiver
- `AcknowledgmentSender` - Base class cho bên gửi acknowledgment
- `AcknowledgmentReceiver` - Base class cho bên nhận và đợi acknowledgment

**Files:**

- `core/ack/AcknowledgmentTracker.py`
- `core/ack/AcknowledgmentSender.py`
- `core/ack/AcknowledgmentReceiver.py`

### Layer 2: Application Integration

Tích hợp Layer 1 với Publisher/Subscriber pattern.

**Components:**

- `TaskServiceWithAck` - Extends AcknowledgmentReceiver, cho reusable services
- `HandlerServiceWithAck` - Extends AcknowledgmentSender + Subscriber

**Files:**

- `core/ack/TaskServiceWithAck.py`
- `core/ack/HandlerServiceWithAck.py`

### Layer 3: Concrete Implementation

VND-specific implementation với browser và API.

**Components:**

- `VndAuthService` - Extends TaskServiceWithAck + browser management
- `VndAutomationService` - Extends HandlerServiceWithAck + API operations

**Files:**

- `services/VndAuthService.py`
- `services/VndAutomationService.py`

## Hướng dẫn sử dụng

### 1. Basic Usage - Single Event

```python
from core.ack.AcknowledgmentTracker import AcknowledgmentTracker
from services.VndAuthService import VndAuthService
from services.VndAutomationService import VndAutomationService

# Step 1: Tạo shared tracker
tracker = AcknowledgmentTracker()

# Step 2: Khởi tạo services với shared tracker
account = {'username': 'user', 'password': 'pass', 'label': 'profile'}
auth_service = VndAuthService(account, shared_tracker=tracker)
handler_service = VndAutomationService(shared_tracker=tracker)

# Step 3: Start handler
handler_service.start()

# Step 4: Emit event với ack
ack_id = auth_service.login_and_get_token_with_ack()

# Step 5: Đợi ack
if auth_service.wait_for_acknowledgments(timeout=30.0):
    print("Handler đã xử lý xong")
else:
    print("Timeout - handler không phản hồi")

# Step 6: Safe cleanup
auth_service.cleanup()
handler_service.stop()
```

### 2. Multiple Events Workflow

```python
# Emit nhiều events
token_ack_id = auth_service.login_and_get_token_with_ack()
raffle_ack_id = auth_service.wait_for_raffle_id_with_ack()

# Đợi TẤT CẢ acks
if auth_service.wait_for_acknowledgments(timeout=60.0):
    # ✓ CẢ 2 handlers đã xử lý xong
    auth_service.cleanup()
```

### 3. Error Handling

```python
# Handler tự động gửi error ack khi có exception
def on_vndTokenFound(self, ack_id, sesInfo, account):
    def process():
        # Nếu có lỗi, handle_with_ack tự động gửi error ack
        user_id = self.api_client.find_user(account['username'])
        if not user_id:
            raise Exception('User not found')
        return {'user_id': user_id}
    
    self.handle_with_ack(ack_id, process)
```

### 4. Backward Compatibility

Code cũ (không có ack) vẫn hoạt động:

```python
# Legacy mode - không dùng ack
auth_service = VndAuthService(account)  # Không truyền shared_tracker
token = auth_service.login_and_get_token()  # Method cũ
auth_service.cleanup()  # Cleanup ngay (như trước)

# Handler vẫn xử lý được (qua Publisher)
handler_service = VndAutomationService()  # Không truyền shared_tracker
handler_service.start()
```

## API Reference

### AcknowledgmentTracker

**Thread-safe coordinator** cho acknowledgments.

```python
class AcknowledgmentTracker:
    def register_pending(
            self,
            ack_id: str,
            success_callback: Callable,
            error_callback: Optional[Callable] = None,
            timeout_callback: Optional[Callable] = None,
            timeout: float = 30.0
    ) -> None:
        """Register pending acknowledgment với callbacks"""
    
    def acknowledge(self, ack_id: str, result: Any = None) -> None:
        """Gửi success acknowledgment"""
    
    def acknowledge_error(self, ack_id: str, error: Exception) -> None:
        """Gửi error acknowledgment"""
    
    def is_pending(self, ack_id: str) -> bool:
        """Check nếu ack_id còn pending"""
    
    def pending_count(self) -> int:
        """Số lượng acks đang pending"""
```

### TaskServiceWithAck

**Base class** cho services emit events và đợi acks.

```python
class TaskServiceWithAck(AcknowledgmentReceiver):
    def emit_event_with_ack(
            self,
            event_name: str,
            timeout: float = 30.0,
            **event_data
    ) -> str:
        """
        Emit event và register pending ack.
        Returns: ack_id
        """
    
    def wait_for_acknowledgments(
            self,
            timeout: float = 60.0
    ) -> bool:
        """
        Đợi TẤT CẢ pending acks.
        Returns: True nếu all acks received, False nếu timeout
        """
```

### HandlerServiceWithAck

**Base class** cho handlers gửi acks.

```python
class HandlerServiceWithAck(AcknowledgmentSender, Subscriber):
    def handle_with_ack(
            self,
            ack_id: str,
            handler_func: Callable[[], Any]
    ) -> None:
        """
        Execute handler và tự động gửi ack.
        - Success: gọi handler_func(), gửi success ack
        - Error: catch exception, gửi error ack
        """
    
    def send_acknowledgment(self, ack_id: str, result: Any = None) -> None:
        """Gửi success ack manually"""
    
    def send_error_acknowledgment(self, ack_id: str, error: Exception) -> None:
        """Gửi error ack manually"""
```

## Best Practices

### ✅ DO

1. **Sử dụng shared tracker**
   ```python
   tracker = AcknowledgmentTracker()
   task_service = TaskService(shared_tracker=tracker)
   handler_service = HandlerService(shared_tracker=tracker)
   ```

2. **Đợi acks trước khi cleanup**
   ```python
   ack_id = service.emit_event_with_ack('event', data=data)
   service.wait_for_acknowledgments(timeout=60.0)
   service.cleanup()  # Safe!
   ```

3. **Sử dụng handle_with_ack helper**
   ```python
   def on_event(self, ack_id, data):
       self.handle_with_ack(ack_id, lambda: self._process(data))
   ```

4. **Set appropriate timeouts**
   ```python
   # Individual ack timeout
   ack_id = service.emit_event_with_ack('event', timeout=30.0)

   # Wait for all acks timeout
   service.wait_for_acknowledgments(timeout=60.0)
   ```

### ❌ DON'T

1. **Không cleanup trước khi đợi acks**
   ```python
   # ❌ SAI
   service.emit_event_with_ack('event')
   service.cleanup()  # Cleanup ngay!

   # ✓ ĐÚNG
   service.emit_event_with_ack('event')
   service.wait_for_acknowledgments()
   service.cleanup()
   ```

2. **Không dùng trackers khác nhau**
   ```python
   # ❌ SAI
   task_service = TaskService()  # Tracker riêng
   handler_service = HandlerService()  # Tracker riêng khác
   # => Không thể coordinate!

   # ✓ ĐÚNG
   tracker = AcknowledgmentTracker()
   task_service = TaskService(shared_tracker=tracker)
   handler_service = HandlerService(shared_tracker=tracker)
   ```

3. **Không block event loop**
   ```python
   # ❌ SAI - block trong handler
   def on_event(self, ack_id, data):
       time.sleep(60)  # Block!
       self.send_acknowledgment(ack_id)

   # ✓ ĐÚNG - async hoặc thread
   def on_event(self, ack_id, data):
       def process():
           # Long operation
           return result
       self.handle_with_ack(ack_id, process)
   ```

## Testing

### Unit Tests

```python
def test_vnd_auth_service_emits_with_ack_id(shared_tracker):
    """Test VndAuthService emits event với ack_id"""
    service = VndAuthService(account, shared_tracker=shared_tracker)
    ack_id = service.login_and_get_token_with_ack()
    
    assert ack_id is not None
    assert shared_tracker.is_pending(ack_id)
```

### Integration Tests

```python
def test_full_ack_workflow(shared_tracker, mock_api):
    """Test full workflow: emit → process → ack → wait"""
    # Setup
    auth = VndAuthService(account, shared_tracker=shared_tracker)
    handler = VndAutomationService(shared_tracker=shared_tracker)
    handler.start()
    
    # Execute
    ack_id = auth.login_and_get_token_with_ack()
    success = auth.wait_for_acknowledgments(timeout=5.0)
    
    # Verify
    assert success is True
    assert shared_tracker.pending_count() == 0
    mock_api.update_account_metadata.assert_called_once()
```

## Troubleshooting

### Timeout Issues

**Symptom:** `wait_for_acknowledgments()` trả về `False`

**Causes:**

1. Handler không subscribe đến event
2. Handler bị lỗi và không gửi ack
3. Timeout quá ngắn

**Solutions:**

```python
# Check handler subscribed
handler.start()  # Đảm bảo đã call start()

# Check handler có lỗi không
# Xem logs để tìm exception

# Tăng timeout
auth.wait_for_acknowledgments(timeout=120.0)  # 2 minutes
```

### Multiple Trackers

**Symptom:** Acks không được nhận dù handler đã gửi

**Cause:** TaskService và HandlerService dùng trackers khác nhau

**Solution:**

```python
# ✓ ĐÚNG - dùng CÙNG tracker
tracker = AcknowledgmentTracker()
task_service = TaskService(shared_tracker=tracker)
handler_service = HandlerService(shared_tracker=tracker)
```

### Memory Leaks

**Symptom:** Pending acks không được cleanup

**Cause:** Timeout callback không được gọi

**Solution:**

```python
# Manual cleanup expired acks
tracker.cleanup_expired()
```

## Future Enhancements

### Planned Features

1. **Retry Mechanism**
    - Auto-retry khi timeout
    - Configurable retry count và delay

2. **Metrics & Monitoring**
    - Track ack success rate
    - Average ack response time
    - Alert khi timeout rate > threshold

3. **Distributed Tracking**
    - Redis-based tracker cho multi-process
    - Support cho horizontal scaling

4. **Other Sites**
    - I9AuthService với ACK
    - J8AuthService với ACK
    - Generic ResourceManager base class

## Migration Guide

### Từ GetRaffleIdTask → VndClaimTaskWithAck

**Before (GetRaffleIdTask):**

```python
def execute(self):
    token = self.authVnd.login_and_get_token()  # No ack
    raffle_id = self.authVnd._wait_for_raffle_id()  # No ack
    self.authVnd.cleanup()  # Ngay lập tức
```

**After (VndClaimTaskWithAck):**

```python
def execute(self):
    # Setup với shared tracker
    tracker = AcknowledgmentTracker()
    self.authVnd = VndAuthService(account, shared_tracker=tracker)
    self.handler = VndAutomationService(shared_tracker=tracker)
    self.handler.start()
    
    # Emit với acks
    token_ack = self.authVnd.login_and_get_token_with_ack()
    raffle_ack = self.authVnd.wait_for_raffle_id_with_ack()
    
    # Đợi acks
    if self.authVnd.wait_for_acknowledgments(timeout=60.0):
        # ✓ Safe cleanup
        self.authVnd.cleanup()
    else:
        logger.warning("Timeout waiting for acks")
```

## References

- [Task Plan](./tasks/task-acknowledgment-mechanism.md) - Chi tiết implementation
- [Architecture Diagrams](./diagrams/) - Kiến trúc và flow
- [Example](../examples/VndClaimTaskWithAck.py) - Demo code hoàn chỉnh
- [Tests](../tests_auto/integration/test_vnd_ack_workflow.py) - Integration tests

---

**Last Updated:** 2025-10-03
**Author:** Zuko
**Version:** 1.0
