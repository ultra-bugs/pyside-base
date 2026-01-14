# Anti-Detect Session with curl_cffi

## Overview

Module `core.extends.CurlSslAntiDetectSession` cung cấp khả năng chống detect bot bằng cách sử dụng `curl_cffi` thay thế cho `requests` library. Điều này giúp:

- **Fake JA3 fingerprint**: Mỗi browser profile có JA3 fingerprint khác nhau
- **Browser impersonation**: Giả làm Chrome, Edge, Safari với các version khác nhau
- **Rotate fingerprints**: Tự động đổi fingerprint sau mỗi request hoặc theo yêu cầu
- **Drop-in replacement**: Không cần sửa code hiện tại, chỉ cần install patcher

## Installation

### 1. Install curl_cffi

```bash
pixi add --pypi curl-cffi
```

### 2. Activate trong Bootstrap

Module đã được integrate vào `main.py`:

```python
def bootstrap(self):
    """Bootstrap the application"""
    from core.extends.CurlSslAntiDetectSession import installAntiDetectSession
    installAntiDetectSession(autoRotate=False)
```

## Usage

### Basic Usage (Monkey-Patched)

Sau khi install patcher, sử dụng `requests` như bình thường:

```python
# Patcher đã được install trong bootstrap
import requests

# requests.get() giờ sử dụng curl_cffi
response = requests.get('https://example.com')
print(response.status_code)

# Tạo session
session = requests.Session()  # Đây là AntiDetectSession
response = session.get('https://example.com')
```

### Manual Session Creation

Tạo session trực tiếp với các options:

```python
from core.extends.CurlSslAntiDetectSession import createAntiDetectSession

# Tạo session với profile cụ thể
session = createAntiDetectSession(impersonate="chrome120")

# Hoặc để auto-select random profile
session = createAntiDetectSession()

# Enable auto-rotation (đổi profile mỗi request)
session = createAntiDetectSession(autoRotate=True)
```

### Profile Rotation

#### Manual Rotation

```python
session = createAntiDetectSession()

# Check current profile
print(f"Current: {session.currentProfile}")  # e.g., "chrome120"

# Rotate to random profile
new_profile = session.rotateProfile()
print(f"New: {new_profile}")  # e.g., "edge101"

# Rotate to specific profile
session.rotateProfile("safari15_5")
```

#### Auto Rotation

```python
# Tự động đổi profile sau mỗi request
session = createAntiDetectSession(autoRotate=True)

for i in range(5):
    response = session.get('https://httpbin.org/headers')
    print(f"Request {i+1} used: {session.currentProfile}")
```

### Custom Profile Pool

Chỉ sử dụng một subset profiles:

```python
from core.extends.CurlSslAntiDetectSession import BrowserProfile, createAntiDetectSession

# Chỉ dùng Chrome profiles
chrome_only = createAntiDetectSession(
    profilePool=BrowserProfile.chromeVersions
)

# Custom pool
custom_pool = ["chrome120", "chrome123", "edge101"]
session = createAntiDetectSession(profilePool=custom_pool)
```

### Global Configuration

Configure rotation cho toàn bộ application:

```python
from core.extends.CurlSslAntiDetectSession import AntiDetectSession, BrowserProfile

# Enable global rotation với custom pool
AntiDetectSession.configureRotation(
    enabled=True,
    profilePool=BrowserProfile.chromeVersions
)

# Disable global rotation
AntiDetectSession.configureRotation(enabled=False)
```

## Available Profiles

### Get Available Profiles

```python
from core.extends.CurlSslAntiDetectSession import getAvailableProfiles

profiles = getAvailableProfiles()
print(profiles['chrome'])   # Chrome profiles
print(profiles['edge'])     # Edge profiles
print(profiles['safari'])   # Safari profiles
print(profiles['all'])      # All profiles
```

### Profile List

**Chrome (7 versions):**
- chrome99, chrome110, chrome116, chrome119, chrome120, chrome123, chrome124

**Edge (2 versions):**
- edge99, edge101

**Safari (3 versions):**
- safari15_3, safari15_5, safari17_0

## Advanced Usage

### DrissionPage Integration

`DrissionPage` sử dụng `requests` làm dependency nên tự động hưởng lợi từ patcher:

```python
# Install patcher trước
from core.extends.CurlSslAntiDetectSession import installAntiDetectSession
installAntiDetectSession()

# DrissionPage SessionPage sẽ dùng curl_cffi
from DrissionPage import SessionPage

page = SessionPage()
page.get('https://example.com')  # Uses anti-detect session
```

### Custom Implementation

Extend `AntiDetectSession` cho custom logic:

```python
from core.extends.CurlSslAntiDetectSession import AntiDetectSession

class MyCustomSession(AntiDetectSession):
    def __init__(self, **kwargs):
        super().__init__(impersonate="chrome120", **kwargs)
    
    def request(self, method, url, **kwargs):
        # Custom pre-request logic
        print(f"Making {method} request to {url}")
        
        # Call parent
        response = super().request(method, url, **kwargs)
        
        # Custom post-request logic
        print(f"Response status: {response.status_code}")
        
        return response
```

## Testing

Run test suite để validate:

```bash
python tests/test_curl_anti_detect.py
```

Tests cover:
- Basic monkey-patched usage
- Profile rotation (manual & auto)
- Custom profile pools
- DrissionPage compatibility

## JA3 Fingerprinting

Mỗi browser profile có JA3 fingerprint riêng:

| Profile | Browser | Version | JA3 Hash |
|---------|---------|---------|----------|
| chrome120 | Chrome | 120 | Different |
| chrome123 | Chrome | 123 | Different |
| edge101 | Edge | 101 | Different |
| safari15_5 | Safari | 15.5 | Different |

Bằng cách rotate profiles, bạn có thể:
- **Bypass rate limiting**: Mỗi request có fingerprint khác nhau
- **Avoid fingerprinting**: Không có pattern cố định
- **Mimic real users**: Mix nhiều browsers/versions

## Performance Considerations

- **curl_cffi** sử dụng libcurl với BoringSSL → tốc độ tương đương requests
- **Profile rotation** có overhead nhỏ (recreate session)
- **Auto-rotation**: Chỉ enable khi thực sự cần (có performance impact)

## Best Practices

1. **Install patcher sớm**: Trong bootstrap trước khi import bất kỳ module nào dùng requests
2. **Auto-rotation carefully**: Chỉ enable cho sensitive endpoints
3. **Profile pool**: Chọn profiles phù hợp với target (e.g., Chrome-only cho Google services)
4. **Logging**: Monitor profile usage qua logger để debug
5. **Error handling**: Wrap requests trong try-catch vì curl_cffi có thể throw errors khác

## Troubleshooting

### Import Error: curl_cffi not found

```bash
pixi add --pypi curl-cffi
```

### Profile rotation không hoạt động

Check logger output để ensure patcher đã được install:

```
INFO: Anti-detect session installed: auto_rotate=False, profile_pool_size=12
```

### DrissionPage vẫn bị detect

Đảm bảo install patcher **trước** khi import DrissionPage:

```python
# ✓ Correct order
from core.extends.CurlSslAntiDetectSession import installAntiDetectSession
installAntiDetectSession()
from DrissionPage import SessionPage

# ✗ Wrong order - DrissionPage đã import requests trước
from DrissionPage import SessionPage
from core.extends.CurlSslAntiDetectSession import installAntiDetectSession
```

## References

- [curl_cffi GitHub](https://github.com/yifeikong/curl_cffi)
- [JA3 Fingerprinting](https://github.com/salesforce/ja3)
- [Browser Impersonation](https://curl.se/libcurl/)
