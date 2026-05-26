import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stackable Multiplier + Autoclicker")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)

score = 0
multiplier = 1

# center circular 
button_pos = (WIDTH // 2, HEIGHT // 2)
button_radius = 60

# multiplier upgrade
right_btn_w, right_btn_h = 200, 70
right_btn_x = WIDTH - right_btn_w - 20
right_btn_y = HEIGHT // 2 - right_btn_h // 2
right_btn_rect = pygame.Rect(right_btn_x, right_btn_y, right_btn_w, right_btn_h)

# multiplier upgrade cost settings
base_cost_mult = 20
growth_rate_mult = 1.6
purchased_mult = 0
mult_cost = math.ceil(base_cost_mult * (growth_rate_mult ** purchased_mult))

# autoclicker settings
autoc_btn_w, autoc_btn_h = 220, 70
autoc_btn_x = WIDTH - autoc_btn_w - 20
autoc_btn_y = HEIGHT - 100
autoc_btn_rect = pygame.Rect(autoc_btn_x, autoc_btn_y, autoc_btn_w, autoc_btn_h)

# autoclicker: first buy gives +1/s, then upgrade gives +1/s stacking
autoclicker_level = 0
score_per_sec = 0
base_cost_autoclicker = 30
growth_rate_autoclicker = 1.5
autoc_cost = math.ceil(base_cost_autoclicker * (growth_rate_autoclicker ** autoclicker_level))
autoclicker_active = False

# colors
bg = (25, 28, 40)
button_color = (70, 170, 255)
button_hover = (100, 200, 255)
rect_color = (60, 180, 90)
rect_hover = (90, 210, 120)
disabled_color = (80, 80, 80)
text_color = (255, 255, 255)

running = True
last_time = pygame.time.get_ticks()
acc = 0.0
while running:
    mouse_pos = pygame.mouse.get_pos()
    hovered_center = (mouse_pos[0] - button_pos[0]) ** 2 + (mouse_pos[1] - button_pos[1]) ** 2 <= button_radius ** 2
    hovered_mult = right_btn_rect.collidepoint(mouse_pos)
    hovered_autoc = autoc_btn_rect.collidepoint(mouse_pos)

    # autoclicker logic: add score per second over time
    if autoclicker_active and score_per_sec > 0:
        now = pygame.time.get_ticks()
        dt = (now - last_time) / 1000.0
        last_time = now
        acc += dt * score_per_sec
        while acc >= 1.0:
            score += 1
            acc -= 1.0
    else:
        last_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hovered_center:
                score += 1 * multiplier

            # multiplier upgrade: +1 per click, stackable
            if hovered_mult:
                if score >= mult_cost:
                    score -= mult_cost
                    purchased_mult += 1
                    multiplier += 1
                    mult_cost = math.ceil(base_cost_mult * (growth_rate_mult ** purchased_mult))

            # autoclicker: first buy gives +1/s, then upgrades give +1/s stacking
            if hovered_autoc:
                if not autoclicker_active:
                    # first buy
                    if score >= autoc_cost:
                        score -= autoc_cost
                        autoclicker_active = True
                        autoclicker_level = 1
                        score_per_sec = 1  # +1 per second
                        autoc_cost = math.ceil(base_cost_autoclicker * (growth_rate_autoclicker ** autoclicker_level))
                else:
                    # upgrade
                    if score >= autoc_cost:
                        score -= autoc_cost
                        autoclicker_level += 1
                        score_per_sec += 1  # stackable: +1/s per upgrade
                        autoc_cost = math.ceil(base_cost_autoclicker * (growth_rate_autoclicker ** autoclicker_level))

    screen.fill(bg)

    score_surface = font.render(f"Score: {score}", True, text_color)
    score_rect = score_surface.get_rect(midtop=(WIDTH // 2, 20))
    screen.blit(score_surface, score_rect)

    mult_surface = small_font.render(f"Multiplier: x{multiplier}", True, text_color)
    mult_rect = mult_surface.get_rect(midtop=(WIDTH // 2, 70))
    screen.blit(mult_surface, mult_rect)

    if autoclicker_active:
        autoc_info = small_font.render(f"Autoclicker: +{score_per_sec}/s (lvl {autoclicker_level})", True, text_color)
    else:
        autoc_info = small_font.render("Autoclicker: not bought", True, text_color)
    autoc_info_rect = autoc_info.get_rect(midtop=(WIDTH // 2, 100))
    screen.blit(autoc_info, autoc_info_rect)

    pygame.draw.circle(screen, button_hover if hovered_center else button_color, button_pos, button_radius)
    label = font.render("Click", True, text_color)
    label_rect = label.get_rect(center=button_pos)
    screen.blit(label, label_rect)

    can_buy_mult = score >= mult_cost
    color_mult = rect_hover if (hovered_mult and can_buy_mult) else (rect_color if can_buy_mult else disabled_color)
    pygame.draw.rect(screen, color_mult, right_btn_rect, border_radius=10)

    mult_text = small_font.render(f"Buy +1 Mult (x{multiplier+1})", True, text_color)
    mult_cost_text = small_font.render(f"-{mult_cost}", True, text_color)
    screen.blit(mult_text, mult_text.get_rect(center=(right_btn_rect.centerx, right_btn_rect.centery - 12)))
    screen.blit(mult_cost_text, mult_cost_text.get_rect(center=(right_btn_rect.centerx, right_btn_rect.centery + 18)))

    # lower-right autoclicker button
    if not autoclicker_active:
        btn_text = "Buy Autoclicker (+1/s)"
    else:
        btn_text = f"Upgrade Autoclicker (lvl {autoclicker_level+1})"

    can_buy_autoc = score >= autoc_cost
    color_autoc = rect_hover if (hovered_autoc and can_buy_autoc) else (rect_color if can_buy_autoc else disabled_color)
    pygame.draw.rect(screen, color_autoc, autoc_btn_rect, border_radius=10)

    autoc_btn_text = small_font.render(btn_text, True, text_color)
    autoc_cost_text = small_font.render(f"-{autoc_cost}", True, text_color)
    screen.blit(autoc_btn_text, autoc_btn_text.get_rect(center=(autoc_btn_rect.centerx, autoc_btn_rect.centery - 12)))
    screen.blit(autoc_cost_text, autoc_cost_text.get_rect(center=(autoc_btn_rect.centerx, autoc_btn_rect.centery + 18)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
