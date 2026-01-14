# Base Qt Application

This is a base Qt application that can be used to create a new Qt application.

Using PySide6, Observed Pattern, and Qt Designer.


# Sơ lược về các thành phần và cấu trúc thư mục 

\+ **App** được viết dựa trên mô hình MVC mix chung với Services

\+ **Service** xử lý các tác vụ đặc thù theo tính năng mà service đó
được đặt tên

\+ **Controller** là các class xử lý UI

\+ **View** là các class được generate từ file **.ui** của **pyside**. Phần
giao diện được thiết kế thông qua công cụ **QtDesigner**

\+ **Model**: chia làm 2 nhánh: `App Model` và `Qt Model`.Model sẽ là
nơi nhận và hold dữ liệu input, cũng như phục vụ dữ liệu mà Controller
yêu cầu



***Cấu trúc thư mục***


\+ **naming_convention** 
    
    sử dụng CamelCase cho method, variable, property và CapitalizeCase cho các class, file.  
    Ví dụ: `MainController.py`            
    sử dụng từ khoá mô tả những gì chứa bên trong đối với thư mục. cố gắng giữ trong khoảng 1-2 từ.
    Ví dụ: `windows/main/ui`


\+ **core :** chứa các class, design pattern mà sẽ được dùng và triển
khai tại nhiều nơi trong app

\+ **windows :** lưu views và controller và các event handler cho
controller.

\+ **scripts:** chứa các file script chủ yếu phục vụ CLI

\+ **services:** chứa các class service

\+ **data**: nơi lưu các dữ liệu người dùng và những dữ liệu được nhúng
sẵn của app

\+ **assets**: nơi lưu các file tài nguyên như hình ảnh, âm thanh, video, tài liệu giúp dịch ứng dụng (đa ngôn ngữ), ...

\+ **vendor**: nơi lưu các file tài nguyên của các thư viện khác như PySide6, compiled qrc ,Qt Designer, ...

-- các mục đang ở giai đoạn ý tưởng, tìm phương án.

\+ **plugins**: nơi lưu các plugin của app, plugin có thể là các class được tạo ra từ các file .ui, .py, ...

# Chi tiết về mindset trong app

Phần này chủ yếu mô tả về hướng đi của luồng dữ liệu trong app. Thiết kế
cơ bản thì sẽ không thay đổi, nếu có sẽ cập nhật thêm tại đây.

## UI -- Giao diện



UI của từng windows/dialog/widget được lưu theo từng controller riêng biệt. Và là con
của class **BaseController**.

Widget : Các controller extend từ **BaseController** sau **init** sẽ
quản lý các *widget* mà nó khởi tạo thông qua **core.WidgetManager**
(tiện việc từ ngoài gọi tới hay từ trong gọi ra)

Xử lý các event đến từ người dùng: Event Handler được thiết kế theo
design pattern **Observe (Pub/Sub).** (xem observer pattern ở file ./docs/observer_pattern.txt)

Các method xử lý của controller sẽ nằm ở **windows.handlers.
{controller_name}Handler**

**Init** xong BaseController sẽ tự động connect các slot & signal của Qt
từ slotmap được khai báo trên controller -- thông qua property
***slot_map*** đưa vào super().\_\_init\_\_.\
**Controller** extend từ **BaseController** bắt buộc phải có property
này. Nếu không sẽ raise ValueError

**slot_map:**

-   type dict

-   key = event name

-   value là list có 2 items. Trong đó:

    -   item 0 là widgetName (property của controller là gì thì
        widgetName tên đó)

    -   item 1 là sự kiện của widget đó (string theo qt)

> ví dụ: tại MainController khai báo\
> { \'open_btn_click\': \[\'pushButton\', \'clicked\'\] }
>
> Mapping như trên biểu thị: **event** *clicked* **của widget**
> *pushButton* **sẽ trigger** Publisher **publish sự kiện**
> *open_btn_click.* **Tương ứng tất cả các** *Subscribers **(ở đây là
> *** *MainControllerHandler* **) sẽ call method name =**
> *on_open_btn_click*

---

Ngoài ra còn có **Component** là dạng cây thư mục bên trong windows. 
Mỗi thư mục component có cấu trúc như thư mục của windows.
mỗi component có thể có nhiều widget,component có thể được tái sử dụng cho nhiều windows khác nhau.
