import pygame
import sys
import random
from hand_detector import HandMotionDetector
from quiz_manager import QuizManager
import threading
import cv2
import time
import json
import textwrap
import math  # <<< THÊM MỚI: Cần cho hiệu ứng animation

# =================================================================================
# --- CONSTANTS & SETTINGS ---
# =================================================================================
# Screen & Frame Rate
WIDTH, HEIGHT = 1920, 1080
FPS = 120

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW_BRIGHT = (255, 255, 0)
GREEN_LIME = (50, 205, 50) # Màu xanh lá cho hiệu ứng
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

# Game Mechanics
PIPE_SPACING = 1200
PIPE_HEIGHT_CHOICES = [550, 650, 750, 850, 900, 950]
FLOOR_Y_POS = 900
KEYBOARD_GRAVITY = 0.28
KEYBOARD_JUMP_STRENGTH = -8
GESTURE_SMOOTHING_FACTOR = 0.1

# Quiz Mechanics
QUIZ_TRIGGER_SCORE = 5
QUIZ_TIME_LIMIT = 30
CORRECT_FX_DURATION = 1500 # <<< THÊM MỚI: Thời gian hiệu ứng (ms)

# File
LEADERBOARD_FILE = 'leaderboard.json'

# =================================================================================
# --- FUNCTIONS ---
# =================================================================================
def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, 'r') as f: return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return []

def save_to_leaderboard(player_name, new_score):
    leaderboard = load_leaderboard()
    leaderboard.append({'name': player_name, 'score': new_score})
    leaderboard.sort(key=lambda item: item['score'], reverse=True)
    with open(LEADERBOARD_FILE, 'w') as f: json.dump(leaderboard[:10], f, indent=4)

# =================================================================================
# --- GAME OBJECT CLASSES ---
# =================================================================================
class Bird:
    # ... (Không thay đổi)
    def __init__(self, surface):
        self.original_surface = pygame.transform.scale(surface, (int(surface.get_width() * 0.22), int(surface.get_height() * 0.22)))
        self.rect = self.original_surface.get_rect(center=(200, 500))
        self.hitbox = self.rect.inflate(-30, -30)
        self.movement = 0
    def apply_gravity(self):
        self.movement += KEYBOARD_GRAVITY
        self.rect.centery += self.movement
        self.hitbox.centery = self.rect.centery
    def jump(self): self.movement = KEYBOARD_JUMP_STRENGTH
    def draw(self, screen, offset=(0,0)):
        draw_rect = self.rect.copy()
        draw_rect.topleft = (self.rect.left + offset[0], self.rect.top + offset[1])
        rotated_surface = pygame.transform.rotozoom(self.original_surface, -self.movement * 3, 1)
        screen.blit(rotated_surface, draw_rect)
    def reset(self):
        self.rect.center = (200, 500)
        self.hitbox.center = (200, 500)
        self.movement = 0

class Pipe:
    # ... (Không thay đổi)
    def __init__(self, surface, x, y, is_top):
        self.original_surface = surface
        if is_top:
            self.surface = pygame.transform.flip(self.original_surface, False, True)
            self.rect = self.surface.get_rect(midbottom=(x, y))
        else:
            self.surface = self.original_surface
            self.rect = self.surface.get_rect(midtop=(x, y))
        self.hitbox = self.rect.inflate(-35, -35)
        self.passed = False
    def move(self):
        self.rect.centerx -= 7
        self.hitbox.centerx = self.rect.centerx
    def draw(self, screen, offset=(0,0)):
        draw_rect = self.rect.copy()
        draw_rect.topleft = (self.rect.left + offset[0], self.rect.top + offset[1])
        screen.blit(self.surface, draw_rect)


class Floor:
    # ... (Không thay đổi)
    def __init__(self, surface, y_pos):
        self.surface = pygame.transform.scale(surface, (WIDTH, surface.get_height()))
        self.rect1 = self.surface.get_rect(topleft=(0, y_pos))
        self.rect2 = self.surface.get_rect(topleft=(WIDTH, y_pos))
    def move(self):
        self.rect1.x -= 3; self.rect2.x -= 3
        if self.rect1.right <= 0: self.rect1.x = self.rect2.right
        if self.rect2.right <= 0: self.rect2.x = self.rect1.right
    def draw(self, screen, offset=(0,0)):
        rect1_offset = self.rect1.copy(); rect2_offset = self.rect2.copy()
        rect1_offset.topleft = (self.rect1.left + offset[0], self.rect1.top + offset[1])
        rect2_offset.topleft = (self.rect2.left + offset[0], self.rect2.top + offset[1])
        screen.blit(self.surface, rect1_offset); screen.blit(self.surface, rect2_offset)


class DeathParticle:
    # ... (Không thay đổi)
    def __init__(self, x, y):
        self.x, self.y = x, y; self.vx, self.vy = random.uniform(-4, 4), random.uniform(-5, 5)
        self.alpha = 255; self.radius = random.randint(2, 6)
        self.color = random.choice([(255, 215, 0), (255, 165, 0), (255, 140, 0)])
    def update(self):
        self.x += self.vx; self.y += self.vy; self.vy += 0.2; self.alpha -= 10
        if self.alpha < 0: self.alpha = 0
    def draw(self, screen):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
            screen.blit(s, (self.x - self.radius, self.y - self.radius))

# <<< THÊM MỚI: Lớp hạt cho hiệu ứng trả lời đúng >>>
class CorrectAnswerParticle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.alpha = 255
        self.radius = random.randint(4, 9)
        self.color = random.choice([YELLOW_BRIGHT, GREEN_LIME, WHITE])
        self.decay = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.decay
        if self.alpha < 0: self.alpha = 0

    def draw(self, screen):
        if self.alpha > 0:
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
            screen.blit(s, (self.x - self.radius, self.y - self.radius))

class BonkStick:
    # ... (Không thay đổi)
    def __init__(self, surface, target_rect):
        self.original_surface = pygame.transform.rotozoom(surface, 35, 0.75)
        self.rect = self.original_surface.get_rect(center=(target_rect.centerx + 120, target_rect.top - 200))
        self.angle = 90
        self.rotation_speed = 0
        self.acceleration = -1.5
        self.state = "swinging"
        self.just_bonked = False
        self.bonk_sound = pygame.mixer.Sound('sounds/hit.mp3')
    def update(self):
        self.just_bonked = False
        if self.state == "swinging":
            self.rotation_speed += self.acceleration
            self.angle += self.rotation_speed
            if self.angle <= -80:
                self.angle = -80
                self.bonk_sound.play()
                self.state = "recoiling"
                self.rotation_speed = 10
                self.just_bonked = True
        elif self.state == "recoiling":
            self.angle += self.rotation_speed
            self.rotation_speed *= 0.85
            if abs(self.rotation_speed) < 1:
                self.rotation_speed = 0
        return self.just_bonked
    def draw(self, screen, offset=(0,0)):
        rotated_surface = pygame.transform.rotozoom(self.original_surface, self.angle, 1)
        rotated_rect = rotated_surface.get_rect(center=self.rect.center)
        rotated_rect.x += offset[0]
        rotated_rect.y += offset[1]
        screen.blit(rotated_surface, rotated_rect)

class Particle:
    # ... (Không thay đổi)
    def __init__(self, screen_width, screen_height):
        self.width, self.height = screen_width, screen_height
        self.x, self.y = random.randint(0, self.width), random.randint(self.height, self.height + 150)
        self.speed, self.radius = random.uniform(0.5, 2.5), random.randint(1, 4)
        self.color = random.choice([(255, 215, 0), (255, 223, 0), (255, 193, 7)])
    def move_and_draw(self, screen):
        self.y -= self.speed
        if self.y < -self.radius: self.y = random.randint(self.height, self.height + 150); self.x = random.randint(0, self.width)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

# =================================================================================
# --- MAIN GAME CLASS ---
# =================================================================================
class Game:
    def __init__(self, control_mode, player_name):
        # General Setup
        self.control_mode = control_mode; self.player_name = player_name
        self.screen = pygame.display.get_surface(); self.clock = pygame.time.Clock()
        self._load_assets_and_fonts()

        # Game Objects
        self.bird = Bird(self.bird_img); self.floor = Floor(self.floor_img, FLOOR_Y_POS); self.pipe_list = []

        # State Management
        self.game_state = 'playing'
        self.score = 0; self.death_particles = []
        self.leaderboard = load_leaderboard(); self.top_score_entry = self.leaderboard[0] if self.leaderboard else None

        # Timers & Events
        self.spawnpipe_event = pygame.USEREVENT + 1

        # Quiz Management
        self.quiz_manager = QuizManager(); self.current_quiz = None; self.quiz_timer_start = 0; self.last_quiz_score = -1

        # Bonk & Correct Answer Effects
        self.bonk_stick = None; self.bonk_hit_time = None; self.screen_shake = 0
        # <<< THÊM MỚI: Các biến cho hiệu ứng trả lời đúng >>>
        self.correct_fx_particles = []; self.correct_fx_start_time = None

        # Gesture Control
        self.hand_x_pos, self.hand_y_pos = None, None
        self.is_fist_closed = False; self.answered_this_quiz = False
        self.latest_cam_frame = None
        if self.control_mode == "gesture":
            self.hand_detector = HandMotionDetector()
            self.gesture_thread = threading.Thread(target=self._gesture_loop, daemon=True)
            self.gesture_thread.start()

        self._reset_game()

    def _load_assets_and_fonts(self):
        # Fonts
        self.game_font = pygame.font.Font('font/TMC-Ong Do.TTF', 70)
        self.quiz_font = pygame.font.Font('font/VT323-Regular.ttf', 40)
        self.quiz_question_font = pygame.font.Font('font/VT323-Regular.ttf', 45)
        self.menu_font = pygame.font.Font('font/04B_19.TTF', 40)
        # <<< THÊM MỚI: Font cho chữ "Chính Xác!" >>>
        self.correct_fx_font = pygame.font.Font('font/TMC-Ong Do.TTF', 150)

        # Images
        self.bg_img = pygame.transform.scale(pygame.image.load('Assets/bg.png').convert(), (WIDTH, HEIGHT))
        self.floor_img = pygame.image.load('Assets/floor.png').convert_alpha()
        bird_img_raw = pygame.image.load('Assets/character_2.png').convert_alpha()
        self.bird_img = pygame.transform.scale2x(bird_img_raw)
        pipe_img_raw = pygame.image.load('Assets/pipe.png').convert_alpha()
        pipe_img_scaled = pygame.transform.scale2x(pipe_img_raw)
        self.pipe_img = pygame.transform.scale(pipe_img_scaled, (int(pipe_img_scaled.get_width()*0.5), int(pipe_img_scaled.get_height()*0.4)))
        self.bonk_stick_img = pygame.image.load('Assets/pipe.png').convert_alpha()

        # Sounds
        self.jump_sound = pygame.mixer.Sound('sounds/jump.mp3'); self.score_sound = pygame.mixer.Sound('sounds/point.mp3')
        self.hit_sound = pygame.mixer.Sound('sounds/hit.mp3'); self.die_sound = pygame.mixer.Sound('sounds/die.mp3')
        # <<< THÊM MỚI: Âm thanh khi trả lời đúng (nhớ tạo file sounds/correct.mp3) >>>
        self.correct_sound = pygame.mixer.Sound('sounds/point.mp3')
        pygame.mixer.music.load('sounds/background.mp3'); pygame.mixer.music.set_volume(0.15); pygame.mixer.music.play(-1)

    def run(self):
        while True:
            status = self._handle_events()
            if status != 'CONTINUE':
                if hasattr(self, 'hand_detector') and self.hand_detector: self.hand_detector.release(); self.hand_detector = None
                return status
            self._update(); self._draw(); self.clock.tick(FPS)

    def _gesture_loop(self):
        while True:
            if not hasattr(self, 'hand_detector') or self.hand_detector is None: break
            hand_pos, is_fist, frame = self.hand_detector.track_hand()
            if self.game_state in ['playing', 'quiz']:
                self.is_fist_closed = is_fist
                if hand_pos: self.hand_x_pos, self.hand_y_pos = hand_pos
                else: self.hand_x_pos, self.hand_y_pos = None, None
            self.latest_cam_frame = frame

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 'QUIT'

            # --- Ngăn input khi đang có hiệu ứng ---
            if self.game_state == 'correct_fx': continue

            # --- Quiz Input (Keyboard) ---
            if self.game_state == 'quiz' and self.control_mode == 'keyboard' and event.type == pygame.KEYDOWN:
                answer_key_map = {pygame.K_a: 'A', pygame.K_b: 'B', pygame.K_c: 'C', pygame.K_d: 'D'}
                if event.key in answer_key_map:
                    self._handle_quiz_answer(answer_key_map[event.key]); return 'CONTINUE'

            # --- General Keyboard Input ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == 'game_over': self._save_score_if_any()
                    return 'MENU'
                if event.key == pygame.K_SPACE:
                    if self.game_state == 'playing' and self.control_mode == "keyboard": self.bird.jump(); self.jump_sound.play()
                    elif self.game_state == 'game_over': self._reset_game()

            # --- Pipe Spawning Event ---
            if event.type == self.spawnpipe_event and self.game_state == 'playing': self._create_pipes()
        return 'CONTINUE'

    def _update(self):
        # --- Playing State ---
        if self.game_state == 'playing':
            if self.control_mode == "keyboard": self.bird.apply_gravity()
            elif self.control_mode == "gesture" and self.hand_y_pos is not None and not self.is_fist_closed:
                target_y = self.hand_y_pos * HEIGHT
                new_y = self.bird.rect.centery + (target_y - self.bird.rect.centery) * GESTURE_SMOOTHING_FACTOR
                self.bird.movement = new_y - self.bird.rect.centery; self.bird.rect.centery = new_y; self.bird.hitbox.centery = self.bird.rect.centery
            
            self.floor.move()
            self.pipe_list = [pipe for pipe in self.pipe_list if pipe.rect.right > -50]
            for pipe in self.pipe_list: pipe.move()
            self._check_collisions(); self._update_score()

        # --- Quiz State ---
        elif self.game_state == 'quiz':
            if (pygame.time.get_ticks() - self.quiz_timer_start) / 1000 > QUIZ_TIME_LIMIT: self._handle_wrong_answer()
            if self.control_mode == 'gesture' and self.is_fist_closed and not self.answered_this_quiz and self.hand_x_pos is not None:
                answer_key = self._get_gesture_answer()
                if answer_key: self._handle_quiz_answer(answer_key); self.answered_this_quiz = True

        # --- Bonking State ---
        elif self.game_state == 'bonking':
            if self.bonk_stick and self.bonk_stick.update():
                self.bonk_hit_time = pygame.time.get_ticks(); self.screen_shake = 25; self.bird.movement = 12
            if self.bonk_hit_time and (pygame.time.get_ticks() - self.bonk_hit_time) > 750:
                self._trigger_explosion(bonk_mode=True); self.bonk_hit_time = None

        # --- Exploding State ---
        elif self.game_state == 'exploding':
            for particle in self.death_particles: particle.update()
            self.death_particles = [p for p in self.death_particles if p.alpha > 0]
            if not self.death_particles: self.game_state = 'game_over'

        # <<< THÊM MỚI: Trạng thái hiệu ứng trả lời đúng >>>
        elif self.game_state == 'correct_fx':
            self._update_correct_fx()


    def _draw(self):
        offset = (0, 0)
        if self.screen_shake > 0: self.screen_shake -= 1; offset = (random.randint(-8, 8), random.randint(-8, 8))
        
        self.screen.blit(self.bg_img, self.bg_img.get_rect(topleft=offset))
        
        if self.game_state == 'playing' or self.game_state == 'correct_fx': # <<< SỬA ĐỔI: Vẽ ống cả khi đang có hiệu ứng
            for pipe in self.pipe_list: pipe.draw(self.screen, offset)
        
        # <<< SỬA ĐỔI: Vẽ chim cả khi đang có hiệu ứng
        if self.game_state in ['playing', 'quiz', 'bonking', 'correct_fx']: self.bird.draw(self.screen, offset)
        elif self.game_state == 'exploding':
            for particle in self.death_particles: particle.draw(self.screen)
        
        # <<< SỬA ĐỔI: Vẽ sàn cả khi đang có hiệu ứng
        if self.game_state not in ['exploding']: self.floor.draw(self.screen, offset)
        if self.bonk_stick and self.game_state == 'bonking': self.bonk_stick.draw(self.screen, offset)
            
        self._draw_ui_overlays()
        pygame.display.update()

    def _draw_ui_overlays(self):
        if self.game_state == 'quiz': self._draw_quiz_ui()
        # <<< THÊM MỚI: Vẽ hiệu ứng trả lời đúng >>>
        if self.game_state == 'correct_fx': self._draw_correct_answer_effect()
        self._draw_score()
        if self.game_state == 'game_over': self._draw_game_over()
        if self.control_mode == "gesture" and self.latest_cam_frame is not None: self._draw_webcam()

    # <<< THÊM MỚI: Các hàm quản lý hiệu ứng >>>
    def _trigger_correct_answer_effect(self):
        self.game_state = 'correct_fx'
        self.correct_sound.play()
        self.current_quiz = None
        self.correct_fx_start_time = pygame.time.get_ticks()
        self.correct_fx_particles.clear()
        for _ in range(70):
             self.correct_fx_particles.append(CorrectAnswerParticle(WIDTH // 2, HEIGHT // 2))

    def _update_correct_fx(self):
        for p in self.correct_fx_particles:
            p.update()
        self.correct_fx_particles = [p for p in self.correct_fx_particles if p.alpha > 0]
        
        if pygame.time.get_ticks() - self.correct_fx_start_time > CORRECT_FX_DURATION:
            self.game_state = 'playing'
            self.correct_fx_start_time = None
            pygame.time.set_timer(self.spawnpipe_event, PIPE_SPACING)

    def _draw_correct_answer_effect(self):
        # Vẽ các hạt pháo hoa
        for p in self.correct_fx_particles:
            p.draw(self.screen)
            
        # Vẽ chữ "Chính Xác!" với hiệu ứng
        elapsed = pygame.time.get_ticks() - self.correct_fx_start_time
        progress = min(1.0, elapsed / (CORRECT_FX_DURATION * 0.8)) # Hoàn thành hiệu ứng chữ nhanh hơn
        
        # Hiệu ứng phóng to rồi nhỏ lại
        scale = 1.0 + 0.6 * math.sin(progress * math.pi)
        
        # Hiệu ứng mờ dần (bắt đầu mờ sau nửa thời gian)
        alpha = 255
        if progress > 0.5:
            alpha = max(0, 255 * (1 - (progress - 0.5) * 2))

        text_surf = self.correct_fx_font.render("Chính Xác!", True, YELLOW_BRIGHT)
        text_surf.set_alpha(alpha)
        
        scaled_surf = pygame.transform.rotozoom(text_surf, 0, scale)
        scaled_rect = scaled_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(scaled_surf, scaled_rect)


    def _trigger_explosion(self, sound=None, bonk_mode=False):
        # ... (Không thay đổi)
        if self.game_state == 'playing' or bonk_mode:
            if sound: sound.play()
            self.game_state = 'exploding'
            for _ in range(30): self.death_particles.append(DeathParticle(self.bird.rect.centerx, self.bird.rect.centery))
            pygame.time.set_timer(self.spawnpipe_event, 0)

    def _check_collisions(self):
        # ... (Không thay đổi)
        for pipe in self.pipe_list:
            if self.bird.hitbox.colliderect(pipe.hitbox):
                self._trigger_explosion(self.hit_sound); time.sleep(0.1); self.die_sound.play(); return
        if self.bird.hitbox.bottom >= FLOOR_Y_POS or self.bird.hitbox.top < -100:
            self._trigger_explosion(self.hit_sound); time.sleep(0.1); self.die_sound.play(); return

    def _create_pipes(self):
        # ... (Không thay đổi)
        random_pipe_pos = random.choice(PIPE_HEIGHT_CHOICES)
        top = Pipe(self.pipe_img, WIDTH + 100, random_pipe_pos - 300, is_top=True)
        bottom = Pipe(self.pipe_img, WIDTH + 100, random_pipe_pos, is_top=False)
        self.pipe_list.extend([top, bottom])

    def _update_score(self):
        # ... (Không thay đổi)
        if self.game_state != 'playing': return
        current_int_score = int(self.score)
        if current_int_score > 0 and current_int_score % QUIZ_TRIGGER_SCORE == 0 and current_int_score != self.last_quiz_score:
            self.last_quiz_score = current_int_score; self._start_quiz(); return
        for pipe in self.pipe_list:
            if not pipe.passed and pipe.rect.centerx < self.bird.rect.centerx:
                pipe.passed = True; self.score += 0.5
                if self.score.is_integer(): self.score_sound.play()

    def _draw_score(self):
        # <<< SỬA ĐỔI: Không vẽ điểm khi đang quiz hoặc có hiệu ứng
        if self.game_state in ['playing', 'game_over']:
            score_surface = self.game_font.render(str(int(self.score)), True, WHITE)
            score_rect = score_surface.get_rect(center=(WIDTH // 2, 100))
            self.screen.blit(score_surface, score_rect)

    def _draw_game_over(self):
        # ... (Không thay đổi)
        texts = [
            (f'Score: {int(self.score)}', HEIGHT // 2 - 50),
            (f'High Score: {self.top_score_entry["name"]} - {self.top_score_entry["score"]}' if self.top_score_entry else 'High Score: N/A', HEIGHT // 2 + 50),
            ('Press SPACE to restart', HEIGHT // 2 + 150)
        ]
        for text, y_pos in texts:
            surface = self.game_font.render(text, True, WHITE)
            rect = surface.get_rect(center=(WIDTH // 2, y_pos)); self.screen.blit(surface, rect)

    def _reset_game(self):
        # ... (Không thay đổi)
        self._save_score_if_any()
        self.leaderboard = load_leaderboard(); self.top_score_entry = self.leaderboard[0] if self.leaderboard else None
        self.game_state = 'playing'; self.pipe_list.clear(); self.death_particles.clear(); self.bird.reset(); self.score = 0
        self.bonk_stick = None; self.bonk_hit_time = None; self.last_quiz_score = -1; self.current_quiz = None; self.screen_shake = 0
        self.is_fist_closed = False; self.answered_this_quiz = False
        pygame.time.set_timer(self.spawnpipe_event, PIPE_SPACING)

    def _save_score_if_any(self):
        # ... (Không thay đổi)
        if self.score > 0: save_to_leaderboard(self.player_name, int(self.score))

    def _draw_webcam(self):
        # ... (Không thay đổi)
        frame = self.latest_cam_frame
        if frame is None: return
        webcam_width, webcam_height = 400, 450; frame = cv2.resize(frame, (webcam_width, webcam_height))
        frame_surface = pygame.surfarray.make_surface(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).swapaxes(0,1))
        cam_x, cam_y = WIDTH - webcam_width - 10, HEIGHT - webcam_height - 10
        self.screen.blit(frame_surface, (cam_x, cam_y))
        pygame.draw.rect(self.screen, WHITE, (cam_x, cam_y, webcam_width, webcam_height), 3)
        if self.game_state == 'quiz':
            guide_font = pygame.font.Font('font/VT323-Regular.ttf', 30)
            cam_rect = pygame.Rect(cam_x, cam_y, webcam_width, webcam_height)
            guides = {'A':(cam_rect.left+10, cam_rect.top+10),'B':(cam_rect.right-30,cam_rect.top+10),
                      'C':(cam_rect.left+10, cam_rect.bottom-40),'D':(cam_rect.right-30, cam_rect.bottom-40)}
            for text, pos in guides.items(): self.screen.blit(guide_font.render(text, True, (0,255,0)), pos)

    def _start_quiz(self):
        # ... (Không thay đổi)
        self.game_state = 'quiz'
        self.current_quiz = self.quiz_manager.get_random_question()
        self.quiz_timer_start = pygame.time.get_ticks()
        pygame.time.set_timer(self.spawnpipe_event, 0)
        self.answered_this_quiz = False
        self.pipe_list = [pipe for pipe in self.pipe_list if pipe.rect.centerx > 500]


    # <<< SỬA ĐỔI: Hàm xử lý câu trả lời >>>
    def _handle_quiz_answer(self, answer_key):
        if self.game_state != 'quiz': return
        is_correct = self.quiz_manager.check_answer(self.current_quiz, answer_key)
        if is_correct:
            self._trigger_correct_answer_effect() # Kích hoạt hiệu ứng
        else:
            self._handle_wrong_answer()


    def _handle_wrong_answer(self):
        # ... (Không thay đổi)
        if not self.bonk_stick:
            self.game_state = 'bonking'; self.current_quiz = None
            self.bonk_stick = BonkStick(self.bonk_stick_img, self.bird.rect)

    def _get_gesture_answer(self):
        # ... (Không thay đổi)
        if self.hand_x_pos is None or self.hand_y_pos is None: return None
        x, y = self.hand_x_pos, self.hand_y_pos
        if y < 0.5: return 'A' if x < 0.5 else 'B'
        else: return 'C' if x < 0.5 else 'D'

    def _draw_quiz_ui(self):
        # ... (Không thay đổi)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); self.screen.blit(overlay, (0, 0))
        question_text = self.current_quiz['question']; wrapped_lines = textwrap.wrap(question_text, width=40); y_pos = 200
        for line in wrapped_lines:
            q_surf = self.quiz_question_font.render(line, True, WHITE); q_rect = q_surf.get_rect(center=(WIDTH//2, y_pos))
            self.screen.blit(q_surf, q_rect); y_pos += 50
        y_pos = 450
        for option in self.current_quiz['options']:
            opt_surf = self.quiz_font.render(option, True, WHITE); opt_rect = opt_surf.get_rect(center=(WIDTH//2, y_pos))
            self.screen.blit(opt_surf, opt_rect); y_pos += 80
        time_left = QUIZ_TIME_LIMIT - (pygame.time.get_ticks() - self.quiz_timer_start) / 1000
        timer_surf = self.quiz_font.render(f"Time: {max(0, int(time_left))}", True, YELLOW_BRIGHT)
        timer_rect = timer_surf.get_rect(center=(WIDTH//2, HEIGHT - 150)); self.screen.blit(timer_surf, timer_rect)
        if self.control_mode == 'gesture':
            inst_surf = self.quiz_font.render("Mở tay để di chuyển, Nắm tay để chọn đáp án", True, YELLOW_BRIGHT)
            inst_rect = inst_surf.get_rect(center=(WIDTH//2, HEIGHT - 80)); self.screen.blit(inst_surf, inst_rect)


# =================================================================================
# --- MENU & MAIN LOOP ---
# =================================================================================
# ... (Không thay đổi)
def show_menu(screen):
    title_font = pygame.font.Font('font/TMC-Ong Do.TTF', 100)
    menu_font = pygame.font.Font('font/04B_19.TTF', 40)
    label_font = pygame.font.Font('font/04B_19.TTF', 30); clock = pygame.time.Clock(); player_name, input_active = '', False
    input_rect = pygame.Rect(WIDTH // 2 - 200, 480, 400, 50)
    logo_img = pygame.transform.rotozoom(pygame.image.load('Assets/menu_pic.png').convert_alpha(), 0, 0.35)
    logo_rect = logo_img.get_rect(center=(WIDTH // 2, 280)); angle, angle_speed, bob_range = 0, 2, 10
    text_flash_timer, show_selected_text = 0, True; particles = [Particle(WIDTH, HEIGHT) for _ in range(150)]
    menu_options = ["Keyboard (SPACE)", "Gesture (webcam)", "Leaderboard"]
    selected_option = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return 'QUIT', None
            if event.type == pygame.MOUSEBUTTONDOWN: input_active = input_rect.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN: input_active = False
                    elif event.key == pygame.K_BACKSPACE: player_name = player_name[:-1]
                    elif len(player_name) < 12: player_name += event.unicode
                else:
                    if event.key in [pygame.K_UP, pygame.K_w]: selected_option = (selected_option - 1) % len(menu_options)
                    if event.key in [pygame.K_DOWN, pygame.K_s]: selected_option = (selected_option + 1) % len(menu_options)
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        final_name = player_name if player_name.strip() else "Guest"
                        if selected_option == 0: return "keyboard", final_name
                        if selected_option == 1: return "gesture", final_name
                        if selected_option == 2: return "LEADERBOARD", final_name
        
        angle += angle_speed; logo_rect.centery = 280 + int(bob_range * pygame.math.Vector2(0, 1).rotate(angle).y)
        text_flash_timer += clock.get_time()
        if text_flash_timer > 400: show_selected_text, text_flash_timer = not show_selected_text, 0
        
        screen.fill((10, 20, 30))
        for p in particles: p.move_and_draw(screen)
        
        title_surf = title_font.render("FLAPPY WUKONG", True, WHITE); title_rect = title_surf.get_rect(center=(WIDTH // 2, 120))
        screen.blit(title_surf, title_rect); screen.blit(logo_img, logo_rect)
        label_surf = label_font.render("Enter Name:", True, WHITE); screen.blit(label_surf, (input_rect.x, input_rect.y - 40))
        pygame.draw.rect(screen, COLOR_ACTIVE if input_active else COLOR_INACTIVE, input_rect, 2)
        name_surface = menu_font.render(player_name, True, WHITE); screen.blit(name_surface, (input_rect.x + 10, input_rect.y + 5))
        
        y_start = 600
        for i, txt in enumerate(menu_options):
            is_selected = (i == selected_option)
            color = YELLOW_BRIGHT if is_selected and not input_active else WHITE
            if is_selected and not show_selected_text and not input_active: continue
            text_surf = menu_font.render(txt, True, color)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, y_start + i * 100))
            screen.blit(text_surf, text_rect)
            
        pygame.display.update(); clock.tick(FPS)

def show_leaderboard(screen):
    title_font = pygame.font.Font('font/TMC-Ong Do.TTF', 80)
    score_font = pygame.font.Font('font/04B_19.TTF', 40)
    leaderboard_active = True; clock = pygame.time.Clock(); scores = load_leaderboard()
    while leaderboard_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: leaderboard_active = False
        screen.fill((10, 20, 30))
        title_surf = title_font.render("LEADERBOARD", True, YELLOW_BRIGHT); title_rect = title_surf.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title_surf, title_rect)
        if not scores:
            no_scores_surf = score_font.render("No scores yet!", True, WHITE)
            no_scores_rect = no_scores_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2)); screen.blit(no_scores_surf, no_scores_rect)
        else:
            for i, entry in enumerate(scores):
                score_text = f"{i + 1}.   {entry['name']} - {entry['score']}"
                score_surf = score_font.render(score_text, True, WHITE); score_rect = score_surf.get_rect(center=(WIDTH // 2, 250 + i * 60))
                screen.blit(score_surf, score_rect)
        return_surf = score_font.render("Press ESC to return to menu", True, (200, 200, 200))
        return_rect = return_surf.get_rect(center=(WIDTH // 2, HEIGHT - 100)); screen.blit(return_surf, return_rect)
        pygame.display.update(); clock.tick(FPS)

def main():
    pygame.init(); pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Wukong - AI Quiz Edition")
    while True:
        mode, player_name = show_menu(screen)
        if mode == 'QUIT': break
        if mode == 'LEADERBOARD': show_leaderboard(screen); continue
        game = Game(mode, player_name)
        result = game.run()
        if result == 'QUIT': break
    pygame.quit(); sys.exit()

if __name__ == '__main__':
    main() 