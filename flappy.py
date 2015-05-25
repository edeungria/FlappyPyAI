from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *


FPS = 30
SCREENWIDTH  = 288
SCREENHEIGHT = 512
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird - Alec's AI
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


def main():
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select player sprites
        #randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player1'] = (
            pygame.image.load(PLAYERS_LIST[0][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[0][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[0][2]).convert_alpha(),
        )
        
        IMAGES['player2'] = (
            pygame.image.load(PLAYERS_LIST[1][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[1][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[1][2]).convert_alpha(),
        )

        IMAGES['player3'] = (
            pygame.image.load(PLAYERS_LIST[2][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[2][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[2][2]).convert_alpha(),
        )
        
        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hitmask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player1'] = (
            getHitmask(IMAGES['player1'][0]),
            getHitmask(IMAGES['player1'][1]),
            getHitmask(IMAGES['player1'][2]),
        )

        HITMASKS['player2'] = (
            getHitmask(IMAGES['player2'][0]),
            getHitmask(IMAGES['player2'][1]),
            getHitmask(IMAGES['player2'][2]),
        )

        HITMASKS['player3'] = (
            getHitmask(IMAGES['player3'][0]),
            getHitmask(IMAGES['player3'][1]),
            getHitmask(IMAGES['player3'][2]),
        )        

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        print "GAME OVER"
        print "Player 1 Score:", crashInfo['score1']
        print "Player 2 Score:", crashInfo['score2']
        print "Player 3 Score:", crashInfo['score3']        
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    player1Index = 0
    player1IndexGen = cycle([0, 1, 2, 1])
    player2Index = 0
    player2IndexGen = cycle([0, 1, 2, 1])
    player3Index = 0
    player3IndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    player1x = int(SCREENWIDTH * 0.2)
    player1y = int((SCREENHEIGHT - IMAGES['player1'][0].get_height()) / 2)

    player2x = int(SCREENWIDTH * 0.2)
    player2y = int((SCREENHEIGHT - IMAGES['player1'][0].get_height()) / 2) + 15

    player3x = int(SCREENWIDTH * 0.2)
    player3y = int((SCREENHEIGHT - IMAGES['player1'][0].get_height()) / 2) - 15

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    player1ShmVals = {'val': 0, 'dir': 1}
    player2ShmVals = {'val': 0, 'dir': 1}
    player3ShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                return {
                    'player1y': player1y + player1ShmVals['val'],
                    'basex': basex,
                    'player1IndexGen': player1IndexGen,
                    'player2y': player2y + player2ShmVals['val'],
                    'player2IndexGen': player2IndexGen,
                    'player3y': player3y + player3ShmVals['val'],
                    'player3IndexGen': player3IndexGen,
                }

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            player1Index = player1IndexGen.next()
            player2Index = player2IndexGen.next()
            player3Index = player3IndexGen.next()
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(player1ShmVals)
        playerShm(player2ShmVals)
        playerShm(player3ShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player1'][player1Index],
                    (player1x, player1y + player1ShmVals['val']))
        SCREEN.blit(IMAGES['player2'][player2Index],
                    (player2x, player2y + player2ShmVals['val']))
        SCREEN.blit(IMAGES['player3'][player3Index],
                    (player3x, player3y + player3ShmVals['val']))        
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    score1 = score2 = score3 = 0
    player1Index = player2Index = player3Index = loopIter = 0
    dead1 = dead2 = dead3 = False
    player1IndexGen = movementInfo['player1IndexGen']
    player2IndexGen = movementInfo['player2IndexGen']
    player3IndexGen = movementInfo['player3IndexGen']
    player1x, player1y = int(SCREENWIDTH * 0.2), movementInfo['player1y']
    player2x, player2y = int(SCREENWIDTH * 0.2), movementInfo['player2y']
    player3x, player3y = int(SCREENWIDTH * 0.2), movementInfo['player3y']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    # each player's velocity, max velocity, downward accleration, accleration on flap
    player1VelY    =  -9   # player's velocity along Y, default same as playerFlapped
    player1MaxVelY =  10   # max vel along Y, max descend speed
    player1MinVelY =  -8   # min vel along Y, max ascend speed
    player1AccY    =   1   # players downward accleration
    player1FlapAcc =  -9   # players speed on flapping
    player1Flapped = False # True when player flaps

    player2VelY    =  -9   # player's velocity along Y, default same as playerFlapped
    player2MaxVelY =  10   # max vel along Y, max descend speed
    player2MinVelY =  -8   # min vel along Y, max ascend speed
    player2AccY    =   1   # players downward accleration
    player2FlapAcc =  -9   # players speed on flapping
    player2Flapped = False # True when player flaps

    player3VelY    =  -9   # player's velocity along Y, default same as playerFlapped
    player3MaxVelY =  10   # max vel along Y, max descend speed
    player3MinVelY =  -8   # min vel along Y, max ascend speed
    player3AccY    =   1   # players downward accleration
    player3FlapAcc =  -9   # players speed on flapping
    player3Flapped = False # True when player flaps

    while True:
        for event in pygame.event.get():
            # user quits the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # press space or up to flap
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player1y > -2 * IMAGES['player1'][0].get_height():
                    player1VelY = player1FlapAcc
                    player1Flapped = True
                if player2y > -2 * IMAGES['player2'][0].get_height():
                    player2VelY = player2FlapAcc
                    player2Flapped = True               
                if player3y > -2 * IMAGES['player3'][0].get_height():
                    player3VelY = player3FlapAcc
                    player3Flapped = True 

        # check for crash here
        if not dead1:
            crashTest1 = checkCrash({'x': player1x, 'y': player1y, 'index': player1Index, 'playerNum': 1},
                                   upperPipes, lowerPipes)
            dead1 = crashTest1[0]
            if dead1:
                SOUNDS['hit'].play()
        if not dead2:
            crashTest2 = checkCrash({'x': player2x, 'y': player2y, 'index': player2Index, 'playerNum': 2},
                                   upperPipes, lowerPipes)
            dead2 = crashTest2[0]
            if dead2:
                SOUNDS['hit'].play()
        if not dead3:
            crashTest3 = checkCrash({'x': player3x, 'y': player3y, 'index': player3Index, 'playerNum': 3},
                                   upperPipes, lowerPipes)
            dead3 = crashTest3[0]
            if dead3:
                SOUNDS['hit'].play()

    ############################# PLAYER1 AI
        if not dead1:
            # get target position
            average1Height = average2Height = 0
            
            if player1x < lowerPipes[0]['x'] + IMAGES['pipe'][0].get_width():
                average1Height = lowerPipes[0]['y'] - PIPEGAPSIZE/2       
            else:
                average1Height = lowerPipes[1]['y'] - PIPEGAPSIZE/2
                
    #        for lPipe in lowerPipes:
    #            midpoint = (lPipe['y'] - PIPEGAPSIZE/2)
    #            if playerx < lPipe['x']:
    #                averageHeight = (averageHeight + midpoint)/2

            target = SCREENHEIGHT/2 # target middle if no pipes are around
            if average1Height > 0:
                target = average1Height

            # decide whether or not to flap
            if player1y > target:
                player1VelY = player1FlapAcc
                player1Flapped = True

    #############################

        if dead1 and dead2 and dead3:
            return {
                'y1': player1y,
                'groundCrash1': crashTest1[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score1': score1,
                'player1VelY': player1VelY,
                'y2': player2y,
                'groundCrash2': crashTest2[1],
                'score2': score2,
                'player2VelY': player2VelY,
                'y3': player3y,
                'groundCrash3': crashTest3[1],
                'score3': score3,
                'player3VelY': player3VelY,
            }

        # check for score
        player1MidPos = player1x + IMAGES['player1'][0].get_width() / 2
        player2MidPos = player2x + IMAGES['player2'][0].get_width() / 2
        player3MidPos = player3x + IMAGES['player3'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= player1MidPos < pipeMidPos + 4 and not dead1:
                score1 += 1
                SOUNDS['point'].play()
            if pipeMidPos <= player2MidPos < pipeMidPos + 4 and not dead2:
                score2 += 1
                SOUNDS['point'].play()            
            if pipeMidPos <= player3MidPos < pipeMidPos + 4 and not dead3:
                score3 += 1
                SOUNDS['point'].play() 

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            player1Index = player1IndexGen.next()
            player2Index = player2IndexGen.next()
            player3Index = player3IndexGen.next()
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # player 1's movement
        if not dead1:
            if player1VelY < player1MaxVelY and not player1Flapped:
                player1VelY += player1AccY
            if player1Flapped:
                player1Flapped = False
            player1Height = IMAGES['player1'][player1Index].get_height()
            player1y += min(player1VelY, BASEY - player1y - player1Height)

        # player 2's movement
        if not dead2:
            if player2VelY < player2MaxVelY and not player2Flapped:
                player2VelY += player2AccY
            if player2Flapped:
                player2Flapped = False
            player2Height = IMAGES['player2'][player2Index].get_height()
            player2y += min(player2VelY, BASEY - player2y - player2Height)

        # player 3's movement
        if not dead3:
            if player3VelY < player3MaxVelY and not player3Flapped:
                player3VelY += player3AccY
            if player3Flapped:
                player3Flapped = False
            player3Height = IMAGES['player3'][player3Index].get_height()
            player3y += min(player3VelY, BASEY - player3y - player3Height)        

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        # print score so player overlaps the score
        if score1 > score2 and score1 > score3:
            showScore(score1)
        elif score2 > score1 and score2 > score3:
            showScore(score2)
        else:
            showScore(score3)

        # check which birds to display
        if not dead1 and not dead2 and not dead3:
            SCREEN.blit(IMAGES['player1'][player1Index], (player1x, player1y))
            SCREEN.blit(IMAGES['player2'][player2Index], (player2x, player2y))
            SCREEN.blit(IMAGES['player3'][player3Index], (player3x, player3y))
        elif not dead1 and not dead2:
            SCREEN.blit(IMAGES['player1'][player1Index], (player1x, player1y))
            SCREEN.blit(IMAGES['player2'][player2Index], (player2x, player2y))
        elif not dead2 and not dead3:
            SCREEN.blit(IMAGES['player2'][player2Index], (player2x, player2y))
            SCREEN.blit(IMAGES['player3'][player3Index], (player3x, player3y))
        elif not dead1 and not dead3:
            SCREEN.blit(IMAGES['player1'][player1Index], (player1x, player1y))
            SCREEN.blit(IMAGES['player3'][player3Index], (player3x, player3y))        
        elif not dead1:
            SCREEN.blit(IMAGES['player1'][player1Index], (player1x, player1y))
        elif not dead2:
            SCREEN.blit(IMAGES['player2'][player2Index], (player2x, player2y))        
        elif not dead3:
            SCREEN.blit(IMAGES['player3'][player3Index], (player3x, player3y))
            
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showGameOverScreen(crashInfo):
    """crashes the player down and shows gameover image"""
    if crashInfo['score1'] > crashInfo['score2'] and crashInfo['score1'] > crashInfo['score3']:
        score = crashInfo['score1']
        playerx = SCREENWIDTH * 0.2
        playery = crashInfo['y1']
        playerHeight = IMAGES['player1'][0].get_height()
        playerVelY = crashInfo['player1VelY']
        playerAccY = 2
    elif crashInfo['score2'] > crashInfo['score1'] and crashInfo['score2'] > crashInfo['score3']:
        score = crashInfo['score2']
        playerx = SCREENWIDTH * 0.2
        playery = crashInfo['y2']
        playerHeight = IMAGES['player2'][0].get_height()
        playerVelY = crashInfo['player2VelY']
        playerAccY = 2
    else:
        score = crashInfo['score3']
        playerx = SCREENWIDTH * 0.2
        playery = crashInfo['y3']
        playerHeight = IMAGES['player3'][0].get_height()
        playerVelY = crashInfo['player3VelY']
        playerAccY = 2    

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    if crashInfo['score1'] > crashInfo['score2'] and crashInfo['score1'] > crashInfo['score3']:
        if not crashInfo['groundCrash1']:
            SOUNDS['die'].play()
    elif crashInfo['score2'] > crashInfo['score1'] and crashInfo['score2'] > crashInfo['score3']:
        if not crashInfo['groundCrash2']:
            SOUNDS['die'].play()
    else:
        if not crashInfo['groundCrash3']:
            SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)
        if crashInfo['score1'] > crashInfo['score2'] and crashInfo['score1'] > crashInfo['score3']:
            SCREEN.blit(IMAGES['player1'][1], (playerx,playery))
        elif crashInfo['score2'] > crashInfo['score1'] and crashInfo['score2'] > crashInfo['score3']:
            SCREEN.blit(IMAGES['player2'][1], (playerx,playery))
        else:
            SCREEN.blit(IMAGES['player3'][1], (playerx,playery))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    if player['playerNum'] is 1:
        player['w'] = IMAGES['player1'][0].get_width()
        player['h'] = IMAGES['player1'][0].get_height()
    elif player['playerNum'] is 2:
        player['w'] = IMAGES['player2'][0].get_width()
        player['h'] = IMAGES['player2'][0].get_height()
    else:
        player['w'] = IMAGES['player3'][0].get_width()
        player['h'] = IMAGES['player3'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            if player['playerNum'] is 1:
                pHitMask = HITMASKS['player1'][pi]
            elif player['playerNum'] is 2: 
                pHitMask = HITMASKS['player2'][pi]
            else:
                pHitMask = HITMASKS['player3'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    main()
