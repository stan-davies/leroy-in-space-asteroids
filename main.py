import math
import math as maths
import random
import sys
import json

import pygame
import pygame.joystick
import pygame.locals

# INIT
pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# laoding in json and getting its data
data = json.load(open('data.json'))
WIDTH = data["WIDTH"]
HEIGHT = data["HEIGHT"]
MULTIPLIER = data["MULTIPLIER"]
HIGHSCORE = data["HIGHSCORE"]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screenrect = screen.get_rect()
clock = pygame.time.Clock()
FPS = 120
pygame.mixer.set_num_channels(6)
pygame.display.set_caption("leroy in space: asteroids")

# VARIABLES
w = False
a = False
s = False
d = False
flameSize = ((68 // 3) * MULTIPLIER, (112 // 3) * MULTIPLIER)

asteroid1 = pygame.transform.smoothscale(pygame.image.load("files/asteroid1.png").convert_alpha(),
                                         (62 * MULTIPLIER, 62 * MULTIPLIER))
asteroid2 = pygame.transform.smoothscale(pygame.image.load("files/asteroid2.png").convert_alpha(),
                                         (60 * MULTIPLIER, 30 * MULTIPLIER))
asteroid3 = pygame.transform.smoothscale(pygame.image.load("files/asteroid3.png").convert_alpha(),
                                         (50 * MULTIPLIER, 36 * MULTIPLIER))
asteroid4 = pygame.transform.smoothscale(pygame.image.load("files/asteroid4.png").convert_alpha(),
                                         (26 * MULTIPLIER, 22 * MULTIPLIER))
asteroids = [asteroid1, asteroid2, asteroid3, asteroid4]
hitwhite = pygame.transform.smoothscale(pygame.image.load("files/whitex.png").convert_alpha(),
                                        (10 * MULTIPLIER, 10 * MULTIPLIER))
hitred = pygame.transform.smoothscale(pygame.image.load("files/redx.png").convert_alpha(),
                                      (30 * MULTIPLIER, 30 * MULTIPLIER))
shieldpng = pygame.transform.smoothscale(pygame.image.load("files/shield.png").convert_alpha(),
                                         ((100 // 3) * MULTIPLIER, (100 // 3) * MULTIPLIER))
boosterpng = pygame.transform.smoothscale(pygame.image.load("files/flame1.png").convert_alpha(), (flameSize))
boosterpng2 = pygame.transform.smoothscale(pygame.image.load("files/flame2.png").convert_alpha(), (flameSize))
boosterpng3 = pygame.transform.smoothscale(pygame.image.load('files/flame3.png').convert_alpha(), (flameSize))
boosterpng4 = pygame.transform.smoothscale(pygame.image.load('files/flame4.png').convert_alpha(), (flameSize))
boosterpng5 = pygame.transform.smoothscale(pygame.image.load('files/flame5.png').convert_alpha(), (flameSize))
torchpng = pygame.transform.smoothscale(pygame.image.load("files/blurred torch.png").convert_alpha(),
                                        (600 * MULTIPLIER, 1200 * MULTIPLIER))

# font = pygame.font.Font('files/vgafix.fon', 36 * MULTIPLIER)
# bold_font = pygame.font.Font('files/vgafix.fon', 45 * MULTIPLIER)
font = pygame.font.Font('files/WhiteRabbit-47pD.ttf', 20 * MULTIPLIER)
bold_font = pygame.font.Font('files/WhiteRabbit-47pD.ttf', 29 * MULTIPLIER)

BLACK = pygame.Color(0, 0, 0, 255)
RED = pygame.Color(255, 0, 0, 255)
WHITE = pygame.Color(255, 255, 255, 255)
BLUE = pygame.Color(0, 255, 255, 255)
GREEN = pygame.Color(0, 255, 0, 255)
LIGHT_GREY = pygame.Color(200, 200, 200, 255)
DARK_GREY = pygame.Color(50, 50, 50, 255)
PURPLE = pygame.Color(255, 0, 255, 255)
SEMIBLUE = pygame.Color(0, 0, 255, 225)

run = False
finish = False
win = False
varinfoExists = False
startMenu = True
preferences = False
playMusic = False
play = True
varinfo = None

hitlist = []
collisions = []

lastfire = 0
lastmissile = 0
level = 1
asteroidCount = 2
startscreen = 1
inputType = 1
nextBullet = 60

AsteroidNames = ["callisto", "io", "iapetus", "europa", "ganymede", "titan", "himalia", "lysithea", "valetudo",
                 "euanthe", "amalthea", "adastrea", "ananke", "pasiphae", "metis", "elara", "carme", "thebe",
                 "callirrhoe", "ersa", "eupheme", "dia", "euporie"]

asteroidsKilled = 0


def rotatezoom(surface, angle, newcenter):
    rotatedsurface = pygame.transform.rotozoom(surface, angle, 1)
    rotatedrect = rotatedsurface.get_rect(center=newcenter)
    return rotatedsurface, rotatedrect


def dynamicresize(num):
    num * MULTIPLIER
    return num


def createbullet(projType):
    global lastfire, nextBullet
    now = pygame.time.get_ticks()
    if (now - lastfire) < nextBullet:
        return
    else:
        if projType == "bullet":
            projectile = Bullet(player.unit, player.angle)
            nextBullet = 60
        elif projType == "missile":
            projectile = HomingMissile()
            nextBullet = 480
        else:
            projectile = Laser(player.unit, player.angle)
            nextBullet = 60
        allsprites.add(projectile)
        bulletsprites.add(projectile)
        lastfire = now


def shoot():
    soundObj = pygame.mixer.Sound('files/sound5.wav')
    soundObj.set_volume(0.1)
    # soundObj.play()


def hit():
    soundObj = pygame.mixer.Sound('files/sound6.wav')
    soundObj.set_volume(0.5)
    pygame.mixer.Channel(0).play(soundObj)


def booster():
    if not pygame.mixer.Channel(1).get_busy():
        soundObj = pygame.mixer.Sound('files/sound7.wav')
        soundObj.set_volume(0.5)
        pygame.mixer.Channel(1).play(soundObj)


def powerupnoise():
    if not pygame.mixer.Channel(2).get_busy():
        soundObj = pygame.mixer.Sound('files/sound7.wav')
        soundObj.set_volume(0.5)
        pygame.mixer.Channel(2).play(soundObj)


def powerupavailable():
    if not pygame.mixer.Channel(3).get_busy():
        soundObj = pygame.mixer.Sound('files/sound9.wav')
        soundObj.set_volume(0.5)
        pygame.mixer.Channel(3).play(soundObj)


def music():
    if not pygame.mixer.Channel(4).get_busy():
        # soundObj = pygame.mixer.Sound('files/millibar.wav')   # your song
        soundObj = pygame.mixer.Sound('files/My Song.wav')  # my song (wouldn't recommend)
        soundObj.set_volume(0.3)
        pygame.mixer.Channel(4).play(soundObj)


def intromusic():
    if not pygame.mixer.Channel(5).get_busy():
        soundObj = pygame.mixer.Sound('files/millibar.wav')
        soundObj.set_volume(0.6)
        pygame.mixer.Channel(5).play(soundObj)


def randomvector(inner, outer):
    if inner > outer:
        temp = inner
        inner = outer
        outer = temp
    elif inner == outer:
        outer += 10
    randa = random.random()
    randb = random.random()
    a = -1 * (randa > 0.5) + 1 * (randa < 0.5)
    b = -1 * (randb > 0.5) + 1 * (randb < 0.5)
    randvector = pygame.math.Vector2(random.randint(round(inner), round(outer)) * a,
                                     random.randint(round(inner), round(outer)) * b)
    return randvector


def randomscalar(lower, upper, step):
    if lower > upper:
        temp = lower
        lower = upper
        upper = temp
    elif lower == upper:
        upper += 10

    if step > upper - lower:
        step = (upper - lower) // 2

    randa = random.random()
    posorneg = -1 * (randa > 0.5) + 1 * (randa < 0.5)
    numa = random.randrange(lower, upper, step) * posorneg
    return numa


def randompos():
    top_side = random.randint(50, 250)
    bottom_side = random.randint(750, 950)

    right_side = random.randint(1350, 1850)
    left_side = random.randint(50, 550)

    quarter = random.randint(1, 4)

    if quarter == 1:
        pos = pygame.math.Vector2(left_side, top_side)
    elif quarter == 2:
        pos = pygame.math.Vector2(right_side, top_side)
    elif quarter == 3:
        pos = pygame.math.Vector2(left_side, bottom_side)
    else:
        pos = pygame.math.Vector2(right_side, bottom_side)

    return pos


def createpowerup(pos):
    powerup = 0
    create = random.randint(1, 4)
    if create == 1:
        powerup = Powerup(pos.x, pos.y, "shield")
    elif create == 2:
        powerup = Powerup(pos.x, pos.y, "health")
    elif create == 3:
        powerup = Powerup(pos.x, pos.y, "speed")
    elif create == 4:
        enemy = Enemy("enemy", [60, 70], pygame.math.Vector2(pos.x, pos.y))
        allsprites.add(enemy)
        asteroidsprites.add(enemy)
        enemy.lives = level * 10

    if type(powerup) != int:
        allsprites.add(powerup)
        powerupSprites.add(powerup)
        return powerup


def pausescreen(dopause):
    global level, asteroidCount, HIGHSCORE
    screenCover = pygame.Surface((WIDTH, HEIGHT))
    screenCover.fill(BLACK)
    screenCover.set_alpha(200)
    screen.blit(screenCover, screenCover.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    if dopause:
        pauseTitle = font.render("paused", True, WHITE)
        screen.blit(pauseTitle, pauseTitle.get_rect(center=(WIDTH // 2, (HEIGHT // 2) - 30)))

        unpauseInfo = font.render("press <p> to unpause game", True, WHITE)
        screen.blit(unpauseInfo, unpauseInfo.get_rect(center=(WIDTH // 2, (HEIGHT // 2) + 30)))
    else:
        mousepos = pygame.mouse.get_pos()

        if len(asteroidsprites) == 0:
            successText = f"you win, you eliminated {asteroidsKilled} asteroids"
        else:
            successText = f"you lose, you eliminated {asteroidsKilled} asteroids"

        if HIGHSCORE < asteroidsKilled:
            successText += ", thats a new high score!"
            HIGHSCORE = asteroidsKilled

            json_data = {
                "WIDTH": WIDTH,
                "HEIGHT": HEIGHT,
                "MULTIPLIER": MULTIPLIER,
                "HIGHSCORE": HIGHSCORE
            }

            with open('data.json', 'w') as outf:
                json.dump(json_data, outf)

        successTitle = font.render(successText, True, WHITE)

        screen.blit(successTitle, successTitle.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))

        if level < 11 and len(asteroidsprites) <= 0:
            if mousepos[0] in range(WIDTH // 2 - 70, WIDTH // 2 + 150) and mousepos[1] in range(HEIGHT // 2 + 20,
                                                                                                HEIGHT // 2 + 50):
                nextLevelButton = bold_font.render(f"proceed to level {level + 1}", True, WHITE)
                if pygame.mouse.get_pressed(3)[0]:
                    for i in range(level * 2):
                        asteroid = Asteroid(i, [dynamicresize(60), dynamicresize(120)],
                                            pygame.math.Vector2(
                                                random.randint(dynamicresize(10), WIDTH - dynamicresize(10)),
                                                random.randint(dynamicresize(10), HEIGHT - dynamicresize(10))))
                        asteroidsprites.add(asteroid)
                        allsprites.add(asteroid)

                    if level < 10:
                        enemy = Enemy("enemy", [60, 70], pygame.math.Vector2(randompos()))
                        allsprites.add(enemy)
                        asteroidsprites.add(enemy)
                        enemy.lives = level * 5
                    else:
                        boss = Boss("boss", [60, 70], pygame.math.Vector2(randompos()))
                        allsprites.add(boss)
                        asteroidsprites.add(boss)

                    player.rect.center = (WIDTH // 2, HEIGHT // 2)
                    player.velocity = pygame.math.Vector2(0, 0)
                    player.health = 129
                    player.shield = 129
                    player.fuel = 1038
                    level += 1
                    asteroidCount += 1
                    for bullObj in bulletsprites:
                        bullObj.kill()
            else:
                nextLevelButton = font.render(f"proceed to level {level + 1}", True, WHITE)
            screen.blit(nextLevelButton, nextLevelButton.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))


def gameloop(play):
    global varinfoExists
    global inputType
    global varinfo
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()
                sys.exit()

            if event.key == pygame.K_i:
                if len(infosprites) == 0:
                    varinfo = VarInfo()
                    infosprites.add(varinfo)
                    varinfoExists = True
                else:
                    infosprites.remove(varinfo)
                    varinfoExists = False
            elif event.key == pygame.K_p:
                if play:
                    play = False
                else:
                    play = True
            elif event.key == pygame.K_t:
                inputType = -inputType
    keys = pygame.key.get_pressed()
    events = pygame.event.get()

    if playMusic:
        music()

    screen.fill(BLACK)

    for ast in asteroidsprites:
        collisions = pygame.sprite.collide_rect(ast, player)
        if collisions:
            if player.shield > 0:
                player.shield -= 1
            else:
                player.health -= 1

    for bulletObject in bulletsprites:
        hitCoords = pygame.math.Vector2(bulletObject.rect.center)
        hitlist = pygame.sprite.spritecollide(bulletObject, asteroidsprites, False)
        if not hitlist:
            pass
        else:
            for hits in hitlist:
                hits.ihavebeenhitbyabullet(hitCoords, bulletObject)
                bulletObject.kill()

                if player.powerup <= 945 * 2 and not player.spinAttack:
                    player.powerup += 21

    for asteroid in asteroidsprites:
        # v = asteroid.speedx
        # u = asteroid.speedy
        if asteroid.rect.top > dynamicresize(10) and asteroid.rect.left > dynamicresize(10):
            asteroidhits = pygame.sprite.spritecollide(asteroid, asteroidsprites, False)
            if not asteroidhits:
                pass
            else:
                count = 0
                for crash in asteroidhits:
                    if crash != asteroid:
                        crash.iwashit(asteroid)

    powerupsCaught = pygame.sprite.spritecollide(player, powerupSprites, True)
    for catches in powerupsCaught:
        if catches.powerupType == "shield" and player.shield < 130:
            player.shield += 20
        elif catches.powerupType == "health" and player.health < 130:
            player.health += 20
        elif catches.powerupType == "speed":
            player.maxSpeed += 0.1
            player.boosted = True

    # torchHits = pygame.sprite.spritecollide(torch, allsprites, False)

    # for visibleSprite in torchHits:
    #     screen.blit(visibleSprite.image, visibleSprite.rect)
    allsprites.draw(screen)

    if player.endGame or len(asteroidsprites) <= 0:
        showlevelscreen = True
    else:
        showlevelscreen = False

    if play and not showlevelscreen:
        player.move(keys)
        allsprites.update()
        infosprites.update()
        torchSprite.update()
        hud.update()
        gun.update(keys, events)

    if varinfoExists:
        infosprites.sprites()[0].createitem(len(bulletsprites), f"{len(bulletsprites)=}".split('=')[0])
        infosprites.sprites()[0].createitem(enemy.lives, f"{enemy.lives=}".split('=')[0])

    screen.blit(torch.image, torch.rect)
    # allsprites.draw(screen)
    screen.blit(player.image, player.rect)
    if player.shield > 0:
        screen.blit(shieldpng, shieldpng.get_rect(center=player.rect.center))
    hud.drawme()

    if not play:
        pausescreen(True)

    if level <= 10 and showlevelscreen:
        pausescreen(False)

    pygame.display.update()
    clock.tick(FPS)

    return level, asteroidCount, play


# CLASSES
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.og_image = pygame.transform.smoothscale(pygame.image.load("files/rocket ship.png").convert_alpha(),
                                                     (dynamicresize(68 // 3), dynamicresize(68 // 3)))
        self.image = self.og_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        self.FlameDirection = "none"

        self.angle = 0
        self.ChangeAngle = 0
        self.unit = 0
        self.target = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.velocity = pygame.math.Vector2(0, 0)
        self.maxSpeed = 2
        self.maxVector = pygame.math.Vector2(self.maxSpeed, self.maxSpeed)
        self.health = 129
        self.shield = 129
        self.fuel = 1038
        self.powerup = 0
        self.powerupMax = 945 * 2
        self.endGame = False
        self.playBoosterNoise = False
        self.spinAttack = False
        self.targetAngle = 0
        self.boosted = False
        self.moving = False
        self.starterShip = False
        self.lasers = False

        self.frames = [boosterpng, boosterpng2, boosterpng3, boosterpng4, boosterpng5]
        self.currentFrame = 0
        self.boosterImage = self.frames[self.currentFrame]

    def update(self):
        pass
        # don't put anything in here but also don't delete it

    def rotate(self):
        self.image = pygame.transform.rotate(self.og_image, self.angle)
        self.angle += self.ChangeAngle
        self.angle = self.angle % 360
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self, keys):
        global boosterpng
        self.playBoosterNoise = False

        self.ChangeAngle = 0
        self.pos = pygame.math.Vector2(self.rect.center)

        if self.powerup >= self.powerupMax:
            powerupavailable()
            self.PUBcolour = PURPLE
            if keys[pygame.K_BACKSLASH] or (inputType == 0 and joysticks[0].get_button(1)):
                powerupnoise()
                powerup = random.random()
                if powerup <= 0.5:
                    self.spinAttack = True
                else:
                    self.lasers = True

        if self.spinAttack:
            for i in range(8):
                bullet = Bullet(self.unit.rotate(i * 45), -i * 45)
                bulletsprites.add(bullet)
                allsprites.add(bullet)

            self.powerup -= 10.5
            if self.powerup <= 0:
                self.spinAttack = False
                self.PUBcolour = LIGHT_GREY
        elif self.lasers:
            self.powerup -= 5.25
            if self.powerup <= 0:
                self.lasers = False
                self.PUBcolour = LIGHT_GREY

        if inputType == 1:
            # keyboard input
            if keys[pygame.K_a]:
                self.ChangeAngle = 5
            elif keys[pygame.K_d]:
                self.ChangeAngle = -5
        else:
            # joystick input
            self.ChangeAngle = -joysticks[0].get_axis(2)

        self.rotate()

        self.unit = pygame.math.Vector2(
            [maths.cos(maths.radians(self.angle - 90)), -maths.sin(maths.radians(self.angle - 90))])
        self.target = pygame.math.Vector2(self.pos - (600 * self.unit))

        if inputType == 1:
            # keyboard input
            if keys[pygame.K_w] and self.fuel > 0:
                self.moving = True
            elif keys[pygame.K_s] and self.fuel > 0:
                self.fuel -= 1
                self.unit /= 10
                if pygame.math.Vector2.magnitude(self.velocity + self.unit) < self.maxSpeed:
                    self.velocity += self.unit
            elif not self.starterShip:
                self.moving = False
        else:
            # joystick input
            if -joysticks[0].get_axis(3) > 0 and not self.starterShip:
                self.moving = True
            else:
                self.moving = False

        if self.moving:
            self.playBoosterNoise = True
            self.fuel -= 1
            self.unit /= 10
            self.currentFrame += 0.1
            if math.floor(self.currentFrame) > 4:
                self.currentFrame = 0
            # pygame.draw.aaline(screen, RED, [round(self.pos.x), round(self.pos.y)], [round(self.target.x), round(self.target.y)], 5)
            boosterPicture = self.frames[math.floor(self.currentFrame)]
            self.boosterImage = boosterPicture
            boosterPicture = pygame.transform.rotate(self.boosterImage, (self.angle % 360))
            boosterPos = pygame.math.Vector2(round(self.pos.x), round(self.pos.y)) + (self.unit * 100)
            screen.blit(boosterPicture, boosterPicture.get_rect(center=boosterPos))
            if pygame.math.Vector2.magnitude(self.velocity - self.unit) < self.maxSpeed:
                self.velocity -= self.unit
                # self.velocity *= 2

        if self.playBoosterNoise:
            booster()
        else:
            pygame.mixer.Channel(1).stop()

        self.rect.center += pygame.math.Vector2(round(self.velocity.x), round(self.velocity.y))

        if self.rect.centerx > WIDTH + 100:
            self.rect.centerx = -100
        elif self.rect.centerx < -100:
            self.rect.centerx = WIDTH + 100

        if self.rect.centery < -100:
            self.rect.centery = HEIGHT + 100
        elif self.rect.centery > HEIGHT + 100:
            self.rect.centery = -100

        if self.health <= 0:
            self.endGame = True

        targetVector = pygame.math.Vector2(missileTarget.rect.center) - pygame.math.Vector2(self.rect.center)
        self.targetAngle = targetVector.angle_to(self.unit)

        # pygame.draw.aaline(screen, RED, self.rect.center, missileTarget.rect.center)

        for ast in asteroidsprites:
            tarVec = pygame.math.Vector2(ast.rect.center) - pygame.math.Vector2(self.rect.center)
            tarAng = abs(tarVec.angle_to(-self.unit))
            if tarAng > 20:
                coverSize = ast.imageSize + 20
                cover = pygame.Surface((coverSize, coverSize))
                cover = pygame.transform.rotate(cover, ast.rotation)
                cover.fill(BLACK)
                cover.set_alpha(100)
                coverPos = ast.rect.topleft
                screen.blit(cover, coverPos)

                ast.inLight = False
            else:
                ast.inLight = True

        if varinfoExists:
            infosprites.sprites()[0].createitem(self.velocity.magnitude(),
                                                f"{self.velocity.magnitude()=}".split('=')[0])
            infosprites.sprites()[0].createitem(self.velocity, f"{self.velocity=}".split('=')[0])
            infosprites.sprites()[0].createitem(self.unit, f"{self.unit=}".split('=')[0])


class Hud:
    def __init__(self):
        self.healthOutline = pygame.rect.Rect(((WIDTH // 2) - dynamicresize(160), HEIGHT - dynamicresize(70)),
                                              (dynamicresize(150), dynamicresize(40)))
        self.healthBar = pygame.rect.Rect(((WIDTH // 2) - dynamicresize(150), HEIGHT - dynamicresize(60)),
                                          (dynamicresize(130), dynamicresize(20)))
        # self.shieldBar = pygame.rect.Rect(((WIDTH // 2) - 150, HEIGHT - 60), (130, 20))
        self.shieldBar = pygame.Surface((dynamicresize(130), dynamicresize(20)))
        self.shieldBar.set_alpha(200)
        self.shieldBar.fill(BLUE)
        self.healthFiller = pygame.rect.Rect(((WIDTH // 2) - dynamicresize(157), HEIGHT - dynamicresize(67)),
                                             (dynamicresize(143), dynamicresize(33)))

        self.fuelOutline = pygame.rect.Rect(((WIDTH // 2) + dynamicresize(10), HEIGHT - dynamicresize(70)),
                                            (dynamicresize(150), dynamicresize(40)))
        self.fuelBar = pygame.rect.Rect(((WIDTH // 2) + dynamicresize(20), HEIGHT - dynamicresize(60)),
                                        (dynamicresize(130), dynamicresize(20)))
        self.fuelFiller = pygame.rect.Rect(((WIDTH // 2) + dynamicresize(13), HEIGHT - dynamicresize(67)),
                                           (dynamicresize(143), dynamicresize(33)))

        self.powerupOutline = pygame.rect.Rect((WIDTH - dynamicresize(50), dynamicresize(10)),
                                               (dynamicresize(40), HEIGHT - dynamicresize(20)))
        self.powerupBar = pygame.rect.Rect((WIDTH - dynamicresize(43), dynamicresize(16)), (dynamicresize(26), 0))
        self.PUBcolour = LIGHT_GREY
        self.powerupFiller = pygame.rect.Rect((WIDTH - dynamicresize(47), dynamicresize(13)),
                                              (dynamicresize(33), HEIGHT - dynamicresize(27)))

        self.level = font.render(f"{level = }", True, WHITE)

    def update(self):
        self.healthBar = pygame.rect.Rect(((WIDTH // 2) - dynamicresize(150), HEIGHT - dynamicresize(60)),
                                          (player.health % dynamicresize(130), dynamicresize(20)))
        self.shieldBar = pygame.Surface((player.shield % dynamicresize(130), dynamicresize(20)))
        self.shieldBar.set_alpha(200)
        self.shieldBar.fill(BLUE)
        self.fuelBar = pygame.rect.Rect(((WIDTH // 2) + dynamicresize(20), HEIGHT - dynamicresize(60)),
                                        ((player.fuel // 8) % dynamicresize(130), dynamicresize(20)))
        self.powerupBar = pygame.rect.Rect((WIDTH - dynamicresize(43), dynamicresize(16)),
                                           (dynamicresize(26), player.powerup // 2))

        self.level = font.render(f"{level = }", True, WHITE)

    def drawme(self):
        pygame.draw.rect(screen, WHITE, self.healthOutline)
        pygame.draw.rect(screen, BLACK, self.healthFiller)
        pygame.draw.rect(screen, RED, self.healthBar)
        screen.blit(self.shieldBar, ((WIDTH // 2) - dynamicresize(150), HEIGHT - dynamicresize(60)))

        pygame.draw.rect(screen, WHITE, self.fuelOutline)
        pygame.draw.rect(screen, BLACK, self.fuelFiller)
        pygame.draw.rect(screen, GREEN, self.fuelBar)

        pygame.draw.rect(screen, WHITE, self.powerupOutline)
        pygame.draw.rect(screen, BLACK, self.powerupFiller)
        pygame.draw.rect(screen, self.PUBcolour, self.powerupBar)

        screen.blit(self.level, self.level.get_rect(center=(WIDTH // 2, 50)))


class Torch(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.ogImage = torchpng
        self.image = self.ogImage
        self.rect = self.image.get_rect()
        self.rect.center = player.target

    def update(self):
        self.rect.center = player.target
        self.image = pygame.transform.rotate(self.ogImage, player.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class Gun(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.smoothscale(pygame.image.load('files/big ol bomb.png').convert_alpha(), (30, 30))
        self.rect = self.image.get_rect(center=player.rect.center)

        self.velocity = player.velocity

        self.fire = False
        self.missile = False

    def update(self, keys, events):
        self.velocity = player.velocity
        self.rect.center += self.velocity

        if self.fire:
            if player.lasers:
                projtype = "laser"
            elif self.missile:
                projtype = "missile"
            else:
                projtype = "bullet"
            createbullet(projtype)
            shoot()

        if inputType == 1:
            # keyboard input
            if keys[pygame.K_RETURN]:
                self.fire = True
            elif keys[pygame.K_RSHIFT]:
                self.fire = True
                self.missile = True
            else:
                self.fire = False
                self.missile = False
        else:
            if joysticks[0].get_button(0):
                self.fire = True
            else:
                self.fire = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, parentunit, angle):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.smoothscale(pygame.image.load("files/bullet textture 2.png").convert_alpha(),
                                                  (dynamicresize(10), dynamicresize(10)))
        self.rect = self.image.get_rect(center=player.rect.center)

        self.unit = -pygame.math.Vector2.normalize(parentunit) * 32

        self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        self.unit -= self.unit / 20

        if self.rect.centerx < -100 or self.rect.centerx > WIDTH + 100 or self.rect.centery < -100 or \
                self.rect.centery > HEIGHT + 100 or pygame.math.Vector2.magnitude(self.unit) < 1:
            self.kill()

        self.rect.move_ip(round(self.unit.x), round(self.unit.y))


class Laser(Bullet):
    def __init__(self, parentunit, angle):
        super().__init__(parentunit, angle)

        self.image = pygame.transform.smoothscale(pygame.image.load('files/laser.png').convert_alpha(), (10, 10))
        self.rect = self.image.get_rect(center=player.rect.center)
        self.image = pygame.transform.rotate(self.image, angle)

        self.unit *= 1.5


class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, version):
        pygame.sprite.Sprite.__init__(self)
        self.powerupType = version

        size = dynamicresize(50)

        if self.powerupType == "shield":
            self.image = pygame.transform.smoothscale(pygame.image.load('files/shield increaser.png').convert_alpha(),
                                                      (size, size))
        elif self.powerupType == "health":
            self.image = pygame.transform.smoothscale(pygame.image.load('files/health increaser.png').convert_alpha(),
                                                      (size, size))
        elif self.powerupType == "speed":
            self.image = pygame.transform.smoothscale(pygame.image.load('files/speed increaser.png').convert_alpha(),
                                                      (size, size))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        relPos = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        try:
            self.unit = relPos.normalize() * 5
        except:
            pass

    def update(self):
        self.rect.center += self.unit

        # perturbation = randomvector(0, 1)
        # self.velocity += perturbation


class HomingMissile(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.og_image = pygame.transform.smoothscale(pygame.image.load("files/big ol bomb.png").convert_alpha(),
                                                     (15, 15))
        self.image = self.og_image
        self.rect = self.image.get_rect(center=player.rect.center)

        self.viableAsts = [a for a in asteroidsprites if a.inLight]
        if self.viableAsts:
            self.target = self.viableAsts[random.randint(0, (len(self.viableAsts) - 1))]
            self.unit = (pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)).normalize() * 10
        else:
            self.target = None
            self.unit = pygame.math.Vector2(1, 1)

    def update(self):
        if not self.target:
            self.kill()
        else:
            self.update_vector()
            if not (self.target.rect.centerx in range(0, WIDTH) and self.target.rect.centery in range(0, HEIGHT)):
                self.target = None

        if ((maths.floor(self.unit.x), maths.floor(self.unit.y)) == (0, 0)) or \
                not(self.rect.centerx in range(1, WIDTH - 1) and self.rect.centery in range(1, HEIGHT - 1)):
            self.kill()
  
        self.rect.center += self.unit

    def update_vector(self):
        # an alternate pathfinding method which just gets the relative vector and then makes it smaller and then gets cracking
        # self.unit = (pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)) // 20

        # vector between the projectile and target (correct direction)
        relVec = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
        # the angle between the correct path and current path
        relAng = round(relVec.angle_to(self.unit))

        # if the vector is to the right
        if relAng > 0:
            # turn clockwise (rotate normally turns anti-clockwise so it has to be negative for clockwise)
            self.unit.rotate_ip(-20)
        # the other bit
        elif relAng < 0:
            # ip means in place, i dont know what that means but it works and rotate() doesnt
            self.unit.rotate_ip(20)


class HomingMissileTwo(HomingMissile):
    def __init__(self):
        super().__init__()

        if self.target:
            self.unit = (player.velocity + self.unit) // 10

    def update_vector(self):
        # vector between the projectile and target (correct direction)
        relVec = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
        # the angle between the correct path and current path
        relAng = abs(relVec.angle_to(self.unit))

        # if the vector is to the right
        if relAng in range(1, 180):
            # turn clockwise
            self.unit.rotate(60)
        # the other bit
        elif relAng in range(181, 360):
            self.unit.rotate(-60)


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, number, size: list, pos):
        pygame.sprite.Sprite.__init__(self)

        self.size = [dynamicresize(size[0]), dynamicresize(size[1])]
        self.imageSize = random.randrange(self.size[0], self.size[1], 10)
        if self.imageSize in range(0, 40):
            self.type = "tiny"
            self.divisor = 1
        elif self.imageSize in range(41, 60):
            self.type = "small"
            self.divisor = 2
        elif self.imageSize in range(61, 80):
            self.type = "medium"
            self.divisor = 3
        elif self.imageSize in range(81, 100):
            self.type = "big"
            self.divisor = 4
        elif self.imageSize in range(101, 120):
            self.type = "large"
            self.divisor = 5
        else:
            self.type = "huge"
            self.divisor = 6
        self.rotation = randomscalar(1, 10, 2)
        self.rotateSpeed = randomscalar(1, 10, 2) // self.divisor

        self.og_image = asteroid1
        self.og_image = pygame.transform.scale(self.og_image, (self.imageSize, self.imageSize))
        # self.og_image = pygame.transform.rotate(self.og_image, self.rotation)
        self.image = self.og_image
        self.rect = self.image.get_rect(center=pos)

        self.velocity = pygame.math.Vector2()
        self.velocity.x = randomscalar(6, 9 + level, 1) // self.divisor
        self.velocity.y = randomscalar(6, 9 + level, 1) // self.divisor

        self.num = 5

        if type(number) == int:
            self.name = AsteroidNames[number]
        else:
            self.name = number

        self.HitCounter = 0

        self.color = 255, 255, 255
        self.text = font.render(self.name, True, self.color)

        self.whereIHaveBeenHit = []

        self.lives = 3

        self.inLight = False

    def update(self):
        self.rect.center += self.velocity * (level / 2)
        self.rotation += self.rotateSpeed
        self.image, self.rect = rotatezoom(self.og_image, self.rotation, self.rect.center)

        if self.rect.centerx < -100:
            self.rect.centerx = WIDTH + 100
        elif self.rect.centerx > WIDTH + 100:
            self.rect.centerx = -100

        if self.rect.centery < -100:
            self.rect.centery = WIDTH + 100
        elif self.rect.centery > WIDTH + 100:
            self.rect.centery = -100

        self.showhit()

        if varinfoExists:
            infosprites.sprites()[0].createitem(len(asteroidsprites), f"{len(asteroidsprites)=}".split('=')[0])
            infosprites.sprites()[0].createitem(infosprites.sprites()[0].asteroidBugs,
                                                f"{infosprites.sprites()[0].asteroidBugs=}".split('=')[0])

    def iwashit(self, crasher):

        selfCenter = pygame.math.Vector2(self.rect.center)
        hitterCenter = pygame.math.Vector2(pygame.math.Vector2(crasher.rect.center))
        relativeVector = selfCenter - hitterCenter
        if relativeVector.magnitude() > 0:
            normalVector: pygame.math.Vector2 = pygame.math.Vector2.rotate(relativeVector, 90)
            self.rect.center -= self.velocity * 2
            self.velocity = self.velocity.reflect(normalVector)
        else:
            if varinfoExists:
                infosprites.sprites()[0].asteroidBugs += 1

            allsprites.remove(crasher)
            asteroidsprites.remove(crasher)

            self.velocity *= 1.2
            self.blowmeup(1)

    def ihavebeenhitbyabullet(self, hitCoords, collider):
        global asteroidsKilled

        astCoords = pygame.math.Vector2(self.rect.center)
        relPos = hitCoords - astCoords
        if relPos.x > 0:
            if relPos.y > 0:
                whereHit = "topright"
            else:
                whereHit = "bottomright"
        else:
            if relPos.y > 0:
                whereHit = "topleft"
            else:
                whereHit = "bottomleft"

        if whereHit == "topright" or whereHit == "bottomleft":
            spin = -1
        else:
            spin = 1

        relAng = abs(relPos.angle_to(collider.unit))
        spin *= relAng / 20

        self.rotateSpeed += spin

        pushAst = relPos / 10
        self.velocity.x = round(-pushAst.x)
        self.velocity.y = round(-pushAst.y)

        if player.lasers:
            self.lives -= 3
        else:
            self.lives -= 1

        hit()

        if self.lives == 0:
            asteroidsKilled += 1
            self.blowmeup(3)

            self.kill()

            powerup = createpowerup(hitCoords)

        self.whereIHaveBeenHit.append([relPos, 30])

    def showhit(self):
        if len(self.whereIHaveBeenHit) > 0:
            center = pygame.math.Vector2(self.rect.center)
            for item in self.whereIHaveBeenHit:
                item[1] -= 1
                if item[1] == 0:
                    self.whereIHaveBeenHit.remove(item)
                size = random.randint(dynamicresize(60), dynamicresize(100))
                hitmarker = pygame.Surface((size, size))
                pygame.draw.circle(hitmarker,
                                   (random.randint(150, 225), random.randint(80, 120), random.randint(60, 100)),
                                   (size // 4, size // 4), (size // 4))
                hitmarker.set_alpha(random.randint(130, 180))
                hitmarkerPos = center
                screen.blit(hitmarker, hitmarkerPos)

    def blowmeup(self, times):
        newSize = [self.size[0] - 20, self.size[1] - 20]
        if newSize[0] < 0:
            return
        for j in range(times):
            if newSize[0] > dynamicresize(30):
                rotatedVector = self.velocity.rotate((j - 1) * 120)
                if rotatedVector.magnitude() > 0:
                    rotatedNormal = rotatedVector.normalize() * self.imageSize
                    asteroid = Asteroid(self.name + " - " + str(j + 1), newSize, self.rect.center + rotatedNormal)
                    asteroid.velocity.x = rotatedVector.x
                    asteroid.velocity.y = rotatedVector.y
                    asteroidsprites.add(asteroid)
                    allsprites.add(asteroid)


class Enemy(Asteroid):
    def __init__(self, number, size, pos):
        super().__init__(number, size, pos)
        self.og_image = pygame.transform.smoothscale(pygame.image.load('files/rocket ship.png').convert_alpha(),
                                                     (60, 60))
        self.image = self.og_image
        self.rect = self.image.get_rect(center=pos)

        self.velocity.x = 0
        self.velocity.y = 0

        self.rotateSpeed = 0
        self.rotation = 0

    def update(self):
        super().update()
        relPos = pygame.math.Vector2(player.rect.center) - pygame.math.Vector2(self.rect.center)
        if relPos.x != 0 and relPos.y != 0:
            relUnit = relPos.normalize()
            self.velocity = relUnit
            self.rect.center += pygame.math.Vector2(round(self.velocity.x), round(self.velocity.y))

            forward_vector = pygame.math.Vector2(0, -1)
            self.rotation = relUnit.angle_to(forward_vector)

    def blowmeup(self, pieces):
        return


class Boss(Enemy):
    def __init__(self, number, size, pos):
        super().__init__(number, size, pos)
        self.og_image = pygame.transform.scale(self.image, (180, 180))
        self.image = self.og_image
        self.rect = self.image.get_rect(center=pos)

        self.lives = 100


class VarInfo(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.asteroidBugs = 0

        self.dataList = []

    def update(self):
        for data in self.dataList:
            screen.blit(data[0], (50, 50 * data[2]))

    def createitem(self, data, dataName):
        if len(self.dataList) < 7:
            newData = font.render(f"{dataName} {data = }", True, WHITE)
            self.dataList.append([newData, dataName, len(self.dataList) + 1])
        else:
            newData = font.render(f"{dataName} {data = }", True, WHITE)
            for element in self.dataList:
                if element[1] == dataName:
                    self.dataList[element[2]] = [newData, element[1], element[2]]


# SPRITES
allsprites = pygame.sprite.Group()
asteroidsprites = pygame.sprite.Group()
bulletsprites = pygame.sprite.Group()
playersprites = pygame.sprite.Group()
infosprites = pygame.sprite.Group()
torchSprite = pygame.sprite.Group()
visibleAsteroidSprites = pygame.sprite.Group()
powerupSprites = pygame.sprite.Group()

player = Player()
playersprites.add(player)
player.starterShip = True
player.moving = True

gun = Gun()

asteroid = Asteroid(1, [dynamicresize(60), dynamicresize(120)],
                    pygame.math.Vector2(random.randint(dynamicresize(10), WIDTH - dynamicresize(10)),
                                        random.randint(dynamicresize(10), HEIGHT - dynamicresize(10))))
asteroidsprites.add(asteroid)
allsprites.add(asteroid)

enemy = Enemy("enemy", [180, 190], pygame.math.Vector2(randompos()))
asteroidsprites.add(enemy)
allsprites.add(enemy)

missileTarget = list(asteroidsprites)[0]

torch = Torch()
torchSprite.add(torch)

hud = Hud()

while startMenu:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if preferences:
                if event.key == pygame.K_ESCAPE:
                    if startscreen == 1:
                        quit()
                        sys.exit()
                    else:
                        startscreen = 1
                elif event.key == pygame.K_RIGHT:
                    WIDTH *= 2
                    HEIGHT *= 2
                    MULTIPLIER *= 2
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                elif event.key == pygame.K_LEFT:
                    WIDTH //= 2
                    HEIGHT //= 2
                    MULTIPLIER //= 2
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
            else:
                if event.key == pygame.K_ESCAPE:
                    quit()
                    sys.exit()

    keys = pygame.key.get_pressed()
    mousepos = pygame.mouse.get_pos()

    if playMusic:
        intromusic()

    screen.fill(BLACK)

    # main menu
    if startscreen == 1:
        player.velocity = pygame.math.Vector2(-1, -3)
        player.angle = 30
        player.move(keys)
        screen.blit(player.image, player.rect)

        # title
        title = bold_font.render("welcome to Leroy in Space: Asteroids", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        # start button
        # button1Hitbox = pygame.Surface((130, 20))
        # button1Hitbox.fill(RED)
        # screen.blit(button1Hitbox, button1Hitbox.get_rect(center=((WIDTH // 2) - 200, 300)))
        if mousepos[0] in range((WIDTH // 2) - 265, (WIDTH // 2) - 135) and mousepos[1] in range(290, 310):
            button1 = bold_font.render("start game", True, WHITE)
            if pygame.mouse.get_pressed(3)[0]:
                run = True
                pygame.mixer.Channel(5).stop()
                startMenu = False
        else:
            button1 = font.render("start game", True, WHITE)
        screen.blit(button1, button1.get_rect(center=((WIDTH // 2) - 200, 300)))

        # settings button
        # button2Hitbox = pygame.Surface((100, 20))
        # button2Hitbox.fill(RED)
        # screen.blit(button2Hitbox, button2Hitbox.get_rect(center=(WIDTH // 2, 300)))
        if mousepos[0] in range((WIDTH // 2) - 50, (WIDTH // 2) + 50) and mousepos[1] in range(290, 310):
            button2 = bold_font.render("settings", True, WHITE)
            if pygame.mouse.get_pressed(3)[0]:
                startscreen = 2
        else:
            button2 = font.render("settings", True, WHITE)
        screen.blit(button2, button2.get_rect(center=(WIDTH // 2, 300)))

        # controls button
        # button3Hitbox = pygame.Surface((100, 20))
        # button3Hitbox.fill(RED)
        # screen.blit(button3Hitbox, button3Hitbox.get_rect(center=((WIDTH // 2) + 200, 300)))
        if mousepos[0] in range((WIDTH // 2) + 150, (WIDTH // 2) + 250) and mousepos[1] in range(290, 310):
            button3 = bold_font.render("controls", True, WHITE)
            if pygame.mouse.get_pressed(3)[0]:
                startscreen = 3
        else:
            button3 = font.render("controls", True, WHITE)
        screen.blit(button3, button3.get_rect(center=((WIDTH // 2) + 200, 300)))

    # settings
    elif startscreen == 2:
        title2 = bold_font.render("settings", True, WHITE)
        screen.blit(title2, title2.get_rect(center=(WIDTH // 2, 150)))

        # resolution changer
        resolutionTitle = font.render("resolution", True, WHITE)
        resolution = font.render(f"{WIDTH} x {HEIGHT}", True, WHITE)
        screen.blit(resolutionTitle, resolutionTitle.get_rect(center=(WIDTH // 2, 260)))
        screen.blit(resolution, resolution.get_rect(center=(WIDTH // 2, 300)))

        decrease_res = pygame.draw.polygon(screen, WHITE, [((WIDTH // 2) - 100, 300), ((WIDTH // 2) - 80, 310),
                                                           ((WIDTH // 2) - 80, 290)])
        increase_res = pygame.draw.polygon(screen, WHITE, [((WIDTH // 2) + 100, 300), ((WIDTH // 2) + 80, 310),
                                                           ((WIDTH // 2) + 80, 290)])

        if mousepos[0] in range(decrease_res.left, decrease_res.right) and mousepos[1] in range(decrease_res.top,
                                                                                                decrease_res.bottom):
            if pygame.mouse.get_pressed(3)[0]:
                WIDTH //= 2
                HEIGHT //= 2

                json_data = {
                    "WIDTH": WIDTH,
                    "HEIGHT": HEIGHT,
                    "MULTIPLIER": MULTIPLIER,
                    "HIGHSCORE": HIGHSCORE
                }

                with open('data.json', 'w') as outf:
                    json.dump(json_data, outf)

                screen = pygame.display.set_mode((WIDTH, HEIGHT))
        elif mousepos[0] in range(increase_res.left, increase_res.right) and mousepos[1] in range(increase_res.top,
                                                                                                  increase_res.bottom):
            if pygame.mouse.get_pressed(3)[0]:
                WIDTH *= 2
                HEIGHT *= 2

                json_data = {
                    "WIDTH": WIDTH,
                    "HEIGHT": HEIGHT,
                    "MULTIPLIER": MULTIPLIER,
                    "HIGHSCORE": HIGHSCORE
                }

                with open('data.json', 'w') as outf:
                    json.dump(json_data, outf)

                screen = pygame.display.set_mode((WIDTH, HEIGHT))

        # music toggle
        # musicHitbox = pygame.Surface((160, 30))
        # musicHitbox.fill(RED)
        # screen.blit(musicHitbox, musicHitbox.get_rect(center=((WIDTH // 2), 380)))
        if mousepos[0] in range((WIDTH // 2) - 80, (WIDTH // 2) + 80) and mousepos[1] in range(365, 395):
            if playMusic:
                musicToggle = bold_font.render("music: on", True, WHITE)
                if pygame.mouse.get_pressed(3)[0]:
                    playMusic = False
            else:
                musicToggle = bold_font.render("music: off", True, WHITE)
                if pygame.mouse.get_pressed(3)[0]:
                    playMusic = True
        else:
            if playMusic:
                musicToggle = font.render("music: on", True, WHITE)
            else:
                musicToggle = font.render("music: off", True, WHITE)
        screen.blit(musicToggle, musicToggle.get_rect(center=(WIDTH // 2, 380)))

        # input toggle
        # inputTypeHitbox = pygame.Surface((200, 30))
        # inputTypeHitbox.fill(RED)
        # screen.blit(inputTypeHitbox, inputTypeHitbox.get_rect(center=(WIDTH // 2, 460)))
        if len(joysticks) > 0:
            if mousepos[0] in range((WIDTH // 2) - 100, (WIDTH // 2) + 100) and mousepos[1] in range(435, 475):
                if inputType == 1:
                    inputToggle = bold_font.render("input: keyboard", True, WHITE)
                else:
                    inputToggle = bold_font.render("input: joystick", True, WHITE)

                if pygame.mouse.get_pressed(3)[0]:
                    inputType = -inputType
            else:
                if inputType == 1:
                    inputToggle = font.render("input: keyboard", True, WHITE)
                else:
                    inputToggle = font.render("input: joystick", True, WHITE)
        else:
            inputToggle = font.render("input: keyboard", True, DARK_GREY)
        screen.blit(inputToggle, inputToggle.get_rect(center=(WIDTH // 2, 460)))

        # exit button
        # exitButtonHitbox = pygame.Surface((60, 20))
        # exitButtonHitbox.fill(RED)
        # screen.blit(exitButtonHitbox, exitButtonHitbox.get_rect(center=(WIDTH // 2, 800)))
        if mousepos[0] in range((WIDTH // 2) - 30, (WIDTH // 2) + 30) and mousepos[1] in range(790, 810):
            exitButton = bold_font.render("exit", True, WHITE)
            if pygame.mouse.get_pressed(3)[0]:
                startscreen = 1
        else:
            exitButton = font.render("exit", True, WHITE)
        screen.blit(exitButton, exitButton.get_rect(center=(WIDTH // 2, 800)))

    # controls
    elif startscreen == 3:
        movement = bold_font.render("movement:", True, WHITE)
        screen.blit(movement, movement.get_rect(center=(WIDTH // 2, 200)))

        forward = font.render("forwards: W", True, WHITE)
        backward = font.render("backwards: S", True, WHITE)
        rleft = font.render("rotate left: A", True, WHITE)
        rright = font.render("rotate right: D", True, WHITE)

        screen.blit(forward, forward.get_rect(center=(WIDTH // 2, 250)))
        screen.blit(backward, backward.get_rect(center=(WIDTH // 2, 300)))
        screen.blit(rleft, rleft.get_rect(center=(WIDTH // 2, 350)))
        screen.blit(rright, rright.get_rect(center=(WIDTH // 2, 400)))

        weapons = bold_font.render("weapons:", True, WHITE)
        screen.blit(weapons, weapons.get_rect(center=(WIDTH // 2, 500)))

        shootbutton = font.render("shoot: ENTER", True, WHITE)
        actpow = font.render("activate powerup: \\", True, WHITE)

        screen.blit(shootbutton, shootbutton.get_rect(center=(WIDTH // 2, 550)))
        screen.blit(actpow, actpow.get_rect(center=(WIDTH // 2, 600)))

        if mousepos[0] in range(WIDTH // 2 - 45, WIDTH // 2 + 45) and mousepos[1] in range(780, 820):
            exitbutton = bold_font.render("exit", True, WHITE)
            if pygame.mouse.get_pressed(3)[0]:
                startscreen = 1
        else:
            exitbutton = font.render("exit", True, WHITE)
        screen.blit(exitbutton, exitbutton.get_rect(center=(WIDTH // 2, 800)))

    pygame.display.update()
    clock.tick(FPS)

player.kill()
player = Player()
playersprites.add(player)

# GAME LOOP
while run:
    level, asteroidCount, play = gameloop(play)
