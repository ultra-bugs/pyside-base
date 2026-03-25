## The Problem

Khi làm Phone Farm. Việc gửi lệnh vào một thiết bị đang tắt màn hình hoặc đang bị khóa (locked) là nguyên nhân hàng đầu gây ra lỗi `ElementNotFound` hoặc timeout.

CẦN CÓ giải pháp kỹ thuật xử lý TRIỆT ĐỂ vấn đề này, tích hợp vào hệ thống hiện có.

**Chiến lược: **
1. **Detect State:** Kiểm tra màn hình có tắt không? Có bị khóa không? App có đang nổi không?
2. **Recover (Khôi phục):**
    *   Nếu tắt -> Gửi lệnh bật (Wakeup).
    *   Nếu khóa (Keyguard) -> Gửi lệnh vuốt để mở (Unlock/Swipe).
    *   Nếu sai App -> Gửi lệnh Start App để force nó lên foreground.
3. **Verify:** Kiểm tra lại lần nữa.
4. **Skip/Fail:** Nếu vẫn không được thì mới bỏ qua.

---

### 2. Giải pháp kỹ thuật chi tiết

Để làm việc này, chúng ta phải chọc sâu vào **Android System Services** thông qua lệnh `dumpsys`. Đây là cách hệ điều hành quản lý cửa sổ và nguồn điện.

#### A. Detect Screen Locked & Screen Off (Phát hiện màn hình khóa/tắt)

Trong Android, có 2 khái niệm riêng biệt:
1.  **Power State (Screen On/Off):** Màn hình có sáng đèn không.
2.  **Keyguard State (Locked/Unlocked):** Màn hình sáng nhưng có bị lớp bảo mật (màn hình khóa) che không.

cần check cả hai.

**Lệnh ADB:**
```bash
adb shell dumpsys window | grep "mKeyguardShowing"
adb shell dumpsys power | grep "mWakefulness"
```

*   **Logic xử lý:**
    *   Nếu `mWakefulness=Asleep`: Màn hình đang tắt.
    *   Nếu `mWakefulness=Awake` NHƯNG `mKeyguardShowing=true`: Màn hình sáng nhưng đang ở màn hình khóa.
    *   Điều kiện lý tưởng: `mWakefulness=Awake` VÀ `mKeyguardShowing=false`.

```python
def getDeviceState(self, deviceId: str) -> dict:
    # 1. Check Power (Screen On/Off)
    res_power = self._execAdbSync(deviceId, 'shell dumpsys power | grep mWakefulness')
    is_screen_on = 'Awake' in res_power.StdOut

    # 2. Check Locked (Keyguard)
    # Lưu ý: Một số Android đời thấp output có thể khác, nhưng mKeyguardShowing khá chuẩn
    res_window = self._execAdbSync(deviceId, 'shell dumpsys window | grep mKeyguardShowing')
    is_locked = 'mKeyguardShowing=true' in res_window.StdOut
    
    return {
        'screen_on': is_screen_on,
        'locked': is_locked,
        'ready': is_screen_on and not is_locked
    }
```

#### B. Detect Specific App Foreground (Phát hiện App đang chạy nổi)

Không thể chỉ dùng `pm list packages` (cái này chỉ check đã cài đặt). Chúng ta cần hỏi **Window Manager** xem cửa sổ nào đang nhận input (Focus).
**Lệnh ADB:**
```bash
adb shell dumpsys window windows | grep -E "mCurrentFocus|mFocusedApp"
```

- Output thường sẽ có dạng: `mCurrentFocus=Window{... u0 com.android.chrome/com.google.android.apps.chrome.Main...}`

- RegEx để lấy chuỗi package name nằm trong `u0 <package_name>/`.

**Triển khai Python:**

```python
import re

def isAppInForeground(self, deviceId: str, packageName: str) -> bool:
    # Lệnh này lấy cửa sổ đang focus hiện tại
    result = self._execAdbSync(deviceId, 'shell dumpsys window windows | grep -E "mCurrentFocus|mFocusedApp"')
    
    if not result.IsSuccess:
        return False
        
    # Tìm sự xuất hiện của package name trong dòng mCurrentFocus
    # Ví dụ output: mCurrentFocus=Window{8f88630 u0 com.android.chrome/...}
    return packageName in result.StdOut
```

---

### 3. Quy trình tích hợp

1.  **Bước 1 (Check Power):** Gọi hàm check state ở trên.
    *   Nếu `screen_on == False`: Gửi lệnh `input keyevent KEYCODE_WAKEUP` (224) hoặc `KEYCODE_POWER` (26).
    *   *Chờ 1s.*

2.  **Bước 2 (Unlock):** Check lại state.
    *   Nếu `locked == True`:
        *   Gửi lệnh vuốt màn hình từ dưới lên (Swipe up): `input swipe 500 1500 500 500 300` (Giả lập thao tác người dùng vuốt mở khóa).
        *   *Lưu ý:* Nếu thiết bị có Password/Pin, automation sẽ kẹt ở đây. Phone Farm thường tắt password, chỉ để "Swipe to unlock".
    *   *Chờ 1s.*

3.  **Bước 3 (Check Foreground):**
    *   Gọi `isAppInForeground(deviceId, 'com.android.chrome')`.
    *   Nếu `False`:
        *   Gọi lại lệnh `monkey` hoặc `am start` để force app lên.
        *   Chờ 2-3s để app load UI.

4.  **Bước 4 (Final Check):**
    *   Kiểm tra lại Foreground lần cuối. Nếu vẫn False -> `Raise Exception` (Lúc này mới skip thiết bị).


### Tổng kết giải pháp cho Code hiện tại

Bạn cần thêm 2 method vào class `AndroidManagerService` (hoặc `Device`):
1.  `ensureDeviceUnlocked()`: Sử dụng `dumpsys window` và `dumpsys power` để wakeup và swipe unlock.
2.  `ensureAppForeground(package)`: Sử dụng `dumpsys window` để check `mCurrentFocus`.

Sau đó gọi 2 hàm này ở đầu hàm `connect()` trong `AndroidBrowser.py`.


### More infomation

Technical (Low-level View)

1.  **Tại sao lại là `dumpsys window` mà không phải `dumpsys activity`?**
    *   `ActivityManager` quản lý vòng đời logic của App (Stack).
    *   `WindowManager` quản lý việc vẽ bề mặt (Surface) và điều phối Input.
    *   Automation (như click, tap) cần tương tác với Input. Có trường hợp App bị crash hoặc treo, Activity Stack vẫn báo app đó on-top, nhưng thực tế `WindowManager` đang hiển thị Dialog "App has stopped" -> Automation sẽ fail. Vì vậy hỏi `WindowManager` (`mCurrentFocus`) là chính xác nhất.

2.  **CDP (Chrome DevTools Protocol) và trạng thái App:**
    *   Nếu Chrome bị đẩy xuống background (ví dụ người dùng bấm Home), Chrome sẽ pause việc render web để tiết kiệm pin (cơ chế Doze mode của Android).
    *   Lúc này socket CDP vẫn kết nối được, nhưng các lệnh thao tác DOM hoặc chụp màn hình có thể bị treo (hang) hoặc trả về lỗi.
    *   => **Bắt buộc** Chrome phải ở foreground và màn hình phải sáng.