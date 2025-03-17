# ADBot - Công cụ phân tích nội dung tự động

ADBot là một công cụ tự động phân tích nội dung từ các bài viết trên các trang báo điện tử, sử dụng AI để tóm tắt và phân tích nội dung.

## Tính năng

- Tự động trích xuất nội dung từ các bài viết báo điện tử
- Phân tích nội dung sử dụng AI (DeepSeek hoặc GPT-3.5)
- Tự động cập nhật kết quả vào Google Sheets
- Hỗ trợ nhiều định dạng URL khác nhau
- Tự động backup dữ liệu

## Yêu cầu

- Python 3.8 trở lên
- Tài khoản OpenRouter (cho DeepSeek) hoặc OpenAI (cho GPT-3.5)
- Tài khoản Google Cloud với Google Sheets API được bật
- Các thư viện Python cần thiết (xem requirements.txt)

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/MaiHongPhong1902/adbot.git
cd adbot
```

2. Tạo môi trường ảo và kích hoạt:
```bash
conda create -n Bot python=3.8
conda activate Bot
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

4. Cấu hình các file nhạy cảm:
   - Copy file `.env.example` thành `.env` và điền các API key của bạn
   - Tạo file `credentials.json` từ Google Cloud Console và đặt vào thư mục gốc
   - KHÔNG commit các file này lên git

5. Tạo Service Account và tải credentials:
- Truy cập Google Cloud Console
- Tạo project mới hoặc chọn project có sẵn
- Bật Google Sheets API
- Tạo Service Account và tải file credentials.json
- Đặt file credentials.json vào thư mục gốc của project

## Lưu ý quan trọng

- KHÔNG commit các file nhạy cảm lên git:
  - `.env` (chứa API keys)
  - `credentials.json` (chứa Google Cloud credentials)
  - Các file backup
- Các file này đã được thêm vào `.gitignore`
- Nếu vô tình commit các file này, hãy xóa chúng khỏi git history ngay lập tức

## Cách sử dụng

1. Chạy chương trình:
```bash
python main.py
```

2. Nhập URL bài viết cần phân tích khi được yêu cầu

3. Chọn model AI để phân tích (DeepSeek hoặc GPT-3.5)

4. Kết quả sẽ được tự động cập nhật vào Google Sheets

## Cấu trúc dữ liệu

Kết quả phân tích được lưu trong Google Sheets với các cột:
- URL: Link bài viết gốc
- Chủ đề: Chủ đề chính của bài viết
- Tóm tắt: Tóm tắt ngắn gọn nội dung
- Kết luận: Kết luận chính từ bài viết
- Timestamp: Thời gian phân tích

## Backup dữ liệu

Dữ liệu được tự động backup vào file JSON theo ngày:
- Format: backup_YYYYMMDD.json
- Mỗi entry chứa timestamp, URL và kết quả phân tích

## Xử lý lỗi

Nếu gặp lỗi quyền truy cập Google Sheets:
1. Mở Google Sheet tại URL được cung cấp
2. Click nút Share
3. Thêm email service account với quyền Editor
4. Chạy lại chương trình

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork repository
2. Tạo branch mới
3. Commit các thay đổi
4. Push lên branch
5. Tạo Pull Request

## License

MIT License

Copyright (c) 2024 Mai Hong Phong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Tác giả

- **Mai Hong Phong**
  - Email: maihongphong.work@gmail.com
  - SĐT: 0865243215
  - GitHub: [@MaiHongPhong1902](https://github.com/MaiHongPhong1902)
  - Trường: Đại học Sư phạm Kỹ thuật TP. HCM
