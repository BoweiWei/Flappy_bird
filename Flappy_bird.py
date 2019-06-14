import random # For generating random numbers
import sys # We will use sys.exit to exit the program
import pygame
from pygame.locals import * # Basic pygame 
from itertools import cycle
#from PIL import Image

# Global Variables for the game
FPS = 30
SCREENWIDTH = 288
SCREENHEIGHT = 512
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYERS_LIST = (
    # red bird
    (
        'flappy_bird/redbird-upflap.png',
        'flappy_bird/redbird-midflap.png',
        'flappy_bird/redbird-downflap.png',
    ),
    # blue bird
    (
        'flappy_bird/bluebird-upflap.png',
        'flappy_bird/bluebird-midflap.png',
        'flappy_bird/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'flappy_bird/yellowbird-upflap.png',
        'flappy_bird/yellowbird-midflap.png',
        'flappy_bird/yellowbird-downflap.png',
    ),
)
BACKGROUND = (
    'flappy_bird/background-day.png',
    'flappy_bird/background-night.png',
)

PIPE = 'flappy_bird/pipe-green.png'

def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1

def welcomeScreen():
    """
    Shows welcome images on the screen
    """

    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    loopIter = 0

    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'][0].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    baseShift = GAME_SPRITES['base'].get_width() - GAME_SPRITES['background'].get_width()
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            if event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
                GAME_SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }
                

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))    
        SCREEN.blit(GAME_SPRITES['player'][playerIndex], (playerx, playery + playerShmVals['val']))    
        SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))    
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY)) 
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def mainGame(movementInfo):
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    #basex = 0
    loopIter = 0
    playerIndex = 0
    playerIndexGen = movementInfo['playerIndexGen']
    basex = movementInfo['basex']
    baseShift = GAME_SPRITES['base'].get_width() - GAME_SPRITES['background'].get_width()

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1
    playerRot     =  45   # player's rotation
    playerVelRot  =   3   # angular speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAccv = -8 # velocity while flapping
    playerFlapped = False # It is true only when the bird is flapping


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * GAME_SPRITES['player'][0].get_height():
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()


        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
        if crashTest[0]:
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        #check for score
        playerMidPos = playerx + GAME_SPRITES['player'][0].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Your score is {score}") 
                GAME_SOUNDS['point'].play()

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
            playerRot = 45

        playerHeight = GAME_SPRITES['player'][0].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # move pipes to the left
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0<upperPipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))

        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        #SCREEN.blit(GAME_SPRITES['player'][0], (playerx, playery))
        # myDigits = [int(x) for x in list(str(score))]
        # width = 0
        # for digit in myDigits:
        #     width += GAME_SPRITES['numbers'][digit].get_width()
        # Xoffset = (SCREENWIDTH - width)/2

        # for digit in myDigits:
        #     SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
        #     Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        showScore(score)

        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        
        playerSurface = pygame.transform.rotate(GAME_SPRITES['player'][playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += GAME_SPRITES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += GAME_SPRITES['numbers'][digit].get_width()

def showScore_small(score, pos):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += GAME_SPRITES['numbers_small'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2 + 40

    for digit in scoreDigits:
        SCREEN.blit(GAME_SPRITES['numbers_small'][digit], (Xoffset, pos))
        Xoffset += GAME_SPRITES['numbers_small'][digit].get_width()


def isCollide(playerx, playery, upperPipes, lowerPipes):
    #playerx = player['w'] = GAME_SPRITES['player'][0]
    if playery> GROUNDY - 25  or playery<0:
        GAME_SOUNDS['hit'].play()
        return [True, True]
    
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return [True, False]

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'][0].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return [True, False]

    return [False, False]

def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe
    ]
    return pipe

def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = GAME_SPRITES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    GAME_SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        GAME_SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= GROUNDY - 1:
                    return

        # player y shift
        if playery + playerHeight < GROUNDY - 1:
            playery += min(playerVelY, GROUNDY - playery - playerHeight)
            crashInfo['y'] = playery
        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(GAME_SPRITES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        showScore(score)

        playerSurface = pygame.transform.rotate(GAME_SPRITES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))
        SCREEN.blit(GAME_SPRITES['gameover'], (50, 100))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def RankingScreen(crashInfo):
    """show the score, the historical highest score and save it as a notebook"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = GAME_SPRITES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    try:
        new_score = open("flappy_bird/newscore.txt", "r+")
        n_score = int(new_score.read())
        #print(n_score)
    except FileNotFoundError:
        new_score = open("flappy_bird/newscore.txt", "w+")
        new_score.write("0")
        n_score = 0

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= GROUNDY - 1:
                    return

        #if playerRot > -90:
        #    playerRot -= playerVelRot

        #draw sprites
        SCREEN.blit(GAME_SPRITES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        playerSurface = pygame.transform.rotate(GAME_SPRITES['player'][1], -92)
        #playerSurface = GAME_SPRITES['player'][1].rotate(playerRot)
        SCREEN.blit(playerSurface, (playerx, playery))

        
        showScore(score)


        SCREEN.blit(GAME_SPRITES['gameover'], (50, 100))
        SCREEN.blit(GAME_SPRITES['scoreboard'], (90, 220))
        #print(score, n_score)
        sub = n_score
        if score > sub:
            SCREEN.blit(GAME_SPRITES['new'], (150, 230))
        


        showScore_small(score, 238)
        showScore_small(max(score, n_score), 258)

        if score < 1:
            pass
        elif score < 2:
            SCREEN.blit(GAME_SPRITES['bronzemedal'], (103, 243))
        elif score < 3:
            SCREEN.blit(GAME_SPRITES['silvermedal'], (103, 243))
        else:
            SCREEN.blit(GAME_SPRITES['goldmedal'], (103, 243))


        

        FPSCLOCK.tick(FPS)
        pygame.display.update()

    
    n_score = max(score, n_score)
    with open('flappy_bird/newscore.txt', 'w') as filetowrite:
        filetowrite.write(str(n_score))
        filetowrite.close()


if __name__ == "__main__":
    # This will be the main point from where our game will start
    #global SCREEN, FPSCLOCK
    pygame.init() # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    #pygame.display.set_caption('Flappy Bird')

    

    pygame.display.set_caption('Flappy Bird by Bovey Wayne')
    GAME_SPRITES['numbers'] = ( 
        pygame.image.load('flappy_bird/0.png').convert_alpha(),
        pygame.image.load('flappy_bird/1.png').convert_alpha(),
        pygame.image.load('flappy_bird/2.png').convert_alpha(),
        pygame.image.load('flappy_bird/3.png').convert_alpha(),
        pygame.image.load('flappy_bird/4.png').convert_alpha(),
        pygame.image.load('flappy_bird/5.png').convert_alpha(),
        pygame.image.load('flappy_bird/6.png').convert_alpha(),
        pygame.image.load('flappy_bird/7.png').convert_alpha(),
        pygame.image.load('flappy_bird/8.png').convert_alpha(),
        pygame.image.load('flappy_bird/9.png').convert_alpha(),
    )

    GAME_SPRITES['numbers_small'] = ( 
        pygame.transform.scale(pygame.image.load('flappy_bird/0.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/1.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/2.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/3.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/4.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/5.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/6.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/7.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/8.png').convert_alpha(), (12, 18)),
        pygame.transform.scale(pygame.image.load('flappy_bird/9.png').convert_alpha(), (12, 18)),
    )

    GAME_SPRITES['message'] =pygame.image.load('flappy_bird/message.png').convert_alpha()
    GAME_SPRITES['base'] =pygame.image.load('flappy_bird/base.png').convert_alpha()
    GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), 
    pygame.image.load(PIPE).convert_alpha()
    )
    GAME_SPRITES['gameover'] = pygame.image.load('flappy_bird/gameover.png').convert_alpha()
    GAME_SPRITES['goldmedal'] = pygame.image.load('flappy_bird/goldmedal.png').convert_alpha()
    GAME_SPRITES['silvermedal'] = pygame.image.load('flappy_bird/silvermedal.png').convert_alpha()
    GAME_SPRITES['bronzemedal'] = pygame.image.load('flappy_bird/bronzemedal.png').convert_alpha()
    GAME_SPRITES['scoreboard'] = pygame.image.load('flappy_bird/scoreboard.png').convert_alpha()
    GAME_SPRITES['new'] = pygame.image.load('flappy_bird/new.png').convert_alpha()

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('flappy_bird/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('flappy_bird/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('flappy_bird/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('flappy_bird/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('flappy_bird/wing.wav')

    

    while True:
        #welcomeScreen()
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        randBg = random.randint(0, len(BACKGROUND) - 1)
        GAME_SPRITES['background'] = pygame.image.load(BACKGROUND[randBg]).convert()
        GAME_SPRITES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )
        movementInfo = welcomeScreen() # Shows welcome screen to the user until he presses a button
        crashInfo = mainGame(movementInfo) # This is the main game function
        showGameOverScreen(crashInfo)
        RankingScreen(crashInfo)









