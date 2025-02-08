import sys
import pygame
import cfg
import modules.Levels as Levels

class Button:
    def __init__(self, text, pos, font, color, hover_color, feedback="", sound=None):
        self.x, self.y = pos
        self.font = pygame.font.Font(font, 24)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.feedback = feedback
        self.rect = pygame.Rect(self.x, self.y, 0, 0)
        self.current_color = color
        self.sound = sound
        self.hovered = False

    def show(self, screen):
        text_surface = self.font.render(self.text, True, self.current_color)
        self.rect = pygame.Rect(self.x, self.y, text_surface.get_width(), text_surface.get_height())
        screen.blit(text_surface, (self.x, self.y))

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(x, y):
                return self.feedback

    def update(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            if not self.hovered:
                self.hovered = True
                self.current_color = self.hover_color
                if self.sound:
                    self.sound.play()
        else:
            self.hovered = False
            self.current_color = self.color

def menu(screen):
    pygame.font.init()
    pygame.font.Font(cfg.FONTPATH, 24)

    menu_bg = pygame.image.load(cfg.MENU_BG).convert()
    menu_bg = pygame.transform.scale(menu_bg, (606, 606))

    pygame.mixer.music.load(cfg.MENU_SOUND)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    button_sound = pygame.mixer.Sound(cfg.BUTTON_SOUND)
    button_sound.set_volume(0.02)
    button_play = Button("Play", (250, 200), cfg.FONTPATH, cfg.WHITE, cfg.YELLOW, feedback="start_game", sound=button_sound)
    button_levels = Button("Levels", (250, 250), cfg.FONTPATH, cfg.WHITE, cfg.YELLOW, feedback="select_levels", sound=button_sound)
    button_quit = Button("Quit", (250, 300), cfg.FONTPATH, cfg.WHITE, cfg.YELLOW, feedback="quit_game", sound=button_sound)
    buttons = [button_play, button_levels, button_quit]

    running = True
    while running:
        screen.blit(menu_bg, (0, 0))

        for button in buttons:
            button.update()
            button.show(screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                action = button.click(event)
                if action == "start_game":
                    pygame.mixer.music.stop()
                    startGame(screen, 2)  # Меняем уровень при старте игры на второй уровень
                elif action == "quit_game":
                    pygame.quit()
                    sys.exit()
                elif action == "select_levels":
                    selectLevels(screen)

def selectLevels(screen):
    pygame.font.init()
    pygame.font.Font(cfg.FONTPATH, 24)

    levels_bg = pygame.image.load(cfg.MENU_BG).convert()
    levels_bg = pygame.transform.scale(levels_bg, (606, 606))

    pygame.mixer.music.load(cfg.MENU_SOUND)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    button_sound = pygame.mixer.Sound(cfg.BUTTON_SOUND)
    button_sound.set_volume(0.02)

    button_level2 = Button("Level 2", (250, 200), cfg.FONTPATH, cfg.WHITE, cfg.YELLOW, feedback="start_level1", sound=button_sound)
    button_level3 = Button("Level 3", (250, 250), cfg.FONTPATH, cfg.WHITE, cfg.YELLOW, feedback="start_level3", sound=button_sound)  # Изменил координаты для третьего уровня
    button_back = Button("Back", (250, 300), cfg.FONTPATH, cfg.WHITE, cfg.YELLOW, feedback="back_to_menu", sound=button_sound)

    level_buttons = [button_level2, button_level3, button_back]

    running = True
    while running:
        screen.blit(levels_bg, (0, 0))

        for button in level_buttons:
            button.update()
            button.show(screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in level_buttons:
                action = button.click(event)
                if action == "start_level1":
                    pygame.mixer.music.stop()
                    startGame(screen, 1)  # Уровень 1 теперь запускает первый уровень
                elif action == "start_level3":
                    pygame.mixer.music.stop()
                    startGame(screen, 3)  # Уровень 3 теперь запускает третий уровень
                elif action == "back_to_menu":
                    menu(screen)

def startGame(screen, level_number):
    pygame.font.init()
    font_small = pygame.font.Font(cfg.FONTPATH, 18)
    font_big = pygame.font.Font(cfg.FONTPATH, 24)
    pygame.mixer.music.stop()

    pygame.mixer.music.load(cfg.GAME_SD)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.02)

    eat_sound = pygame.mixer.Sound(cfg.EAT_SD)
    eat_sound.set_volume(0.5)

    level_class = getattr(Levels, f'Level{level_number}')
    level = level_class()
    is_clearance = startLevelGame(level, screen, font_small, eat_sound)

    if level_number == Levels.NUMLEVELS:
        showText(screen, font_big, is_clearance, True)
    else:
        showText(screen, font_big, is_clearance)

def startLevelGame(level, screen, font, eat_sound):
    clock = pygame.time.Clock()
    SCORE = 0
    wall_sprites = level.setupWalls(cfg.SKYBLUE)
    gate_sprites = level.setupGate(cfg.WHITE)
    hero_sprites, ghost_sprites = level.setupPlayers(cfg.HEROPATH,
                                                     [cfg.BlinkyPATH, cfg.ClydePATH, cfg.InkyPATH, cfg.PinkyPATH])
    food_sprites = level.setupFood(cfg.YELLOW, cfg.WHITE)
    is_clearance = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(-1)
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    for hero in hero_sprites:
                        hero.changeSpeed([-1, 0])
                        hero.is_move = True
                elif event.key == pygame.K_RIGHT:
                    for hero in hero_sprites:
                        hero.changeSpeed([1, 0])
                        hero.is_move = True
                elif event.key == pygame.K_UP:
                    for hero in hero_sprites:
                        hero.changeSpeed([0, -1])
                        hero.is_move = True
                elif event.key == pygame.K_DOWN:
                    for hero in hero_sprites:
                        hero.changeSpeed([0, 1])
                        hero.is_move = True
            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT) or (event.key == pygame.K_RIGHT) or (event.key == pygame.K_UP) or (
                        event.key == pygame.K_DOWN):
                    hero.is_move = False

        screen.fill(cfg.BLACK)

        for hero in hero_sprites:
            hero.update(wall_sprites, gate_sprites)

        hero_sprites.draw(screen)

        for hero in hero_sprites:
            food_eaten = pygame.sprite.spritecollide(hero, food_sprites, True)

        if food_eaten:
            eat_sound.play()

        SCORE += len(food_eaten)
        wall_sprites.draw(screen)
        gate_sprites.draw(screen)
        food_sprites.draw(screen)

        for ghost in ghost_sprites:
            if ghost.tracks_loc[1] < ghost.tracks[ghost.tracks_loc[0]][2]:
                ghost.changeSpeed(ghost.tracks[ghost.tracks_loc[0]][0: 2])
                ghost.tracks_loc[1] += 1
            else:
                if ghost.tracks_loc[0] < len(ghost.tracks) - 1:
                    ghost.tracks_loc[0] += 1
                elif ghost.role_name == 'Clyde':
                    ghost.tracks_loc[0] = 2
                else:
                    ghost.tracks_loc[0] = 0

                ghost.changeSpeed(ghost.tracks[ghost.tracks_loc[0]][0: 2])
                ghost.tracks_loc[1] = 0

            if ghost.tracks_loc[1] < ghost.tracks[ghost.tracks_loc[0]][2]:
                ghost.changeSpeed(ghost.tracks[ghost.tracks_loc[0]][0: 2])
            else:
                if ghost.tracks_loc[0] < len(ghost.tracks) - 1:
                    ghost.tracks_loc[0] += 1
                elif ghost.role_name == 'Clyde':
                    ghost.tracks_loc[0] = 2
                else:
                    ghost.tracks_loc[0] = 0

                ghost.changeSpeed(ghost.tracks[ghost.tracks_loc[0]][0: 2])
                ghost.tracks_loc[1] = 0

            ghost.update(wall_sprites, None)

        ghost_sprites.draw(screen)
        score_text = font.render("Score: %s" % SCORE, True, cfg.RED)
        screen.blit(score_text, [10, 10])

        if len(food_sprites) == 0:
            is_clearance = True
            break

        if pygame.sprite.groupcollide(hero_sprites, ghost_sprites, False, False):
            is_clearance = False
            break

        pygame.display.update()
        clock.tick(10)

    return is_clearance

def showText(screen, font, is_clearance, flag=False):
    clock = pygame.time.Clock()
    msg = 'Game Over!' if not is_clearance else 'Congratulations, you won!'
    sound = pygame.mixer.Sound(cfg.LOSE_SOUND) if not is_clearance else pygame.mixer.Sound(cfg.WIN_SOUND)
    sound.set_volume(0.3)
    sound.play()
    positions = [[235, 233], [65, 303], [170, 333]] if not is_clearance else [[145, 233], [65, 303], [170, 333]]

    surface = pygame.Surface((400, 200))
    surface.set_alpha(10)
    surface.fill((128, 128, 128))
    screen.blit(surface, (100, 200))
    texts = [msg, 'Press ENTER to continue or play again.', 'Press ESCAPE to quit.']
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()
                    pygame.quit()

        for idx, (text, position) in enumerate(zip(texts, positions)):
            screen.blit(font.render(text, True, cfg.WHITE), position)

        pygame.display.update()
        clock.tick(10)

def initialize():
    pygame.init()
    icon_image = pygame.image.load(cfg.ICONPATH)
    pygame.display.set_icon(icon_image)
    screen = pygame.display.set_mode([606, 606])
    pygame.display.set_caption('Pacman')
    return screen

if __name__ == '__main__':
    screen = initialize()
    menu(screen)