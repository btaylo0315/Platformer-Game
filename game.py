# Imports
import pygame
import json

# Window settings
GRID_SIZE = 64
WIDTH = 30 * GRID_SIZE
HEIGHT = 17 * GRID_SIZE
TITLE = "Game Title"
FPS = 60


# Create window
pygame.init()
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (0, 150, 255)
GRAY = (175, 175, 175)

#stages
START = 0
PLAYING = 1
LOSE = 2
LEVEL_COMPLETE = 3
WIN = 4

# Load fonts
font_xl = pygame.font.Font('assets/fonts/Dinomouse-Regular.otf', 96)
font_lg = pygame.font.Font('assets/fonts/Dinomouse-Regular.otf', 64)
font_md = pygame.font.Font('assets/fonts/Dinomouse-Regular.otf', 32)
font_sm = pygame.font.Font('assets/fonts/Dinomouse-Regular.otf', 24)
font_xs = pygame.font.Font(None, 14)

# Load images
hero_idle_imgs_rt = [pygame.image.load('assets/images/characters/player_idle.png').convert_alpha()]

hero_walk_imgs_rt = [pygame.image.load('assets/images/characters/player_walk1.png').convert_alpha(),
                     pygame.image.load('assets/images/characters/player_walk2.png').convert_alpha()]

hero_jump_imgs_rt = [pygame.image.load('assets/images/characters/player_jump.png').convert_alpha()]

hero_idle_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_idle_imgs_rt]
hero_walk_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_walk_imgs_rt]
hero_jump_imgs_lt = [pygame.transform.flip(img, True, False) for img in hero_jump_imgs_rt]





grass_dirt_img = pygame.image.load('assets/images/tiles/grass_dirt.png').convert_alpha()
block_img = pygame.image.load('assets/images/tiles/block.png').convert_alpha()
platform_img = pygame.image.load('assets/images/tiles/stone.png').convert_alpha()
right_ramp_img = pygame.image.load('assets/images/tiles/right_ramp.png').convert_alpha()
gem_img = pygame.image.load('assets/images/items/gem2.png').convert_alpha()
heart_img = pygame.image.load('assets/images/items/heart.png').convert_alpha()

enemy_imgs = pygame.image.load('assets/images/characters/enemy2a.png').convert_alpha()

lawnmower_imgs_rt = [pygame.image.load('assets/images/characters/lawnmower.png').convert_alpha()]
lawnmower_imgs_lt = [pygame.image.load('assets/images/characters/lawnmowerw1.png').convert_alpha()]


axe_imgs = [pygame.image.load('assets/images/characters/axe1.png').convert_alpha(),
            pygame.image.load('assets/images/characters/axe2a.png').convert_alpha()]

flag_img = pygame.image.load('assets/images/tiles/Tree.png').convert_alpha()
pole_img = pygame.image.load('assets/images/tiles/Flag_pole.png').convert_alpha()
# Load sounds
lawnmower_msc = 'assets/sounds/lawnmower.wav'
axe_hit_snd = pygame.mixer.Sound('assets/sounds/axe_hit.ogg')

# Load Levels
levels = ['assets/levels/world-1.json',
          'assets/levels/world-2.json',
          'assets/levels/world-3.json',]


#settings
gravity = 1.0
terminal_velocity = 24


# Game classes
class Entity(pygame.sprite.Sprite):
    
    def __init__(self, x, y, image):
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x * GRID_SIZE + GRID_SIZE // 2
        self.rect.centery = y * GRID_SIZE + GRID_SIZE // 2

        self.vx = 0
        self.vy = 0
        
    def apply_gravity(self):
        self.vy += gravity
        if self.vy > terminal_velocity:
            self.vy = terminal_velocity
            
    def check_world_edge(self):
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = self.speed
        elif self.rect.right > world_width:
            self.rect.right = world_width
            self.vx = -1 * self.speed
            
    def move_and_check_blocks(self):
        self.rect.x += self.vx
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for block in hits:
            if self.vx > 0:
                self.rect.right = block.rect.left
            elif self.vx < 0:
                self.rect.left = block.rect.right

        self.rect.y += self.vy
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for block in hits:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.jumping = False
            elif self.vy < 0:
                self.rect.top = block.rect.bottom

            self.vy = 0

class AnimatedEntity(Entity):

    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])

        self.images = images
        self.image_index = 0
        self.ticks = 0
        self.animation_speed = 10

    def set_image_list(self):
        self.images = self.images
        
    def  animate(self):
        self.set_image_list()
        self.ticks += 1
        
        if self.ticks % self.animation_speed == 0:
            self.image_index += 1

            if self.image_index >= len(self.images):
                self.image_index = 0
                
            self.image = self.images[self.image_index] 
        
class Hero(AnimatedEntity):
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.speed = 8
        self.jump_power = 27

        self.vx = 0
        self.vy = 0
        self.hurt_timer = 0
        self.facing_right = True
        self.jumping = False

        self.hearts = 3
        self.gems = 0
        self.score = 0
        self.developer_mode = False

    def move_to(self, x, y):
        self.rect.centerx = x * GRID_SIZE + GRID_SIZE // 2
        self.rect.centery = y * GRID_SIZE + GRID_SIZE // 2
       
    def move_right(self):
    	self.vx = self.speed
    	self.facing_right = True
    	
    def move_left(self):
    	self.vx = -1 * self.speed
    	self.facing_right = False

    def stop(self):
        self.vx = 0
    
    def jump(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 1

        if len(hits) > 0:
            self.vy = -1 * self.jump_power
            self.jumping = True
            
    def check_items(self):
        hits = pygame.sprite.spritecollide(self, items, True)

        for item in hits:
            item.apply(self)
            
    def check_enemies(self):
        hits = pygame.sprite.spritecollide(self, enemies, False)

        for enemy in hits:
            if self.rect.centerx < enemy.rect.centerx:
                self.rect.right = enemy.rect.left
            elif self.rect.centerx > enemy.rect.centerx:
                self.rect.left = enemy.rect.right
            if self.rect.centery < enemy.rect.centery:
                self.rect.bottom = enemy.rect.top           
            elif self.rect.centery > enemy.rect.centery:
                self.rect.bottom = enemy.rect.top
                    
            if self.hurt_timer == 0:
                    self.hearts -= 1
                    self.hurt_timer = 1.0 * FPS
                    print(self.hearts)
            else:
                self.hurt_timer -= 1

                if self.hurt_timer < 0:
                    self.hurt_timer = 0

    def reached_goal(self):
        return pygame.sprite.spritecollideany(self, goal)

    def set_image_list(self):
        if self.facing_right:
            if self.jumping:
                self.images = hero_jump_imgs_rt
            elif self.vx == 0: 
                self.images = hero_idle_imgs_rt
            else:
                self.images = hero_walk_imgs_rt
        else:
            if self.jumping:
                self.images = hero_jump_imgs_lt
            elif self.vx == 0:
                self.images = hero_idle_imgs_lt
            else:
                self.images = hero_walk_imgs_lt

    def update(self):
        if self.developer_mode == True:
            self.apply_gravity()
            self.check_world_edge()
            self.check_items()
            self.move_and_check_blocks()
            self.animate()
        else:
            self.check_enemies()
            self.apply_gravity()
            self.check_world_edge()
            self.check_items()
            self.move_and_check_blocks()
            self.animate()

    
        
class Gem(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
    def apply(self, character):
        character.gems += 1
        character.score += 10
        print(character.gems)

    	 
class Block(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(self, x, y, image)

class Platform(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Flag(Entity):
    
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Enemy(AnimatedEntity):
    
    def __init__(self, x, y, images):
        super().__init__(x, y, images)
        self.speed = 2
        self.vx = -1 * self.speed
        self.vy = 0

    def reverse(self):
        self.vx *= -1

    def check_platform_edges(self):
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, platforms, False)
        self.rect.y -= 2

        must_reverse = True

        for platform in hits:
            if self.vx < 0 and platform.rect.left <= self.rect.left:
                must_reverse = False
            elif self.vx > 0 and platform.rect.right >= self.rect.right:
                must_reverse = False

        if must_reverse:
            self.reverse()
        
    def update(self):
        self.check_world_edge()
        self.apply_gravity()
        self.check_platform_edges()
        self.move_and_check_blocks()
        
class Lawnmower(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)
        self.speed = 3.5
        self.vx = -1 * self.speed

    def set_image_list(self):
        if self.vx < 0:
            self.images = lawnmower_imgs_lt
        else:
            self.images = lawnmower_imgs_rt
        
    def update(self):
        self.apply_gravity()
        self.check_platform_edges()
        self.animate()
        self.move_and_check_blocks()
        self.check_world_edge()

class Blade(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)
        self.animation_speed = 4
        
    def update(self):
        self.move_and_check_blocks()
        self.check_world_edge()
        self.apply_gravity()
        self.check_platform_edges()
        self.animate()
        
def show_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, [x, 0], [x, HEIGHT], 1)
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, [0, y], [WIDTH, y], 1)

    for x in range(0, WIDTH, GRID_SIZE):
        for y in range(0, HEIGHT, GRID_SIZE):
            point = '(' + str(x//64) + ',' + str(y // 64) + ')'
            text = font_xs.render(point, True, GRAY)
            screen.blit(text, [x + 4, y + 4])

# Helper functoins
def draw_grid(offset_x = 0, offset_y = 0):
    for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
        adj_x = x - offset_x % GRID_SIZE
        pygame.draw.line(screen, GRAY, [adj_x, 0], [adj_x, HEIGHT], 1)

    for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
        adj_y = y - offset_y % GRID_SIZE
        pygame.draw.line(screen, GRAY, [0, adj_y], [WIDTH, adj_y], 1)

    for x in range(0, WIDTH + GRID_SIZE, GRID_SIZE):
        for y in range(0, HEIGHT + GRID_SIZE, GRID_SIZE):
            adj_x = x - offset_x % GRID_SIZE + 4
            adj_y = y - offset_y % GRID_SIZE + 4
            disp_x = x // GRID_SIZE + offset_x // GRID_SIZE
            disp_y = y // GRID_SIZE + offset_y // GRID_SIZE
            
            point = '(' + str(disp_x) + ',' + str(disp_y) + ')'
            text = font_xs.render(point, True, GRAY)
            screen.blit(text, [adj_x, adj_y])

def show_start_screen():
    text = font_xl.render(TITLE, True, WHITE)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2 - 8
    screen.blit(text, rect)

    text = font_sm.render('Press any key to start', True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 2, HEIGHT // 2 + 8
    screen.blit(text, rect)

def show_lose_screen():
    text = font_xl.render('Game Over', True, WHITE)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2 - 8
    screen.blit(text, rect)

    text = font_sm.render('Press r to play again', True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 2, HEIGHT // 2 + 8
    screen.blit(text, rect)

def show_win_screen():
    text = font_xl.render('You Win!', True, WHITE)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2 - 8
    screen.blit(text, rect)

    text = font_sm.render('Press r to play again', True, WHITE)
    rect = text.get_rect()
    rect.center = WIDTH // 2, HEIGHT // 2 + 8
    screen.blit(text, rect)
    
def show_level_complete_screen():
    text = font_xl.render('Level Complete!', True, WHITE)
    rect = text.get_rect()
    rect.midbottom = WIDTH // 2, HEIGHT // 2 - 8
    screen.blit(text, rect)


def show_hud():
    text = font_md.render(str(hero.score), True, WHITE)
    rect = text.get_rect()
    rect.midtop = WIDTH // 2, 16
    screen.blit(text, rect)

    screen.blit(gem_img, [WIDTH - 100, 16])
    text = font_md.render('x' + str(hero.gems), True, WHITE) 
    rect = text.get_rect()
    rect.topleft = WIDTH - 60, 25
    screen.blit(text, rect)

    for i in range(hero.hearts):
        x = i * 36 + 16
        y = 16
        screen.blit(heart_img, [x, y])
        
def start_game():
    global hero, stage, current_level
    hero = Hero(0, 0, hero_idle_imgs_rt)
    stage = START
    current_level = 0

def start_level():
    global player, platforms, items, enemies, hero, goal, all_sprites, lawnmowers
    global world_width, world_height
    platforms = pygame.sprite.Group()
    player = pygame.sprite.GroupSingle()
    blades = pygame.sprite.Group()
    lawnmowers = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    items = pygame.sprite.Group()
    goal = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    
    with open (levels[current_level]) as f:
        data = json.load(f)

    world_width = data['width'] * GRID_SIZE
    world_height = data['height'] * GRID_SIZE
    
    for loc in data['grass_locs']:
        x = loc[0]
        y = loc[1]
        p = Platform(x, y, grass_dirt_img)
        platforms.add(p)

    for loc in data['block_locs']:
        x = loc[0]
        y = loc[1]
        p = Platform(x, y, platform_img)
        platforms.add(p)

    for loc in data['gem_locs']:
        x = loc[0]
        y = loc[1]
        g = Gem(x, y, gem_img)
        items.add(g)

    hero.move_to(data['start'][0], data['start'][1])
    player.add(hero)

    for i, loc in enumerate(data['flag_locs']):
        if i == 0:
            goal.add( Flag(loc[0], loc[1], flag_img) )
        else:
            goal.add( Flag(loc[0], loc[1], pole_img) )

    for loc in data['lawnmower_locs']:
        x = loc[0]
        y = loc[1]
        L = Lawnmower(x, y, lawnmower_imgs_lt)
        enemies.add(L)

    for loc in data['blade_locs']:
        x = loc[0]
        y = loc[1]
        B = Blade(x, y, axe_imgs)
        enemies.add(B)

    all_sprites.add(player, platforms, items, enemies, goal)
    pygame.mixer.music.load(lawnmower_msc)
    pygame.mixer.music.play(-1)
    
# Game loop
grid_on = False

running = True
start_game()
start_level()
while running:
    # Input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                hero.developer_mode = True
                
            elif stage == START:
                stage = PLAYING
                if event.key == pygame.K_ESCAPE:
                    running = False

            elif stage == PLAYING:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    hero.jump()
                elif event.key == pygame.K_g:
                    grid_on = not grid_on

            elif stage == LOSE or stage == WIN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    start_game()
                    start_level()
                
    pressed = pygame.key.get_pressed()
    
    if stage == PLAYING:
        if pressed[pygame.K_LEFT]:
            hero.move_left()
        elif pressed[pygame.K_RIGHT]:
            hero.move_right()
        else:
            hero.stop()
        
    # Game logic
    if stage == PLAYING:
        all_sprites.update()
        
        if hero.hearts == 0:
            stage = LOSE

        elif hero.reached_goal():
            stage = LEVEL_COMPLETE
            countdown = 2 * FPS
            
        dist = world_width
        for mower in lawnmowers:
            dist = min(world_width, abs(hero.rect.x - mower.rect.x))
        volume = 1 - (dist / world_width)
        pygame.mixer.music.set_volume(volume)
        print(volume)
            
    elif stage == LEVEL_COMPLETE:
        countdown -= 1
        if countdown <+ 0:
            current_level += 1

            if current_level < len(levels):                    
                start_level()
                stage = PLAYING
            else:
                stage = WIN
            
    if hero.rect.centerx < WIDTH // 2:
        offset_x = 0
    elif hero.rect.centerx > world_width - WIDTH // 2:
        offset_x = world_width - WIDTH 
    else:
        offset_x = hero.rect.centerx - WIDTH // 2
    
            
    # Drawing code
    screen.fill(SKY_BLUE)

    for sprite in all_sprites:
        screen.blit(sprite.image, [sprite.rect.x - offset_x, sprite.rect.y])
        
    if grid_on:
        draw_grid(offset_x)
    show_hud()

    if stage == START:
        show_start_screen()
    elif stage == LOSE:
        show_lose_screen()
    elif stage == LEVEL_COMPLETE:
        show_level_complete_screen()
    elif stage == WIN:
        show_win_screen()

        
    # Update screen
    pygame.display.update()


    # Limit refresh rate of game loop 
    clock.tick(FPS)


# Close window and quit
pygame.quit()

