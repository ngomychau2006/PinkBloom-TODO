# PinkBloom TODO

Ứng dụng quản lý công việc TODO chạy local, sử dụng Python Flask và SQLite.

## 1. Yêu cầu
- Python 3.9 trở lên
- Visual Studio Code
- Extension Python (khuyến nghị)

## 2. Cài đặt và chạy
Mở thư mục `PinkBloom_TODO` trong VS Code, mở Terminal và chạy:

```bash
python -m venv .venv
```

Kích hoạt môi trường ảo:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Cài thư viện:
```bash
pip install -r requirements.txt
```

Chạy ứng dụng:
```bash
python app.py
```

Mở trình duyệt tại: http://127.0.0.1:5000

## 3. Database
- SQLite tự động tạo file `todo.db` trong thư mục dự án ở lần chạy đầu.
- Bảng `tasks` lưu thông tin công việc: tên, mô tả, danh mục, mức ưu tiên, trạng thái, hạn hoàn thành, đánh dấu quan trọng và ngày tạo.
- Không cần cài MySQL hoặc cấu hình server database.

## 4. Chức năng
- Thêm / sửa / xóa công việc.
- Cập nhật trạng thái nhanh.
- Thống kê tổng số, hoàn thành, đang làm, chưa bắt đầu, quá hạn và tỷ lệ hoàn thành.
- Tìm kiếm, lọc theo trạng thái / danh mục / ưu tiên.
- Đánh dấu công việc quan trọng.
- Cảnh báo hạn công việc.
- Responsive cho màn hình nhỏ.

## 5. Cấu trúc thư mục
```text
PinkBloom_TODO/
├── app.py
├── requirements.txt
├── README.md
├── todo.db              # tự sinh khi chạy
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```
