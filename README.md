# FlappyWukong
Flappy Wukong is a classic Flappy Bird-style game where players control the character Wukong as he flies through obstacles in the form of columns.


            FLAPPY WUKONG - README

1. THÔNG TIN SẢN PHẨM
---------------------
Flappy Wukong là một trò chơi theo phong cách "Flappy Bird" cổ điển, 
trong đó người chơi điều khiển nhân vật Ngộ Không bay qua các chướng ngại vật là những chiếc cột. 
Trò chơi có đồ họa tùy chỉnh và hỗ trợ hai chế độ điều khiển: bàn phím truyền thống và cử chỉ tay thông qua webcam.

Mục tiêu của trò chơi là điều khiển Ngộ Không bay càng xa càng tốt để ghi điểm cao.

2. CÔNG NGHỆ ĐƯỢC DÙNG
-----------------------
- Ngôn ngữ lập trình: Python
- Thư viện game: Pygame (dùng để xây dựng game, xử lý đồ họa, sự kiện và âm thanh)
- Thị giác máy tính: OpenCV (dùng để truy cập và xử lý hình ảnh từ webcam)
- Nhận dạng cử chỉ: Mediapipe (dùng để theo dõi các điểm mốc trên bàn tay và chuyển thành tín hiệu điều khiển)

3. INPUT (ĐẦU VÀO)
------------------
Trò chơi chấp nhận hai loại đầu vào từ người chơi:

- **Bàn phím:**
  - `SPACE`: Khi ở chế độ "Keyboard", nhấn để Ngộ Không bay lên. Khi ở màn hình "Game Over", nhấn để chơi lại.
  - `UP`/`DOWN` hoặc `W`/`S`: Dùng để điều hướng trong menu chính.
  - `ENTER`/`SPACE`: Chọn chế độ chơi trong menu.
  - `ESC`: Thoát khỏi màn chơi hiện tại và quay về menu chính.

- **Cử chỉ tay (Gesture):**
  - Yêu cầu có webcam.
  - Di chuyển bàn tay của bạn lên hoặc xuống trước webcam. Vị trí theo chiều dọc của cổ tay sẽ điều khiển trực tiếp vị trí của Ngộ Không trên màn hình.

4. OUTPUT (ĐẦU RA)
-------------------
- **Cửa sổ game:** Hiển thị trò chơi Flappy Wukong.
- **Menu chính:** Cho phép người chơi chọn chế độ điều khiển (Bàn phím hoặc Cử chỉ).
- **Màn hình chơi game:** Hiển thị nhân vật Ngộ Không, các cột, điểm số hiện tại và nền game.
- **Khung webcam:** Khi ở chế độ "Gesture", một khung hình nhỏ hiển thị hình ảnh từ webcam sẽ xuất hiện ở góc dưới bên phải màn hình.
- **Màn hình kết thúc (Game Over):** Hiển thị khi người chơi thua, bao gồm điểm số cuối cùng và điểm cao nhất.

5. CÁCH CHẠY SẢN PHẨM
----------------------
Để chạy trò chơi, hãy làm theo các bước sau:

**Bước 1: Cài đặt các thư viện cần thiết**
Mở terminal hoặc command prompt và chạy lệnh sau để cài đặt tất cả các thư viện được liệt kê trong file `requirements.txt`:
pip install -r requirements.txt

**Bước 2: Chuẩn bị tài nguyên game**
Đảm bảo rằng các tài nguyên của game (hình ảnh, phông chữ) được đặt đúng cấu trúc thư mục như trong mã nguồn. Cụ thể, bạn cần có một thư mục tên `framework` và các file phông chữ (`TMC-Ong Do.TTF`, `04B_19.TTF`) ngang hàng với file `main.py`.

Cấu trúc thư mục dự kiến:
/FlappyWukong
|-- main.py
|-- hand_detector.py
|-- requirements.txt
|-- readme.txt
|-- TMC-Ong Do.TTF
|-- 04B_19.TTF
|-- /framework
    |-- bg.jpg
    |-- floor.png
    |-- character.png
    |-- pipe.png

**Bước 3: Chạy game**
Sử dụng lệnh sau trong terminal hoặc command prompt tại thư mục gốc của dự án:
python main.py

6. CÁCH TƯƠNG TÁC VỚI SẢN PHẨM
--------------------------------
- **Tại Menu chính:** Dùng phím mũi tên LÊN/XUỐNG để chọn "Keyboard" hoặc "Gesture", sau đó nhấn ENTER để bắt đầu.
- **Nếu chọn "Keyboard":** Nhấn phím SPACE để giữ cho Ngộ Không không bị rơi và bay qua giữa các cây cột.
- **Nếu chọn "Gesture":** Đưa tay của bạn vào vùng nhận diện của webcam. Di chuyển tay lên xuống để điều khiển Ngộ Không. Một cửa sổ nhỏ hiển thị hình ảnh webcam sẽ giúp bạn điều chỉnh vị trí tay.
- **Trong khi chơi:** Nhấn phím `ESC` bất cứ lúc nào để quay lại menu chính.
- **Khi thua:** Màn hình "Game Over" sẽ hiện ra. Nhấn `SPACE` để bắt đầu một lượt chơi mới.
