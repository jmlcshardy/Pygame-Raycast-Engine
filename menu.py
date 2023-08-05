from main import *
from Widgets.label import Label
from Widgets.slider import Slider
from level_editor import map_maker
from guns import Projectile


def menu():
    pygame.display.set_caption("Raycast Engine (Move Mouse)")
    title = Label("Raycast Engine", x=screen_width//2, y=150, font=title_font, center=True)
    while True:
        screen.fill((3, 37, 126))
        render_walls()
        player.ray_angle += .2
        player.rotation -= .2

        title.show(screen)
        player.z = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save()
                quit()

            elif event.type == pygame.MOUSEMOTION:
                pygame.display.set_caption("Raycast Engine")

        if play.button(screen):
            player.rotation = 0
            player.ray_angle = 270
            main()
        if edit.button(screen):
            player.x = 192
            player.y = 192
            map_maker()

        pygame.display.update()


def settings():
    current_screen = pygame.display.get_surface().copy()

    scale = 1.0 / float(5)
    surf_size = current_screen.get_size()

    scale_size = (int(surf_size[0] * scale), int(surf_size[1] * scale))
    background = pygame.transform.smoothscale(current_screen, scale_size)
    background = pygame.transform.smoothscale(background, surf_size)

    menu_button = Button((326, 587, 500, 75), text="Menu", hover_color=(150, 150, 150))
    resume_button = Button((326, 487, 500, 75), text="Resume", hover_color=(150, 150, 150))

    mouse_sens = Slider(20, 101, 100, 900, 8, horizontal=True, show_value=True, circle_color=(100, 100, 255),
                        text="Mouse Sensitivity", min_value=1, radius=10)

    bob_height = Slider(10, 101, 200, 900, 8, horizontal=True, show_value=True, circle_color=(100, 100, 255),
                        text="View bobbing amplifier", min_value=0, radius=10)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(False)
                    return False

        screen.blit(background, (0, 0))

        if menu_button.button(screen):
            save()
            return True

        if resume_button.button(screen):
            pygame.mouse.set_visible(False)
            save()
            return False

        player.mouse_sensitivity = mouse_sens.slide(screen, player.mouse_sensitivity)
        player.bob_height = (bob_height.slide(screen, int(player.bob_height*100))) / 100

        pygame.display.flip()

        save_json = {
            "mouse_sensitivity": player.mouse_sensitivity,
            "view_bob": int(player.bob_height * 100),
            "x": int(player.x),
            "y": int(player.y)
        }

        with open("settings.json", "w") as setting:
            json.dump(save_json, setting, indent=2)
