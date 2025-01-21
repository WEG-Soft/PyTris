import pygame
import random

pygame.init()

TILE_SIZE = 32
COLS = 24
ROWS = 20
TTL_TILES = COLS * ROWS
SCREEN_WIDTH = TILE_SIZE * COLS
SCREEN_HEIGHT = TILE_SIZE * ROWS

WINDOW = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
W_ICON = pygame.image.load('icon.png')
pygame.display.set_caption("Tetris",'icon.png')
pygame.display.set_icon(W_ICON)

CLOCK = pygame.time.Clock()
FPS = 60

BG_COLOR = (0,0,200)
WHITE = (255,255,255)
BLACK = (0,0,0)

COLORS = [
    (255,255,0),
    (0,255,255),
    (153,0,255),
    (255,153,0),
    (0,0,255),
    (0,255,0),
    (255,0,0)
]

SHAPES = [
    [
        [1,1],
        [1,1]
        
    ],
    [
        [1],
        [1],
        [1],
        [1]
    ],
    [
        [1,0],
        [1,1],
        [1,0]
    ],
    [
        [1,1],
        [0,1],
        [0,1]
    ],
    [
        [0,1],
        [0,1],
        [1,1]
    ],
    [
        [1,0],
        [1,1],
        [0,1]
    ],
    [
        [0,1],
        [1,1],
        [1,0]
    ]
]

DEF_FONT = '8bit-font.ttf'
FONT_SIZE = 32
FONT_SPACING = 0
FONT = pygame.font.Font(DEF_FONT,FONT_SIZE//2)

print(FONT_SIZE)

class Scribe:
        def __init__(self):
            self.lines = []
        def print(self,txt:str):
            self.lines.append(txt)
        def render(self):
            global FONT_SIZE
            for(i,str) in enumerate(self.lines):
                text = FONT.render(str,False,WHITE)
                textrect= text.get_rect()
                WINDOW.blit(text,(4,((FONT_SIZE )*i)+FONT_SPACING),textrect) 
            self.lines = []
        def write(self,text:str,pos:tuple[int],size:int=FONT_SIZE,color=WHITE):
            global DEF_FONT
            nfont = FONT
            if size != FONT_SIZE:
                nfont = pygame.font.Font(DEF_FONT,size)
            rendtxt = nfont.render(text,False,color)
            recttxt = rendtxt.get_rect()
            WINDOW.blit(rendtxt,(pos[0],pos[1]),recttxt)
        def write_ml(self,text:str,pos:tuple[int],size:int=FONT_SIZE,color=WHITE):
            ftxt = text.split("\n")
            for (l,line) in enumerate(ftxt):
                rendtxt = FONT.render(line,False,color)
                recttxt = rendtxt.get_rect()
                WINDOW.blit(rendtxt,(pos[0],pos[1] + (l*size)),recttxt)

def ceil(x):
    return -int(-x // 1)

pygame.mixer.init(channels=1)

SFX_CHANNEL = pygame.mixer.Channel(0)

SFX_MENU = pygame.mixer.Sound('sounds/menu.wav')
SFX_ROTATE = pygame.mixer.Sound('sounds/rotate_piece.wav')
SFX_MOVE = pygame.mixer.Sound('sounds/move_piece.wav')
SFX_LAND = pygame.mixer.Sound('sounds/piece_landed.wav')
SFX_CLEAR = pygame.mixer.Sound('sounds/line_clear.wav')
SFX_TETRIS = pygame.mixer.Sound('sounds/tetris_clear.wav')
SFX_SPEED = pygame.mixer.Sound('sounds/speed_up.wav')

BOARD = [[0 for _ in range(10)] for _ in range(20)]

def calculate_score():
    global BLOCKS
    global PIECES_PLAYED
    global SCORE
    global CLEARS
    global SPEED
    
    PIECES_PLAYED = sum(BLOCKS)
    SCORE = 0
    SCORE += PIECES_PLAYED * 4
    SCORE += 1000 * (SPEED - 1)
    for (i,v) in enumerate(CLEARS):
        SCORE += v * (32 * (2**i))


def checklines():
    global SPEEDMULT
    global SPEED
    global MRATE
    global LINES_CLEARED
    global PIECES_PLAYED
    global CLEARS
    
    rows_to_clear = []
    
    for r in range(len(BOARD)):
        if all(v > 0 for v in BOARD[r]):
            rows_to_clear.append(r)

    for r in rows_to_clear:
        for i in range(r, 0, -1):
            BOARD[i] = BOARD[i - 1][:]
        BOARD[0] = [0] * len(BOARD[0])
    
    if len(rows_to_clear) > 0:
        CLEARS[len(rows_to_clear)-1] += 1
        LINES_CLEARED += len(rows_to_clear)
        SFX_CHANNEL.play(SFX_CLEAR)
        if len(rows_to_clear) == 4:
            SFX_CHANNEL.play(SFX_TETRIS)
        cspeed = SPEED
        SPEED = int(LINES_CLEARED / 2) + 1
        if SPEED != cspeed:
            SFX_CHANNEL.queue(SFX_SPEED)
        MRATE = (FPS / 2) * (SPEEDMULT ** SPEED)
    calculate_score()
        
def comp2brd(matrix, x, y):
    return all(
        0 <= x + tx < 10 and y + ty < 20 and (v == 0 or BOARD[y + ty][x + tx] == 0)
        for ty, r in enumerate(matrix) for tx, v in enumerate(r)
    )

def draw_bg():
    global GAME_OVER
    global sh
    
    WINDOW.fill(BLACK)
    WINDOW.fill(BG_COLOR,(0,0,TILE_SIZE*2,SCREEN_HEIGHT))
    pygame.draw.rect(WINDOW,WHITE,(TILE_SIZE*2-4,0,4,SCREEN_HEIGHT))
    WINDOW.fill(BG_COLOR,(TILE_SIZE*12,0,SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.draw.rect(WINDOW,WHITE,(TILE_SIZE*12,0,4,SCREEN_HEIGHT))
    for i in range(200):
        b = TILE_SIZE * 2
        r = int(i / 10)
        c = i % 10
        rect = (b + (c*TILE_SIZE),r * TILE_SIZE,TILE_SIZE,TILE_SIZE)
        
        if BOARD[r][c] > 0:
            pygame.draw.rect(WINDOW,COLORS[BOARD[r][c]-1],rect)
            pygame.draw.rect(WINDOW,BLACK,rect,1)
        else:
            if (sh.x <= c <= sh.x + len(sh.shape[0])-1 and r > sh.y) and not GAME_OVER:
                pygame.draw.rect(WINDOW,(30,30,30),rect)
            pygame.draw.rect(WINDOW,(40,40,40),rect,1)
            
            
def draw_shape(x,y,type:int,matrix:list[list[int]],size=1):
    T_S = TILE_SIZE * size
    for (yi,r) in enumerate(matrix):
        for (xi,v) in enumerate(r):
            if v > 0:
                rect = (x + (xi*T_S),y + (yi*T_S),T_S,T_S)
                pygame.draw.rect(WINDOW,COLORS[type],rect)
                pygame.draw.rect(WINDOW,BLACK,rect,1)

def render_field():
    global GAME_OVER
    global scribe
    global sh
    draw_bg()
    
    
    pygame.draw.rect(WINDOW,BLACK,(TILE_SIZE*13-8,TILE_SIZE-8,TILE_SIZE*4,TILE_SIZE*6))
    for i in range(8):
        r = int(i/2)
        c = i % 2
        pygame.draw.rect(WINDOW,(40,40,40),(TILE_SIZE * 13.5 + c * TILE_SIZE,TILE_SIZE*2 + r * TILE_SIZE,TILE_SIZE,TILE_SIZE),1)
    draw_shape(TILE_SIZE * 13.5,TILE_SIZE*2,NEXTSHAPE,SHAPES[NEXTSHAPE])
    scribe.write("NEXT:",(TILE_SIZE * 13,TILE_SIZE))
    
    pygame.draw.rect(WINDOW,BLACK,(TILE_SIZE*13 - 8,TILE_SIZE*7.5 - 8,TILE_SIZE*4,TILE_SIZE*2))
    scribe.write_ml(f'LINES:\n{LINES_CLEARED:03d}',(TILE_SIZE * 13,TILE_SIZE * 7.5))
    
    pygame.draw.rect(WINDOW,BLACK,(TILE_SIZE*13 - 8,TILE_SIZE*10 - 8,TILE_SIZE*4,TILE_SIZE*2))    
    scribe.write_ml(f'SPEED:\n{SPEED}',(TILE_SIZE * 13,TILE_SIZE * 10))
    
    pygame.draw.rect(WINDOW,BLACK,(TILE_SIZE*13 - 8,TILE_SIZE*12.5 - 8,TILE_SIZE*4,TILE_SIZE*3))
    scribe.write_ml(f'PIECES\nPLAYED:\n{PIECES_PLAYED:04d}',(TILE_SIZE * 13,TILE_SIZE * 12.5))
    
    pygame.draw.rect(WINDOW,BLACK,(TILE_SIZE*13 - 8,TILE_SIZE*16 - 8,TILE_SIZE*4,TILE_SIZE*3))
    scribe.write_ml(f'TOTAL\nSCORE:\n{SCORE:05d}',(TILE_SIZE * 13,TILE_SIZE * 16))
    
    pygame.draw.rect(WINDOW,BLACK,(TILE_SIZE*18-8,TILE_SIZE-8,TILE_SIZE*6,TILE_SIZE*16))
    scribe.write_ml(f'CLEARS:\nSINGLE: {CLEARS[0]:02d}\nDOUBLE: {CLEARS[1]:02d}\nTRIPLE: {CLEARS[2]:02d}\nTETRIS: {CLEARS[3]:02d}',(TILE_SIZE*18,TILE_SIZE))
    
    scribe.write_ml("SHAPE\nCOUNTS:",(TILE_SIZE*18,TILE_SIZE*7))
    SH_S = 0.5
    draw_shape(TILE_SIZE * 18,TILE_SIZE*9,0,SHAPES[0],SH_S)
    scribe.write(f'{BLOCKS[0]:02d}',(TILE_SIZE*19.5,TILE_SIZE*9.25))
    draw_shape(TILE_SIZE * 18,TILE_SIZE*10.5,1,SHAPES[1],SH_S)
    scribe.write(f'{BLOCKS[1]:02d}',(TILE_SIZE*19.5,TILE_SIZE*11.25))
    draw_shape(TILE_SIZE * 18,TILE_SIZE*13,2,SHAPES[2],SH_S)
    scribe.write(f'{BLOCKS[2]:02d}',(TILE_SIZE*19.5,TILE_SIZE*13.5))
    draw_shape(TILE_SIZE * 18,TILE_SIZE*15,3,SHAPES[3],SH_S)
    scribe.write(f'{BLOCKS[3]:02d}',(TILE_SIZE*19.5,TILE_SIZE*15.5))
    
    draw_shape(TILE_SIZE * 21,TILE_SIZE*9,4,SHAPES[4],SH_S)
    scribe.write(f'{BLOCKS[4]:02d}',(TILE_SIZE*22.5,TILE_SIZE*9.5))
    draw_shape(TILE_SIZE * 21,TILE_SIZE*11,5,SHAPES[5],SH_S)
    scribe.write(f'{BLOCKS[5]:02d}',(TILE_SIZE*22.5,TILE_SIZE*11.5))
    draw_shape(TILE_SIZE * 21,TILE_SIZE*13,6,SHAPES[6],SH_S)
    scribe.write(f'{BLOCKS[6]:02d}',(TILE_SIZE*22.5,TILE_SIZE*13.5))
    
    
    
    if GAME_OVER:
        pygame.draw.rect(WINDOW,BLACK,(TILE_SIZE*2,TILE_SIZE*16,TILE_SIZE*10,TILE_SIZE*4))
        pygame.draw.rect(WINDOW,WHITE,(TILE_SIZE*2-4,TILE_SIZE*16,TILE_SIZE*10+8,TILE_SIZE*4),4)
        scribe.write_ml("GAME OVER\nESC - QUIT\nSPACE - RETRY",(TILE_SIZE*3,TILE_SIZE*17))
    
    draw_shape(TILE_SIZE*2 + sh.x * TILE_SIZE ,sh.y * TILE_SIZE,sh.type,sh.shape)

class Shape:
    def __init__(self):
        self.type = 1
        self.shape = SHAPES[self.type]
        self.x = 4
        self.y = 0
    
    def set_off(self):
        self.lxo = 1
        self.rxo = 1
        self.byo = 1
        for i in range(len(self.shape)):
            if self.shape[i][0] != 0:
                self.lxo = 0
        for i in range(len(self.shape)):
            if self.shape[i][2] != 0:
                self.rxo = 0
        for i in range(len(self.shape[-1])):
            if self.shape[-1][i] != 0:
                self.byo = 0
            
    def mx(self,dx):
        nx = self.x + dx
        if comp2brd(self.shape, nx,self.y):
            self.x = nx
            SFX_MOVE.play()
    
    def my(self):
        global GAME_OVER
        global NEXTSHAPE
        global BLOCKS
        ny = self.y + 1
        if (not comp2brd(self.shape, self.x, ny)) or self.y + len(self.shape) >= 20:
            BLOCKS[self.type] += 1
            SFX_LAND.play()
            if self.y > 0 or self.x != 4 :
                for (ty, r) in enumerate(self.shape):
                    for (tx, v) in enumerate(r):
                        if v > 0:
                            BOARD[self.y + ty][self.x + tx] = self.type + 1
                checklines()
                self.__init__()
                self.set_shape(NEXTSHAPE)
                NEXTSHAPE = random.randint(0,6)
            else:
                GAME_OVER = True
            return True
        else:
            self.y += 1
            return False
    
    def rotate(self):
        nmat = [[0 for _ in range(len(self.shape))] for _ in range(len(self.shape[0]))]
        
        for i in range(len(self.shape)):
            for j in range(len(self.shape[0])):
                nmat[j][len(self.shape) - 1 - i] = self.shape[i][j]
        
        if comp2brd(nmat,self.x,self.y):
            self.shape = nmat
            SFX_ROTATE.play()
    
    def set_shape(self,s):
        self.type = s
        self.shape = SHAPES[self.type]

def wait_for_keys():
    global RUN
    while RUN and any(pygame.key.get_pressed()):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
                
def check_for_quit():
    global RUN
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN = False
        if keys[pygame.K_ESCAPE]:
            RUN = False

TITLE_TILES = (ROWS-2)*(COLS-2)
TITLE_BG = [random.randint(0,6) for _ in range(TITLE_TILES)]

sh = Shape()
sh.set_shape(random.randint(0,6))

scribe = Scribe()

PAUSING = False
TURNING = False
MOVING = False
SPACED = False

SCORE = 0
CLEARS = [0,0,0,0]
BLOCKS = [0,0,0,0,0,0,0]
LINES_CLEARED = 0
NEXTSHAPE = random.randint(0,6)
PIECES_PLAYED = 0

SPEED = 1
SPEEDMULT = 0.9
FRAME = 0
MFRAME = 0
MRATE = FPS / 2
MDELTA = MRATE

TITLE_SCREEN = True
GAME_OVER = False
PAUSED = False

RUN = True

while RUN:
    pygame.mixer.music.load('music/title.mp3')
    pygame.mixer.music.play(-1)
    
    while RUN and TITLE_SCREEN:
        check_for_quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
            SFX_MENU.play()
            TITLE_SCREEN = False
        WINDOW.fill(BG_COLOR)
        pygame.draw.rect(WINDOW,WHITE,(16,16,SCREEN_WIDTH-TILE_SIZE,SCREEN_HEIGHT-TILE_SIZE),16)
        
        for i in range(TITLE_TILES):
            r = int(i/(COLS-2))
            c = i % (COLS-2)
            pygame.draw.rect(WINDOW,COLORS[TITLE_BG[i]],(TILE_SIZE + TILE_SIZE * c,TILE_SIZE + TILE_SIZE * r,TILE_SIZE,TILE_SIZE))
        
        pygame.draw.rect(WINDOW,BLACK,(TILE_SIZE*5,TILE_SIZE*5,TILE_SIZE*14,TILE_SIZE*7))
        pygame.draw.rect(WINDOW,WHITE,(TILE_SIZE*5+4,TILE_SIZE*5+4,TILE_SIZE*14-8,TILE_SIZE*7-8),4)
        scribe.write("TETRIS",(TILE_SIZE*6,TILE_SIZE*6),FONT_SIZE * 2)
        scribe.write("python EDITION",(TILE_SIZE*8.5,TILE_SIZE*8))
        scribe.write("PRESS SPACE",(TILE_SIZE*9,TILE_SIZE*10.5))
        pygame.draw.rect(WINDOW,WHITE,(TILE_SIZE*7.25,TILE_SIZE*9.5,TILE_SIZE*9,TILE_SIZE*0.25))
        
        pygame.display.flip()
        CLOCK.tick(FPS / 4)
    
    wait_for_keys()
    
    pygame.mixer.music.load('music/typeA.mp3')
    pygame.mixer.music.play(-1)
    
    while RUN and not GAME_OVER:
        check_for_quit()
        
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_RETURN] and not PAUSING:
            PAUSED = True
        PAUSING = keys[pygame.K_RETURN]
        
        while RUN and PAUSED:
            check_for_quit()
            keys = pygame.key.get_pressed()
        
            if keys[pygame.K_RETURN] and not PAUSING:
                PAUSED = False
            PAUSING = keys[pygame.K_RETURN]
            
            render_field()
            
            scribe.write("PAUSED",(TILE_SIZE*2.5,TILE_SIZE*10.5),int(FONT_SIZE*1.5))
            
            pygame.display.flip()
            CLOCK.tick(FPS)
        
        if keys[pygame.K_l] and not TURNING:
            sh.rotate()
        TURNING = keys[pygame.K_l]
        if keys[pygame.K_a] and not MOVING:
            sh.mx(-1)
        if keys[pygame.K_d] and not MOVING:
            sh.mx(1)
        MOVING = keys[pygame.K_a] or keys[pygame.K_d]
        if keys[pygame.K_s]:
            MDELTA = 2
        else:
            MDELTA = MRATE
        
        if keys[pygame.K_SPACE] and not SPACED:
            MFRAME = 0
            while not sh.my():
                ""
        SPACED = keys[pygame.K_SPACE]
        if MFRAME > MDELTA:
            sh.my()
            MFRAME = 0
        
        
        render_field()
        
        pygame.display.flip()
        CLOCK.tick(FPS)
        MFRAME += 1
        
    pygame.mixer.music.stop()
    
    wait_for_keys()
    
    MFRAME = 0
    
    pygame.mixer.music.load('music/game_over.mp3')
    pygame.mixer.music.queue('music/lost.mp3')
    pygame.mixer.music.play()
    
    while RUN and GAME_OVER:
        check_for_quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            BOARD = [[0 for _ in range(10)] for _ in range(20)]
    
            sh.set_shape(1)

            TURNING = False
            MOVING = False
            SPACED = False

            SCORE = 0
            CLEARS = [0,0,0,0]
            BLOCKS = [0,0,0,0,0,0,0]
            LINES_CLEARED = 0
            NEXTSHAPE = random.randint(0,6)
            PIECES_PLAYED = 0

            SPEED = 1
            SPEEDMULT = 0.9
            FRAME = 0
            MFRAME = 0
            MRATE = FPS / 2
            MDELTA = MRATE
            GAME_OVER = False
            
            SFX_MENU.play()
        
        render_field()        
        
        pygame.display.flip()
        CLOCK.tick(FPS / 4)
        MFRAME += 1
        
    wait_for_keys()
pygame.quit()