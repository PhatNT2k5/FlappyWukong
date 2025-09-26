# hand_detector.py
import cv2
import mediapipe as mp

class HandMotionDetector:
    """
    Lớp chịu trách nhiệm phát hiện chuyển động của bàn tay, vị trí cổ tay
    và trạng thái nắm/mở của bàn tay bằng MediaPipe.
    """
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.65, min_tracking_confidence=0.65)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def _is_fist(self, hand_landmarks):
        """
        Kiểm tra xem bàn tay có đang nắm lại không bằng cách so sánh vị trí
        của các đầu ngón tay với các khớp giữa của chúng.
        """
        try:
            # Vị trí các đầu ngón tay (trỏ, giữa, nhẫn, út)
            finger_tips_y = [
                hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y,
                hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y,
                hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y,
                hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
            ]
            # Vị trí các khớp giữa ngón tay (PIP)
            finger_pips_y = [
                hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y,
                hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y,
                hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y,
                hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP].y
            ]
            # Nếu tất cả các đầu ngón tay đều ở thấp hơn (giá trị y lớn hơn) khớp giữa -> nắm tay
            return all(tip > pip for tip, pip in zip(finger_tips_y, finger_pips_y))
        except:
            return False

    def track_hand(self):
        """
        Theo dõi bàn tay, trả về vị trí, trạng thái nắm tay và khung hình camera.
        Returns:
            Tuple[tuple | None, bool, np.ndarray | None]: (hand_pos, is_fist, frame)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, False, None
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        hand_pos, is_fist = None, False

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_drawing.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
            wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
            hand_pos = (wrist.x, wrist.y)
            is_fist = self._is_fist(hand_landmarks)

        # Hiển thị trạng thái để người dùng dễ dàng nhận biết
        status_text = "Fist Closed (Chon)" if is_fist else "Hand Open (Di chuyen)"
        color = (0, 255, 0) if is_fist else (0, 0, 255)
        cv2.putText(frame, status_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            
        return hand_pos, is_fist, frame

    def release(self):
        """Giải phóng camera."""
        self.cap.release()