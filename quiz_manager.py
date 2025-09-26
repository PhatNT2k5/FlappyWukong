# quiz_manager.py
import random

# Bộ 25 câu hỏi về AI dành cho học sinh cấp ba
AI_QUESTIONS = [
    # --- Khái niệm cơ bản ---
    {
        "question": "AI là viết tắt của từ gì?",
        "options": ["A. Artificial Intelligence", "B. Automated Input", "C. Associated Ideas", "D. Algorithmic Integration"],
        "correct_answer": "A"
    },
    {
        "question": "Mục tiêu chính của Trí tuệ nhân tạo là gì?",
        "options": [
            "A. Thay thế hoàn toàn con người trong mọi công việc",
            "B. Tạo ra máy móc có thể suy nghĩ, học hỏi và giải quyết vấn đề",
            "C. Chỉ để chơi các trò chơi phức tạp như cờ vua, cờ vây",
            "D. Làm cho máy tính chạy nhanh hơn"
        ],
        "correct_answer": "B"
    },
    {
        "question": "Đâu là một ví dụ về 'AI hẹp' (Narrow AI)?",
        "options": [
            "A. Một robot có ý thức và cảm xúc như con người",
            "B. Một trợ lý ảo như Siri hoặc Google Assistant",
            "C. Một hệ thống có thể làm bất kỳ công việc trí tuệ nào mà con người có thể làm",
            "D. Một nhân vật trong phim khoa học viễn tưởng"
        ],
        "correct_answer": "B"
    },
    {
        "question": "Học máy (Machine Learning) được định nghĩa là gì?",
        "options": [
            "A. Một cỗ máy được lập trình sẵn mọi quy tắc",
            "B. Khả năng của máy tính tự học hỏi từ dữ liệu mà không cần lập trình tường minh",
            "C. Một loại phần cứng máy tính đặc biệt",
            "D. Tốc độ xử lý của máy tính"
        ],
        "correct_answer": "B"
    },
    {
        "question": "'Deep Learning' là một nhánh của lĩnh vực nào?",
        "options": ["A. Mạng máy tính", "B. An ninh mạng", "C. Học máy (Machine Learning)", "D. Thiết kế web"],
        "correct_answer": "C"
    },

    # --- Lịch sử và Nhân vật ---
    {
        "question": "Ai được coi là 'cha đẻ của trí tuệ nhân tạo'?",
        "options": ["A. Bill Gates", "B. Alan Turing", "C. Steve Jobs", "D. Mark Zuckerberg"],
        "correct_answer": "B"
    },
    {
        "question": "Alan Turing đã đề xuất phép thử nào để kiểm tra trí thông minh của máy móc?",
        "options": ["A. The Coffee Test", "B. The Mirror Test", "C. The Voight-Kampff Test", "D. The Imitation Game (Turing Test)"],
        "correct_answer": "D"
    },
    {
        "question": "Năm 1997, siêu máy tính nào của IBM đã đánh bại nhà vô địch cờ vua thế giới Garry Kasparov?",
        "options": ["A. Watson", "B. AlphaGo", "C. Deep Blue", "D. Hal 9000"],
        "correct_answer": "C"
    },
    {
        "question": "Sự kiện nào đã đánh dấu một cột mốc quan trọng khi AI của Google DeepMind đánh bại kỳ thủ cờ vây hàng đầu thế giới Lee Sedol?",
        "options": ["A. Trận đấu cờ vua năm 1997", "B. Cuộc thi Jeopardy! năm 2011", "C. Trận đấu AlphaGo và Lee Sedol năm 2016", "D. Sự ra mắt của iPhone"],
        "correct_answer": "C"
    },

    # --- Các loại hình học máy ---
    {
        "question": "Trong Machine Learning, 'Học tăng cường' (Reinforcement Learning) là gì?",
        "options": ["A. Học từ dữ liệu được dán nhãn", "B. Học bằng cách thử và sai để tối đa hóa phần thưởng", "C. Học để phân loại dữ liệu", "D. Học cách nén dữ liệu"],
        "correct_answer": "B"
    },
    {
        "question": "Khi bạn huấn luyện một mô hình AI để phân biệt giữa ảnh chó và mèo bằng cách cung cấp cho nó hàng nghìn bức ảnh đã được dán nhãn, đó là loại học máy nào?",
        "options": ["A. Học có giám sát (Supervised Learning)", "B. Học không giám sát (Unsupervised Learning)", "C. Học tăng cường (Reinforcement Learning)", "D. Học bán giám sát (Semi-supervised Learning)"],
        "correct_answer": "A"
    },
    {
        "question": "Một thuật toán AI tự động nhóm các khách hàng có hành vi mua sắm tương tự nhau mà không có thông tin trước. Đây là ví dụ của loại học nào?",
        "options": ["A. Học có giám sát", "B. Học không giám sát", "C. Học tăng cường", "D. Học vẹt"],
        "correct_answer": "B"
    },

    # --- Ứng dụng thực tế ---
    {
        "question": "Lĩnh vực nào của AI tập trung vào việc máy tính 'nhìn' và hiểu hình ảnh?",
        "options": ["A. Natural Language Processing", "B. Computer Vision", "C. Reinforcement Learning", "D. Expert Systems"],
        "correct_answer": "B"
    },
    {
        "question": "Khi bạn nói chuyện với một trợ lý ảo, công nghệ AI nào đang được sử dụng để hiểu lời nói của bạn?",
        "options": ["A. Thị giác máy tính (Computer Vision)", "B. Xử lý ngôn ngữ tự nhiên (NLP)", "C. Học tăng cường", "D. Hệ chuyên gia"],
        "correct_answer": "B"
    },
    {
        "question": "Hệ thống gợi ý sản phẩm trên các trang thương mại điện tử (như Amazon, Tiki) sử dụng AI để làm gì?",
        "options": [
            "A. Tính toán giá vận chuyển",
            "B. Cá nhân hóa trải nghiệm mua sắm bằng cách đề xuất các mặt hàng bạn có thể thích",
            "C. Quản lý kho hàng",
            "D. Thiết kế giao diện trang web"
        ],
        "correct_answer": "B"
    },
    {
        "question": "Xe tự lái chủ yếu dựa vào sự kết hợp của những công nghệ AI nào?",
        "options": [
            "A. Xử lý ngôn ngữ tự nhiên và hệ chuyên gia",
            "B. Thị giác máy tính và học máy",
            "C. AI tạo sinh và robot",
            "D. Phân tích dữ liệu lớn và mạng xã hội"
        ],
        "correct_answer": "B"
    },
    {
        "question": "Công nghệ 'Deepfake' sử dụng AI để làm gì?",
        "options": [
            "A. Dịch thuật ngôn ngữ",
            "B. Tạo ra hình ảnh hoặc video giả mạo, ghép mặt người này vào video của người khác",
            "C. Chẩn đoán bệnh tật",
            "D. Điều khiển robot công nghiệp"
        ],
        "correct_answer": "B"
    },
    {
        "question": "Trợ lý ảo nào sau đây được phát triển bởi Apple?",
        "options": ["A. Alexa", "B. Siri", "C. Google Assistant", "D. Cortana"],
        "correct_answer": "B"
    },
    {
        "question": "Mô hình ngôn ngữ lớn (LLM) nào được phát triển bởi Google?",
        "options": ["A. GPT-4", "B. Llama", "C. Gemini", "D. Claude"],
        "correct_answer": "C"
    },
    {
        "question": "Trong y tế, AI có thể được ứng dụng để làm gì?",
        "options": [
            "A. Phân tích hình ảnh y tế (X-quang, MRI) để phát hiện bệnh",
            "B. Thay thế hoàn toàn các bác sĩ",
            "C. Sản xuất thuốc generic",
            "D. Quản lý lịch hẹn của bệnh viện"
        ],
        "correct_answer": "A"
    },
    
    # --- Đạo đức và Tương lai ---
    {
        "question": "Vấn đề 'thiên vị' (bias) trong AI có nghĩa là gì?",
        "options": [
            "A. AI luôn đưa ra quyết định công bằng",
            "B. AI có thể đưa ra các quyết định không công bằng do học từ dữ liệu thiên vị của con người",
            "C. AI có sở thích riêng",
            "D. AI hoạt động chậm hơn dự kiến"
        ],
        "correct_answer": "B"
    },
    {
        "question": "Mạng nơ-ron nhân tạo (Artificial Neural Network) được lấy cảm hứng từ đâu?",
        "options": ["A. Mạng lưới máy tính toàn cầu (Internet)", "B. Cấu trúc của bộ não con người", "C. Mạng lưới giao thông", "D. Tổ ong"],
        "correct_answer": "B"
    },
    {
        "question": "AI tạo sinh (Generative AI) là gì?",
        "options": [
            "A. Một AI chỉ có thể phân loại dữ liệu",
            "B. Một AI có khả năng tạo ra nội dung mới như văn bản, hình ảnh, âm nhạc",
            "C. Một AI chỉ chơi game",
            "D. Một loại virus máy tính"
        ],
        "correct_answer": "B"
    },
    {
        "question": "Đâu là một rủi ro tiềm tàng của việc phát triển AI quá mạnh mẽ?",
        "options": [
            "A. Máy tính sẽ trở nên quá rẻ",
            "B. Mất việc làm ở một số ngành nghề",
            "C. Internet sẽ nhanh hơn",
            "D. Pin điện thoại sẽ bền hơn"
        ],
        "correct_answer": "B"
    },
    {
        "question": "Thuật ngữ 'Hộp đen' (Black Box) trong AI ám chỉ điều gì?",
        "options": [
            "A. Giao diện người dùng của một ứng dụng AI",
            "B. Phần cứng chứa chip AI",
            "C. Tình trạng khó giải thích tại sao một mô hình AI lại đưa ra một quyết định cụ thể",
            "D. Một cơ sở dữ liệu an toàn"
        ],
        "correct_answer": "C"
    }
]

class QuizManager:
    def __init__(self):
        """Khởi tạo trình quản lý câu đố."""
        self.questions = AI_QUESTIONS
        self.used_question_indices = []

    def get_random_question(self):
        """
        Lấy một câu hỏi ngẫu nhiên chưa được sử dụng trong phiên chơi này.
        Nếu tất cả đã được sử dụng, nó sẽ bắt đầu lại.
        """
        available_indices = list(set(range(len(self.questions))) - set(self.used_question_indices))

        if not available_indices:
            # Nếu đã hết câu hỏi, reset lại danh sách đã dùng
            print("\n--- Bạn đã hoàn thành tất cả câu hỏi! Bắt đầu lại từ đầu. ---\n")
            self.used_question_indices = []
            available_indices = list(range(len(self.questions)))

        chosen_index = random.choice(available_indices)
        self.used_question_indices.append(chosen_index)
        
        return self.questions[chosen_index]

    def check_answer(self, question, selected_option_key):
        """
        Kiểm tra xem câu trả lời đã chọn (ví dụ: 'A') có đúng không.
        - question: dictionary của câu hỏi hiện tại.
        - selected_option_key: chuỗi 'A', 'B', 'C', hoặc 'D'.
        """
        return question["correct_answer"].upper() == selected_option_key.upper()

# Ví dụ cách sử dụng (bạn có thể chạy phần này để kiểm tra)
if __name__ == "__main__":
    quiz_manager = QuizManager()
    score = 0
    total_questions = len(quiz_manager.questions)

    for i in range(total_questions):
        current_question = quiz_manager.get_random_question()
        
        print(f"\nCâu hỏi {i + 1}/{total_questions}: {current_question['question']}")
        for option in current_question["options"]:
            print(option)
            
        user_answer = input("Nhập câu trả lời của bạn (A, B, C, hoặc D): ").strip()
        
        is_correct = quiz_manager.check_answer(current_question, user_answer)
        
        if is_correct:
            print("Chính xác! 🎉")
            score += 1
        else:
            print(f"Không đúng. Đáp án đúng là: {current_question['correct_answer']}")
    
    print(f"\n--- KẾT THÚC ---")
    print(f"Bạn đã trả lời đúng {score}/{total_questions} câu hỏi.")