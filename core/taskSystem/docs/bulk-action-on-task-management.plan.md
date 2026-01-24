# PLAN: TASK TAGGING & BULK OPERATIONS SYSTEM

## 1. VẤN ĐỀ CẦN GIẢI QUYẾT (PROBLEM STATEMENT)

Hiện tại, `TaskSystem` hoạt động rất tốt ở mức độ vi mô (Micro-management) - tức là quản lý từng Task dựa trên UUID. Tuy nhiên, khi quy mô hệ thống mở rộng, chúng ta gặp phải các giới hạn sau:

1.  **Thiếu khả năng điều khiển vĩ mô (Lack of Macro Control):** Người dùng hoặc hệ thống không thể tác động lên một nhóm Task (Ví dụ: "Dừng toàn bộ các tác vụ mạng", "Tạm dừng tất cả các tác vụ thuộc nhóm A"). Việc phải gọi API từng task một là không khả thi.
2.  **Hiệu năng tra cứu thấp (Inefficient Lookup):** Để tìm các task thuộc một loại cụ thể, hệ thống hiện tại phải Loop qua toàn bộ danh sách active tasks (độ phức tạp O(N)). Điều này sẽ gây lag khi số lượng task tăng lên hàng nghìn.
3.  **Rủi ro với Task Chain (Chain Integrity Risk):** Khi thực hiện thao tác hàng loạt (Bulk Action), nếu không phân biệt được đâu là Task độc lập, đâu là Child Task nằm trong Chain, việc gửi lệnh Stop bừa bãi sẽ làm gãy logic xử lý lỗi (Retry/Recovery) của Chain cha.

## 2. GIẢI PHÁP & CHIẾN LƯỢC (SOLUTION & STRATEGY)

Chúng ta sẽ áp dụng mô hình **Embedded Metadata + Reverse Indexing**.
Mục tiêu là biến Tag trở thành thuộc tính tự nhiên của Task và dùng Index để truy xuất tức thì.

### A. Data Model & Serialization
*   **Thay đổi:** Thêm thuộc tính `tags` (Set of Strings) vào `AbstractTask`.
*   **Giải quyết vấn đề:**
    *   Cho phép gắn nhãn linh hoạt (Explicit Tags).
    *   Tự động gắn nhãn theo `ClassName` (Implicit Tags) -> Giải quyết vấn đề nhóm Task theo loại mà không cần code thêm logic filter.
    *   Tự động gắn nhãn `_ChainedChild` cho task con -> Đánh dấu để bảo vệ cấu trúc Chain.
*   **Persistence:** Cập nhật logic `serialize` và `deserialize` để lưu trữ và khôi phục `tags`. Đảm bảo Backward Compatibility cho các job cũ trong Database.

### B. Reverse Indexing Mechanism
*   **Thay đổi:** Tích hợp `Tag Index` (`Dict[Tag, Set[UUID]]`) vào `TaskTracker`.
*   **Giải quyết vấn đề:** Đưa độ phức tạp tìm kiếm từ **O(N)** về **O(1)**. Khi cần lấy danh sách "NetworkTask", `TaskTracker` trả về ngay lập tức set UUIDs tương ứng mà không cần scan memory.

### C. Smart Targeting (Manager Level Filtering)
*   **Thay đổi:** Triển khai các phương thức Bulk Ops (`cancelTasksByTag`, `pauseTasksByTag`) tại `TaskManagerService` kèm theo logic lọc (Filtering).
*   **Giải quyết vấn đề:**
    *   Mặc định **LOẠI BỎ** các task có tag `_ChainedChild` khỏi danh sách tác động khi gọi Bulk Action.
    *   Ngăn chặn việc vô tình can thiệp vào quy trình nội bộ của Task Chain (Loose Coupling).
    *   Vẫn giữ quyền can thiệp thủ công (Manual Intervention) nếu người dùng chỉ định đích danh UUID của child task.

## 3. CÁC ĐỐI TƯỢNG NỘI BỘ BỊ ẢNH HƯỞNG (INTERNAL AFFECTED OBJECTS)

### `AbstractTask`
*   **Attributes:** Thêm `self.tags: Set[str]`.
*   **Methods:**
    *   Update `__init__`: Nhận tham số tags, auto-add `ClassName`.
    *   Update `serialize()`/`deserialize()`: Handle field `tags`.
    *   Thêm helper: `addTag()`, `removeTag()`, `hasTag()`.

### `TaskChain`
*   **Behavior:** Khi khởi tạo hoặc add children tasks, phải tự động inject tag `_ChainedChild` và `Parent_{UUID}` vào các task con.
*   **Mục đích:** Định danh rõ ràng quan hệ cha-con để phục vụ việc Filtering sau này.

### `TaskTracker`
*   **Data Structure:** Thêm `_tagIndex`.
*   **Logic:**
    *   Khi `addTask`: Phân tích tags của task và update Index.
    *   Khi `removeTask`: Clean up UUID khỏi Index.
    *   Khi Task update tags (Runtime): Cần cơ chế (Signal/Direct Call) để re-index.
*   **API:** Thêm `getUuidsByTag(tag)`.

### `TaskManagerService`
*   **API Extension:** Thêm các method `stopTasksByTag(tag)`, `pauseTasksByTag(tag)`, v.v.
*   **Logic:** Thực hiện quy trình 3 bước:
    1.  Query UUIDs từ Tracker (nhanh).
    2.  Filter (Loại bỏ `_ChainedChild` nếu mode là Bulk).
    3.  Execute command trên danh sách đã lọc.

## 4. ẢNH HƯỞNG BÊN NGOÀI & CẦN LƯU Ý (EXTERNAL IMPACTS & NOTES)

### UI / Client Side
*   Hệ thống UI cần cập nhật để hiển thị Tags.
*   Các nút bấm hành động (Action Buttons) trên UI dashboard nên chuyển sang gọi API theo Tag (ví dụ: nút "Stop All Adb Tasks") thay vì Client phải tự get list rồi loop call API.

### Thread Safety
*   Việc truy xuất và cập nhật `_tagIndex` trong `TaskTracker` phải đảm bảo Thread-safe (do `TaskTracker` có thể được gọi từ Worker Thread hoặc Main Thread). Sử dụng cơ chế Signal/Slot của Qt hoặc Mutex Lock là bắt buộc.