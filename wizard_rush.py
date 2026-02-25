import math
import random
import sys

import pygame


WIDTH, HEIGHT = 1280, 720
FPS = 60
GROUND_Y = HEIGHT - 170
PLAYER_X = 220

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_SETTINGS = "settings"
STATE_GAME_OVER = "game_over"


def clamp(value, low, high):
    return max(low, min(high, value))


class Button:
    def __init__(self, x, y, w, h, label, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.action = action

    def draw(self, surface, font, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        base = (42, 56, 104) if not hovered else (70, 92, 170)
        shadow = self.rect.move(0, 6)
        pygame.draw.rect(surface, (8, 10, 24), shadow, border_radius=16)
        pygame.draw.rect(surface, base, self.rect, border_radius=16)
        shine = pygame.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.w - 8, 14)
        pygame.draw.rect(surface, (185, 210, 255), shine, border_radius=8)
        pygame.draw.rect(surface, (150, 180, 255), self.rect, 2, border_radius=16)
        text = font.render(self.label, True, (240, 246, 255))
        surface.blit(text, text.get_rect(center=self.rect.center))

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()
            return True
        return False


def draw_vertical_gradient(surface, top_color, bottom_color):
    for y in range(surface.get_height()):
        t = y / max(1, surface.get_height() - 1)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))


def draw_soft_glow(surface, center, radius, color, alpha):
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(5, 0, -1):
        r = int(radius * i / 5)
        a = int(alpha * i / 5 * 0.35)
        pygame.draw.circle(glow, (*color, a), (radius, radius), r)
    surface.blit(glow, (center[0] - radius, center[1] - radius))


def draw_wizard(surface, x, y, frame, jumping):
    bob = math.sin(frame * 0.25) * 4 if not jumping else -4
    px = int(x)
    py = int(y + bob)

    # shadow
    shadow_w = 74 if not jumping else 56
    pygame.draw.ellipse(surface, (0, 0, 0, 100), (px - shadow_w // 2, GROUND_Y + 56, shadow_w, 18))

    # robe
    robe = pygame.Rect(px - 35, py - 70, 70, 95)
    pygame.draw.rect(surface, (28, 37, 88), robe, border_radius=20)
    pygame.draw.rect(surface, (16, 22, 52), (px - 16, py - 70, 32, 88), border_radius=14)

    # scarf
    pygame.draw.rect(surface, (158, 38, 42), (px - 22, py - 42, 44, 12), border_radius=4)
    pygame.draw.rect(surface, (232, 198, 84), (px - 22, py - 37, 44, 4))

    # head + hair
    pygame.draw.circle(surface, (248, 220, 186), (px, py - 84), 24)
    pygame.draw.ellipse(surface, (38, 24, 18), (px - 24, py - 108, 48, 18))
    scar = [(px - 2, py - 97), (px + 3, py - 102), (px + 1, py - 94), (px + 6, py - 99)]
    pygame.draw.lines(surface, (214, 88, 74), False, scar, 2)

    # glasses
    pygame.draw.circle(surface, (10, 10, 10), (px - 10, py - 86), 6, 2)
    pygame.draw.circle(surface, (10, 10, 10), (px + 10, py - 86), 6, 2)
    pygame.draw.line(surface, (10, 10, 10), (px - 4, py - 86), (px + 4, py - 86), 2)

    # hat
    pygame.draw.rect(surface, (25, 25, 30), (px - 30, py - 120, 60, 8), border_radius=4)
    hat_points = [(px, py - 162), (px - 20, py - 120), (px + 20, py - 120)]
    pygame.draw.polygon(surface, (20, 20, 26), hat_points)

    # arms
    swing = math.sin(frame * 0.6) * 10 if not jumping else 18
    pygame.draw.rect(surface, (28, 37, 88), (px - 48, py - 58 + int(swing * 0.15), 14, 56), border_radius=8)
    pygame.draw.rect(surface, (28, 37, 88), (px + 34, py - 58 - int(swing * 0.15), 14, 56), border_radius=8)

    # wand
    pygame.draw.rect(surface, (96, 58, 30), (px + 40, py - 10, 5, 42), border_radius=3)
    glow = 6 + int((math.sin(frame * 0.8) + 1) * 3)
    pygame.draw.circle(surface, (130, 246, 255), (px + 42, py + 34), glow)

    # collision rect
    return pygame.Rect(px - 28, py - 106, 56, 132)


def main():
    pygame.init()
    pygame.display.set_caption("Wizard Rush 2D - Pygame")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("georgia", 72, bold=True)
    h1_font = pygame.font.SysFont("georgia", 42, bold=True)
    body_font = pygame.font.SysFont("segoeui", 28)
    small_font = pygame.font.SysFont("segoeui", 22)

    stars = [(random.randint(0, WIDTH), random.randint(20, 360), random.randint(1, 3)) for _ in range(80)]
    hills_back = [{"x": i * 180, "h": random.randint(120, 220)} for i in range(10)]
    hills_mid = [{"x": i * 170, "h": random.randint(170, 280)} for i in range(10)]
    castle_spires = [{"x": i * 240 + 100, "w": random.randint(36, 66), "h": random.randint(170, 310)} for i in range(7)]
    clouds_far = [{"x": i * 260, "y": random.randint(85, 200), "w": random.randint(150, 260)} for i in range(8)]
    fog_bands = [{"x": i * 300, "y": random.randint(400, 560), "w": random.randint(220, 340)} for i in range(7)]
    lane_marks = [i * 90 for i in range(20)]
    runes = [i * 150 for i in range(14)]

    state = STATE_MENU
    prev_state = STATE_MENU
    difficulty = "Normal"
    fx_level = "High"

    speed_profile = {
        "Easy": (360, 1.25),
        "Normal": (470, 1.0),
        "Hard": (580, 0.82),
    }
    speed, spawn_interval = speed_profile[difficulty]

    player_y = GROUND_Y
    player_vel_y = 0.0
    gravity = 1500.0
    jump_force = 690.0
    long_jump_window = 0.28
    long_jump_active = 0.0
    last_space_time = -10.0
    score = 0.0
    best = 0
    frame = 0.0
    spawn_timer = 0.0
    obstacles = []
    particles = []
    shake_time = 0.0
    shake_power = 0.0
    chroma_time = 0.0
    flash_time = 0.0

    def reset_run():
        nonlocal player_y, player_vel_y, score, spawn_timer, frame, obstacles, particles, long_jump_active, last_space_time
        nonlocal shake_time, shake_power, chroma_time, flash_time
        player_y = GROUND_Y
        player_vel_y = 0.0
        score = 0.0
        spawn_timer = 0.0
        frame = 0.0
        long_jump_active = 0.0
        last_space_time = -10.0
        shake_time = 0.0
        shake_power = 0.0
        chroma_time = 0.0
        flash_time = 0.0
        obstacles.clear()
        particles.clear()

    def start_game():
        nonlocal state
        reset_run()
        state = STATE_PLAYING

    def go_menu():
        nonlocal state
        reset_run()
        state = STATE_MENU

    def open_settings(from_state):
        nonlocal state, prev_state
        prev_state = from_state
        state = STATE_SETTINGS

    def close_settings():
        nonlocal state
        state = prev_state

    def cycle_difficulty():
        nonlocal difficulty, speed, spawn_interval
        options = ["Easy", "Normal", "Hard"]
        difficulty = options[(options.index(difficulty) + 1) % len(options)]
        speed, spawn_interval = speed_profile[difficulty]

    def cycle_fx():
        nonlocal fx_level
        options = ["Low", "Medium", "High"]
        fx_level = options[(options.index(fx_level) + 1) % len(options)]

    menu_buttons = [
        Button(WIDTH // 2 - 140, 360, 280, 62, "Start Run", start_game),
        Button(WIDTH // 2 - 140, 436, 280, 62, "Settings", lambda: open_settings(STATE_MENU)),
        Button(WIDTH // 2 - 140, 512, 280, 62, "Quit", lambda: sys.exit(0)),
    ]
    pause_buttons = [
        Button(WIDTH // 2 - 140, 360, 280, 62, "Resume", lambda: set_state(STATE_PLAYING)),
        Button(WIDTH // 2 - 140, 436, 280, 62, "Settings", lambda: open_settings(STATE_PAUSED)),
        Button(WIDTH // 2 - 140, 512, 280, 62, "Main Menu", go_menu),
    ]
    game_over_buttons = [
        Button(WIDTH // 2 - 140, 420, 280, 62, "Retry", start_game),
        Button(WIDTH // 2 - 140, 496, 280, 62, "Main Menu", go_menu),
    ]
    settings_buttons = [
        Button(WIDTH // 2 - 170, 350, 340, 62, "", cycle_difficulty),
        Button(WIDTH // 2 - 170, 430, 340, 62, "", cycle_fx),
        Button(WIDTH // 2 - 170, 520, 340, 62, "Back", close_settings),
    ]

    def set_state(new_state):
        nonlocal state
        state = new_state

    def spawn_particle(x, y, vx, vy, life, size, color, gravity=430.0, drag=0.0):
        particles.append(
            {
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "life": life,
                "max_life": life,
                "size": size,
                "color": color,
                "gravity": gravity,
                "drag": drag,
            }
        )

    def emit_dust(x, y, count, tint=(180, 205, 230)):
        for _ in range(count):
            spawn_particle(
                x + random.uniform(-16, 16),
                y + random.uniform(-4, 3),
                random.uniform(-120, 95),
                random.uniform(-140, -40),
                random.uniform(0.2, 0.38),
                random.randint(2, 5),
                tint,
                gravity=340,
                drag=1.6,
            )

    def emit_sparks(x, y, count, tint=(130, 245, 255)):
        for _ in range(count):
            spawn_particle(
                x + random.uniform(-10, 10),
                y + random.uniform(-10, 10),
                random.uniform(-170, 170),
                random.uniform(-240, -50),
                random.uniform(0.22, 0.5),
                random.randint(2, 6),
                tint,
                gravity=420,
                drag=0.45,
            )

    def emit_hit_burst(x, y, count, tint):
        for _ in range(count):
            spawn_particle(
                x,
                y,
                random.uniform(-260, 260),
                random.uniform(-320, 110),
                random.uniform(0.3, 0.7),
                random.randint(3, 8),
                tint,
                gravity=520,
                drag=0.25,
            )

    def trigger_impact_vfx(x, y, tint=(255, 140, 140), power=1.0):
        nonlocal shake_time, shake_power, chroma_time, flash_time
        shake_time = max(shake_time, 0.22 * power)
        shake_power = max(shake_power, 11.0 * power)
        chroma_time = max(chroma_time, 0.16 * power)
        flash_time = max(flash_time, 0.1 * power)
        emit_hit_burst(x, y, int(16 * power), tint)

    def spawn_obstacle():
        kind = "wall" if random.random() < 0.28 else "hurdle"
        if kind == "wall":
            h = random.randint(230, 300)
            w = random.randint(74, 96)
            y = GROUND_Y + 60 - h
        else:
            h = random.randint(70, 165)
            w = random.randint(45, 75)
            y = GROUND_Y + 60 - h

        rect = pygame.Rect(WIDTH + 30, y, w, h)
        obstacles.append({"rect": rect, "kind": kind, "phase": random.uniform(0, 6.28)})

    def cast_spell():
        if not obstacles:
            return
        target = None
        for o in obstacles:
            if o["rect"].centerx > PLAYER_X:
                target = o
                break
        if not target:
            return
        wx = PLAYER_X + 42
        wy = int(player_y) - 18
        tx = target["rect"].centerx
        ty = target["rect"].centery
        for i in range(10):
            t = i / 9
            sx = wx + (tx - wx) * t + random.uniform(-3, 3)
            sy = wy + (ty - wy) * t + random.uniform(-3, 3)
            emit_sparks(sx, sy, 1, (138, 246, 255) if target["kind"] == "hurdle" else (192, 152, 255))
        emit_hit_burst(tx, ty, 12, (130, 245, 255) if target["kind"] == "hurdle" else (198, 160, 255))
        if target["kind"] == "wall":
            trigger_impact_vfx(tx, ty, (205, 170, 255), 0.8)
        obstacles.remove(target)

    while True:
        dt = clock.tick(FPS) / 1000.0
        frame += 1
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == STATE_PLAYING:
                        set_state(STATE_PAUSED)
                    elif state == STATE_PAUSED:
                        set_state(STATE_PLAYING)
                    elif state == STATE_SETTINGS:
                        close_settings()
                elif event.key == pygame.K_RETURN and state == STATE_MENU:
                    start_game()
                elif event.key == pygame.K_r and state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER):
                    start_game()
                elif event.key in (pygame.K_SPACE, pygame.K_UP):
                    if state == STATE_MENU:
                        start_game()
                    elif state == STATE_PLAYING:
                        now = pygame.time.get_ticks() / 1000.0
                        grounded = player_y >= GROUND_Y - 0.1
                        is_double_tap = (now - last_space_time) <= long_jump_window

                        if grounded:
                            if is_double_tap:
                                player_vel_y = -(jump_force * 1.2)
                                long_jump_active = 0.24
                            else:
                                player_vel_y = -jump_force
                                long_jump_active = 0.0

                            n = 4 if fx_level == "Low" else 7 if fx_level == "Medium" else 10
                            emit_dust(PLAYER_X, GROUND_Y + 64, n, (215, 232, 255) if not is_double_tap else (250, 214, 120))
                            if is_double_tap:
                                trigger_impact_vfx(PLAYER_X, GROUND_Y + 52, (250, 214, 120), 0.55)
                        elif is_double_tap and long_jump_active <= 0.0:
                            player_vel_y = min(player_vel_y, -(jump_force * 0.55))
                            long_jump_active = 0.2
                            emit_sparks(PLAYER_X + 24, player_y + 14, 10, (246, 225, 128))

                        last_space_time = now
                elif event.key == pygame.K_e and state == STATE_PLAYING:
                    cast_spell()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == STATE_MENU:
                    for b in menu_buttons:
                        if b.click(event.pos):
                            break
                elif state == STATE_PAUSED:
                    for b in pause_buttons:
                        if b.click(event.pos):
                            break
                elif state == STATE_GAME_OVER:
                    for b in game_over_buttons:
                        if b.click(event.pos):
                            break
                elif state == STATE_SETTINGS:
                    for b in settings_buttons:
                        if b.click(event.pos):
                            break

        # Update
        if state == STATE_PLAYING:
            if shake_time > 0.0:
                shake_time = max(0.0, shake_time - dt)
            if chroma_time > 0.0:
                chroma_time = max(0.0, chroma_time - dt)
            if flash_time > 0.0:
                flash_time = max(0.0, flash_time - dt)

            effective_gravity = gravity * (0.58 if long_jump_active > 0.0 else 1.0)
            if long_jump_active > 0.0:
                long_jump_active = max(0.0, long_jump_active - dt)
            player_vel_y += effective_gravity * dt
            player_y += player_vel_y * dt
            if player_y > GROUND_Y:
                player_y = GROUND_Y
                player_vel_y = 0.0

            score += dt * (11 + speed * 0.035)
            spawn_timer += dt
            if spawn_timer >= spawn_interval:
                spawn_timer = 0.0
                spawn_obstacle()

            # world scroll
            for h in hills_back:
                h["x"] -= speed * 0.18 * dt
                if h["x"] < -220:
                    h["x"] += 180 * len(hills_back)
            for h in hills_mid:
                h["x"] -= speed * 0.34 * dt
                if h["x"] < -220:
                    h["x"] += 170 * len(hills_mid)
            for s in castle_spires:
                s["x"] -= speed * 0.28 * dt
                if s["x"] < -140:
                    s["x"] += 240 * len(castle_spires)
            for c in clouds_far:
                c["x"] -= speed * 0.09 * dt
                if c["x"] < -300:
                    c["x"] += 260 * len(clouds_far)
            for f in fog_bands:
                f["x"] -= speed * 0.24 * dt
                if f["x"] < -360:
                    f["x"] += 300 * len(fog_bands)
            for i, x in enumerate(lane_marks):
                lane_marks[i] = x - speed * 0.95 * dt
                if lane_marks[i] < -120:
                    lane_marks[i] += 1800
            for i, x in enumerate(runes):
                runes[i] = x - speed * 0.72 * dt
                if runes[i] < -170:
                    runes[i] += 2200

            player_hitbox = pygame.Rect(PLAYER_X - 28, int(player_y) - 106, 56, 132)
            for o in list(obstacles):
                rect = o["rect"]
                rect.x -= int(speed * dt)
                o["phase"] += dt * 3.2
                if rect.right < -40:
                    obstacles.remove(o)
                    continue
                if player_hitbox.colliderect(rect):
                    best = max(best, int(score))
                    state = STATE_GAME_OVER
                    tint = (255, 130, 130) if o["kind"] == "hurdle" else (196, 138, 255)
                    trigger_impact_vfx(player_hitbox.centerx, player_hitbox.centery, tint, 1.3)
                    break

            if fx_level != "Low" and random.random() < (0.11 if fx_level == "Medium" else 0.19):
                emit_sparks(PLAYER_X + 42, int(player_y) - 26, 1, (130, 245, 255))
            if player_y >= GROUND_Y - 0.1 and random.random() < (0.08 if fx_level == "Low" else 0.14):
                emit_dust(PLAYER_X - 8, GROUND_Y + 64, 1, (164, 184, 206))

        for p in list(particles):
            if "max_life" not in p:
                p["max_life"] = p["life"]
                p["gravity"] = p.get("gravity", 430.0)
                p["drag"] = p.get("drag", 0.0)
            p["life"] -= dt
            p["vx"] *= max(0.0, 1.0 - p.get("drag", 0.0) * dt)
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += p.get("gravity", 430.0) * dt
            if p["life"] <= 0:
                particles.remove(p)

        # Draw
        draw_vertical_gradient(screen, (11, 16, 44), (42, 28, 66))
        draw_soft_glow(screen, (1080, 105), 124, (140, 195, 255), 120)
        pygame.draw.circle(screen, (232, 245, 255), (1080, 105), 56)
        pygame.draw.circle(screen, (138, 185, 255), (1080, 105), 84, 2)
        pygame.draw.rect(screen, (255, 136, 92), (0, 250, WIDTH, 180), border_radius=0)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((12, 16, 38, 168))
        screen.blit(overlay, (0, 0))

        for sx, sy, sr in stars:
            alpha = 120 + int((math.sin((frame + sx) * 0.02) + 1) * 60)
            pygame.draw.circle(screen, (220, 235, 255, alpha), (sx, sy), sr)

        for c in clouds_far:
            cx, cy, w = int(c["x"]), c["y"], c["w"]
            pygame.draw.ellipse(screen, (120, 132, 178), (cx, cy, w, 42))
            pygame.draw.ellipse(screen, (106, 120, 164), (cx + 38, cy - 18, w - 52, 40))

        for h in hills_back:
            pygame.draw.rect(screen, (44, 52, 90), (h["x"], HEIGHT - 270 - h["h"], 220, h["h"]), border_radius=24)
        for h in hills_mid:
            pygame.draw.rect(screen, (62, 66, 102), (h["x"], HEIGHT - 235 - h["h"], 220, h["h"]), border_radius=22)
        for s in castle_spires:
            sx = int(s["x"])
            spire_body = pygame.Rect(sx, HEIGHT - 238 - s["h"], s["w"], s["h"])
            pygame.draw.rect(screen, (48, 44, 70), spire_body, border_radius=6)
            roof = [(sx + s["w"] // 2, spire_body.y - 28), (sx - 8, spire_body.y + 4), (sx + s["w"] + 8, spire_body.y + 4)]
            pygame.draw.polygon(screen, (34, 30, 52), roof)
            window_y = spire_body.y + 28
            while window_y < spire_body.bottom - 18:
                pygame.draw.rect(screen, (232, 194, 122), (sx + s["w"] // 2 - 3, window_y, 6, 10), border_radius=2)
                window_y += 26

        for f in fog_bands:
            fx, fy, fw = int(f["x"]), f["y"], f["w"]
            pygame.draw.ellipse(screen, (98, 128, 170), (fx, fy, fw, 80))

        pygame.draw.rect(screen, (34, 36, 56), (0, GROUND_Y + 52, WIDTH, 180))
        pygame.draw.rect(screen, (82, 174, 235), (0, GROUND_Y + 48, WIDTH, 6))
        pygame.draw.rect(screen, (44, 54, 78), (0, GROUND_Y + 124, WIDTH, 98))
        for x in lane_marks:
            pygame.draw.rect(screen, (190, 220, 255), (int(x), GROUND_Y + 88, 54, 8), border_radius=4)
        for x in runes:
            pygame.draw.polygon(
                screen,
                (120, 220, 255),
                [(int(x), GROUND_Y + 56), (int(x + 10), GROUND_Y + 46), (int(x + 20), GROUND_Y + 56), (int(x + 10), GROUND_Y + 66)],
            )

        for o in obstacles:
            rect = o["rect"]
            if o["kind"] == "wall":
                aura = (148, 110, 246)
                body = (76, 46, 122)
                trim = (198, 164, 255)
                symbol = (238, 220, 255)
            else:
                aura = (220, 80, 120)
                body = (118, 42, 62)
                trim = (190, 80, 110)
                symbol = (245, 120, 150)

            draw_soft_glow(screen, rect.center, max(rect.width, rect.height), aura, 30)
            pygame.draw.rect(screen, body, rect, border_radius=8)
            pygame.draw.rect(screen, tuple(min(255, c + 30) for c in body), (rect.x + 6, rect.y + 8, max(4, rect.w - 12), max(4, rect.h - 12)), border_radius=6)
            pygame.draw.rect(screen, trim, rect, 2, border_radius=8)
            pulse_r = max(5, rect.w // 8) + int((math.sin(o["phase"]) + 1.0) * 2)
            pygame.draw.circle(screen, symbol, rect.center, pulse_r, 1)

        draw_wizard(screen, PLAYER_X, player_y, frame, player_y < GROUND_Y - 0.1)

        for p in particles:
            life_ratio = clamp(p["life"] / max(0.001, p.get("max_life", p["life"])), 0.0, 1.0)
            r = clamp(int(p["size"] * (0.4 + life_ratio * 1.5)), 1, 14)
            alpha = int(40 + life_ratio * 215)
            pygame.draw.circle(screen, (*p["color"], alpha), (int(p["x"]), int(p["y"])), r)

        # HUD
        if state == STATE_PLAYING:
            draw_soft_glow(screen, (160, 74), 180, (95, 170, 255), 35)
            pygame.draw.rect(screen, (10, 14, 36), (24, 20, 270, 110), border_radius=16)
            pygame.draw.rect(screen, (128, 170, 255), (24, 20, 270, 110), 2, border_radius=16)
            screen.blit(body_font.render(f"SCORE  {int(score)}", True, (210, 240, 255)), (42, 38))
            screen.blit(small_font.render(f"BEST   {best}", True, (190, 206, 238)), (42, 75))
            screen.blit(small_font.render("SPACE x2 long jump  E breaks cursed walls  ESC pause", True, (140, 220, 255)), (36, HEIGHT - 42))

        def draw_center_panel(title, subtitle):
            panel = pygame.Rect(WIDTH // 2 - 300, 170, 600, 390)
            draw_soft_glow(screen, panel.center, 360, (84, 132, 255), 26)
            pygame.draw.rect(screen, (8, 12, 28), panel, border_radius=22)
            pygame.draw.rect(screen, (145, 180, 255), panel, 2, border_radius=22)
            pygame.draw.rect(screen, (176, 208, 255), (panel.x + 12, panel.y + 14, panel.w - 24, 6), border_radius=3)
            screen.blit(h1_font.render(title, True, (210, 226, 255)), (panel.centerx - h1_font.size(title)[0] // 2, panel.y + 30))
            if subtitle:
                screen.blit(small_font.render(subtitle, True, (165, 195, 235)), (panel.centerx - small_font.size(subtitle)[0] // 2, panel.y + 90))

        if state == STATE_MENU:
            draw_center_panel("WIZARD RUSH", "Press ENTER/SPACE or click Start")
            for b in menu_buttons:
                b.draw(screen, body_font, mouse_pos)

        elif state == STATE_PAUSED:
            draw_center_panel("PAUSED", "Press ESC to resume quickly")
            for b in pause_buttons:
                b.draw(screen, body_font, mouse_pos)

        elif state == STATE_SETTINGS:
            settings_buttons[0].label = f"Difficulty: {difficulty}"
            settings_buttons[1].label = f"Effects: {fx_level}"
            draw_center_panel("SETTINGS", "Tune challenge and visuals")
            for b in settings_buttons:
                b.draw(screen, body_font, mouse_pos)

        elif state == STATE_GAME_OVER:
            draw_center_panel("GAME OVER", f"Final Score: {int(score)}")
            for b in game_over_buttons:
                b.draw(screen, body_font, mouse_pos)

        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (0, 0, 0, 58), (0, 0, WIDTH, HEIGHT), width=110, border_radius=10)
        screen.blit(vignette, (0, 0))

        frame_img = screen.copy()
        screen.fill((0, 0, 0))

        shake_x = 0
        shake_y = 0
        if shake_time > 0.0:
            decay = shake_time / 0.22
            amount = shake_power * clamp(decay, 0.0, 1.0)
            shake_x = int(random.uniform(-amount, amount))
            shake_y = int(random.uniform(-amount * 0.7, amount * 0.7))
            shake_power = max(0.0, shake_power * 0.92)

        screen.blit(frame_img, (shake_x, shake_y))

        if chroma_time > 0.0:
            strength = clamp(chroma_time / 0.16, 0.0, 1.0)
            offset = int(2 + strength * 4)
            red_pass = frame_img.copy()
            cyan_pass = frame_img.copy()
            red_pass.fill((255, 90, 90, 255), special_flags=pygame.BLEND_RGBA_MULT)
            cyan_pass.fill((110, 235, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
            red_pass.set_alpha(int(65 * strength))
            cyan_pass.set_alpha(int(65 * strength))
            screen.blit(red_pass, (shake_x + offset, shake_y))
            screen.blit(cyan_pass, (shake_x - offset, shake_y))

        if flash_time > 0.0:
            white = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            white.fill((240, 245, 255, int(130 * clamp(flash_time / 0.1, 0.0, 1.0))))
            screen.blit(white, (0, 0))

        pygame.display.flip()


if __name__ == "__main__":
    main()
