#-----------------------------------------------------------------------------------------------------
#------- Videojuego headUP ---------------------------------------------------------------------------
#------- Por: Santiago Taborda E   santiago.tabordae@udea.edu.co -------------------------------------
#-------      Estudiante de Ingeniería de Telecomunicaciones  ----------------------------------------
#-------      CC 1000393907, Wpp 3108983553 ----------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-------      Emmanuel Arango A    emmanuel.arango@udea.edu.co  --------------------------------------
#-------      Estidiante de Ingeniería de Telecomunicaciones -----------------------------------------
#-------      CC 1017214646, Wpp 3122859327 ----------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
#------- Curso Básico de Procesamiento de Imágenes y Visión Artificial--------------------------------
#------- V2 Abril de 2021-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------
#-- 1. Librerías -------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------
import pygame            #Conjunto de modulos de python diseñado para el desarrollo de videojuegos
import json              #Modulo de python para el manejo de datos de formato JSON
import numpy as np       #Librería fundamental para la computación científica en Python
from scipy.spatial import distance #Función de la biblioteca scipy para el calculo de distancia 
import os                #Modulo de python que permite el manejo de directorios/archivos
from pygame import mixer #módulo pygame para cargar y reproducir sonidos
import cv2  	         #Biblioteca libre de visión artificial para el procesado de imagenes

#-----------------------------------------------------------------------------------------------------
#-- 2. Inicialización --------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------

#---- PDI --------------------------------------------------------------------------------------------
#Umbrales de color de acuerdo con el espacio de color YCrCb [Y, Cr, Cb] 
min_YCrCb = np.array([80,135,85],np.uint8)   #El valor Y toma valor entre (16-235)
max_YCrCb = np.array([235,180,135],np.uint8) #El valor Cb Cr toma valor entre (16-240)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)) #Elemento estructurante para la morfología
video = cv2.VideoCapture(0)                  #Se captura el video de la camara en la variable
finger_counting = 0 #Variable que se encarga de contar el número de dedos presentes en pantalla

#---- VIDEOJUEGO -------------------------------------------------------------------------------------
mixer.init()                #Inicializa el módulo mixer para la carga y reproducción de sonido
pygame.init()               #Inicialización de pygame
clock = pygame.time.Clock() #inicialización del reloj, util para las animaciones y actualización

#---- Se define las dimensiones de la ventana principal del juego ------------------------------------
SCREEN_WIDTH = 1024  #ancho
SCREEN_HEIGHT = 1000 #alto

#---- Se definen las VARIABLES Y CONSTANTES del juego ------------------------------------------------
FPS = 80                #Constante que controla los frames por segundo para actualizar pantalla
GRAVITY = 1             #Constante que simula la gravedad para el movimiento fisico
WHITE = (255, 255, 255) #Constante de color
BLACK = (0, 0, 0)       #Constante de color
BACKGROUND =(47, 45, 60)#Constante de color
PLATFOR_NUMBER = 10     #Constante que permite decidir el número de plataformas en pantalla
SCROLLING_LIMIT = 300   #Constante para determinar cuando se activa el desplazamiento de pantalla
GAME_OVER = False       #Constante que permite determinar el fin de la partida
FONT_SMALL = pygame.font.SysFont('Lucida Sans',20, bold=True) #Constante de letra tamaño pequeño
FONT_BIG = pygame.font.SysFont('Lucida Sans',24, bold=True)   #Constante de letra tamaño grande
Scrolling = 0           #No es una constante, desplaza las plataformas
Score = -PLATFOR_NUMBER #No es una constante, permite llevar cuenta del puntaje alcanzado
High_score = 0          #No es una constante, permite llevar cuenta del puntaje más alto 
Fade_background = 0     #No es una constante, permite la visualización correcta del game over

#---- Se crea la ventana principal del juego ---------------------------------------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#creación de la ventana pygame
pygame.display.set_caption('headUpGame')                       #cambio del titulo de la ventana

#---- Se cargan las imagenes y se configura para mantener la posible transparencia de la -------------
#---- imagen png cargada -----------------------------------------------------------------------------
backGroundImage = pygame.image.load('./assets/background/space2.jpg').convert_alpha()#Fondo
platformImage = pygame.image.load('./assets/platform/Tile.png').convert_alpha()#Plataformas

#---- Se carga la musica y efectos de sonido ---------------------------------------------------------
#Musica general
pygame.mixer.music.load('./music/The_Astronaut_loop.wav')#Carga un archivo de musica y lo preparará
pygame.mixer.music.set_volume(0.1)                       #Modifica el volumen para la reproducción
pygame.mixer.music.play(-1, 0.0, )                       #Reproduce el archivo de musica cargado
#Efecto de sonido para el Game Over
gameOverFx = pygame.mixer.Sound('./music/game_over.wav') #Crear un nuevo objeto de sonido desde un archivo
gameOverFx.set_volume(0.5)                           #Modifica el volumen para la reproducción
#Efecto de sonido para el enemigo
enemyFx = pygame.mixer.Sound('./music/scream.wav') #Crear un nuevo objeto de sonido desde un archivo
enemyFx.set_volume(0.1)                            #Modifica el volumen para la reproducción

#---- Función para los letreros en pantalla ----------------------------------------------------------
def screenDrawText(stringText, fontText, colorText, posXText, posYText):
    imageText = fontText.render(stringText, True, colorText)
    screen.blit(imageText, (posXText, posYText))

#---- Función para los panel de score en pantalla ----------------------------------------------------
def screenDrawPanel():
    pygame.draw.rect(screen, BACKGROUND, (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(screen, WHITE, (1,30), (SCREEN_WIDTH, 30), 1)
    screenDrawText('SCORE : '+str(Score)+' | HIGH SCORE : '+str(High_score), FONT_SMALL, WHITE, 10, 2)

#---- Determinar si existe un score más alto o no ----------------------------------------------------
#El score se almacena en un archivo .txt, si dicho archivo existe, se recupera el score pero si no
#existe, se define en cero el score más alto
if os.path.exists('highScore.txt'): 
    with open('highScore.txt', 'r') as file:
        High_score = int(file.read())
else:
    High_score = 0

#----------------------------------------------------------------------------------------------------
#-- 3. Sprites --------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
class sprites:
    #Clase para la carga y la definición de las imagenes que se usan como sprites en animación
    def __init__(self, filename, location):
        self.locationFile = location

        #Lectura del archivo JSON para determinar los parametros del sprite
        self.filename = filename
        with open(self.filename) as f: #Se abre el archivo para su lectura
            self.data = json.load(f)   #Se mapea el archivo a la variable data
        f.close                        #Se cierra el archivo para ahorrar recursos

    def spriteDimensions(self, imageName):
        escale = self.data[imageName]['escale']         #valores para el escalado de la imagen
        downsizing = self.data[imageName]['downsizing'] #valores para el ajuste del rectangulo
        offset = self.data[imageName]['offset']         #valores para el offset de la imagen

        image = pygame.image.load(self.locationFile+imageName).convert_alpha()

        #Tener en cuenta que se redimensiona la imagen del personaje para efectos esteticos y se
        #Asigna a la instancia creada en la inicialización
        image = pygame.transform.scale(image, (escale['w'],escale['h']))
        
        #Se obtiene un rectangulo preliminar en el limite de la imagen 
        rect = image.get_rect() #se obtiene una area rectangular al rededor de la imagen

        #Tamaño para modificar el rectangulo que se usará para la interacción según el anterior
        width = rect.width - downsizing['w']
        height = rect.height - downsizing['h']

        returnList = []
        returnList.append(image)
        returnList.append([width, height])
        returnList.append(offset)

        return returnList

#----------------------------------------------------------------------------------------------------
#-- 4. Personaje ------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    #Se hace uso de pygame.sprite.Sprite que facilita tanto las colisiones como el movimiento y
    #el manejo de sprites (cambios y transiciones)

    #---- Inicialización del personaje --------------------------------------------------------------
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)#constructor de la clase padre
        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT, self.UP_KEY = False, False, False, False
        self.loadFrames()                  #se cargan las diferentes images que serán los sprites
        
        #se inicializan las variables que se utilizan en el personaje
        self.rectPosX = (SCREEN_WIDTH-10)//2#Coordenadas iniciales de acuerdo plataforma inicial
        self.rectPosY = SCREEN_HEIGHT-200   #Coordenadas iniciales de acuerdo plataforma inicial
        self.rect = pygame.Rect(self.rectPosX, self.rectPosY, self.idleLeftRects[0][0], self.idleLeftRects[0][1])
        self.rect.center = (self.rectPosX,self.rectPosY)#Se modifica el centro del rectangulo a las coordenadas
        self.currentFrame = 0
        self.lastFrame = 0
        self.velocityY = 0
        self.velocityX = 0
        self.state = 'idle'
        self.currentImage = self.idleLeftFrames[0]
        self.offsetX = 0
        self.offsetY = 0
        self.UnlockJump = True #Variable que habilita el salto del perosnaje

    #---- Dibujo en pantalla del personaje ----------------------------------------------------------
    def draw(self, display):
        #---- Actualización del personaje en la pantalla ------------------------------------------
        #Se utilizan las coordenadas del rectangulo para el dibujo del personaje con un offset
        #el offset evita problemas de colisión, es el rectangulo el que se toma en cuenta
        display.blit(self.currentImage, (self.rect.x-self.offsetX, self.rect.y-self.offsetY))

    #---- Movimiento y actualización del personaje --------------------------------------------------               
    def moving(self):
        #SE DEBE COMENTAR MEJOR EL MOVIMIENTO VERTICAL
        
        #---- Movimiento vertical -----------------------------------------------------------------
        self.velocityY += GRAVITY #Aplica gravedad restando en cada iteración el valor almacenado en GRAVITY
        if self.UP_KEY:           #Se reconoce cuando se precione la flecha hacia arriba para salto
            self.velocityY = -25  #Valor asociado a la fuerza del salto del personaje
       
        #---- Movimiento horizontal ---------------------------------------------------------------
        self.velocityX = 0
        if self.LEFT_KEY:       #Se reconoce cuando se precione la flecha hacia la izquierda
            self.velocityX = -4 #El movimiento horizontal se hace en unidades de 2
        elif self.RIGHT_KEY:    #Se reconoce cuando se precione la flecha hacia la derecha
            self.velocityX = 4  #El movimiento horizontal se hace en unidades de 2

        #---- Reconocimiento de limites de pantalla ------------------------------------------------       
        if self.rect.x + self.velocityX < 0: 
            self.velocityX = -self.rect.x 
        if (self.rect.x+58) + self.velocityX > SCREEN_WIDTH:
            self.velocityX = SCREEN_WIDTH - (self.rect.x+58)
        
        #---- Reconocimiento colisión con plataformas ----------------------------------------------
        for platform_i in platformsGroup: #Se recorren las plataformas para identificar colisión
            #Se identifica colisión con el uso de rect.colliderect entre la plataforma y un rect
            #generado a partir del personaje pero desplazado para mejor identificación
            if platform_i.rect.colliderect(self.rect.x, self.rect.y+self.velocityY, self.rect.width, 
                                            self.rect.height):
                #Se identifica la posición inferior del rectangulo del personaje con respecto
                #al centro del rectangulo de la plataforma 
                if self.rect.bottom < platform_i.rect.centery:
                    #Se identifica si la velocidad actual es positiva para determinar caida, no salto
                    if self.velocityY > 0:
                        #Se modifica la posición del rectangulo del personaje para que quede justo
                        #encima del rectangulo de la plataforma
                        self.rect.bottom = platform_i.rect.top 
                        self.UnlockJump = True #Permite saltar luego de estar sobre una plataforma
                        self.velocityY = 0
                        if platform_i.getHorizontalType():
                            self.rect.x += platform_i.getVelocityX()

        #---- Reconocimiento para activar desplazamiento --------------------------------------------
        Scrolling = 0
        if self.rect.top <= SCROLLING_LIMIT:
            #se reconoce si el personaje esta saltando para un desplazamiento progresivo
            if self.velocityY < 0:          
                Scrolling = -self.velocityY #es el contrario del salto o caida del personaje


        #---- Actualización del rectangulo ----------------------------------------------------------      
        self.rect.x += self.velocityX #Según la consideración del evento se actualiza la posición
                                      #del personaje para el eje x
        self.rect.y += self.velocityY + Scrolling #Según la consideración del evento se actualiza la 
                                                  #posición del personaje para el eje y sin permitir
                                                  #que el personaje sobrepase el limite de scroll
                                                  #al estar en la ultima plataforma

        self.setState()
        self.animate()

        self.mask = pygame.mask.from_surface(self.currentImage)

        return Scrolling

    #---- Cambio del estado para permitir la animación del personaje --------------------------------               
    def setState(self):
        
        self.state = 'idle' #Estado predeterminado del personaje para la asignación de la animación

        if (self.velocityY != 0 and self.velocityX < 0):   #Animación de salto a la izquierda
            self.state = 'jumping left'
        elif (self.velocityY != 0 and self.velocityX > 0): #Animación de salto a la derecha
            self.state = 'jumping right'
        elif (self.velocityY != 0 and self.velocityX == 0):#Animación de salto a la derecha en caida del personaje
            self.state = 'jumping right'
        elif (self.velocityX > 0):      #Animación de movimiento a la derecha
            self.state = 'moving right'
        elif (self.velocityX < 0):      #Animación de movimiento a la izquierda
            self.state = 'moving left'
    
    #---- Animación del personaje -------------------------------------------------------------------               
    def animate(self):
        currentTime = pygame.time.get_ticks() #Se obtiene el tiempo actual de la ventana

        if (self.state == 'idle'):
            #se identifica cada 200 milisegundos para efectuar la actualización de los sprites
            if ((currentTime - self.lastFrame) > 300):
                self.lastFrame = currentTime #se vuelve a cambiar el frame anterior con el tiempo actual

                #se identifica cual es el sprite siguiente en la animación
                #el operador % permite que se cambie el indice del sprite como un loop
                #si la lista de sprites tiene 4 posiciones, currentFrame varia entre 0 y 3
                self.currentFrame = ((self.currentFrame+1)%len(self.idleLeftFrames))
                if self.FACING_LEFT:
                    #Se cambia la imagen deacuerdo al sprite escogido segun el tiempo
                    self.currentImage = self.idleLeftFrames[self.currentFrame]

                    #Se actualiza el rect correspondiente para cada sprite
                    self.rect.update(self.rect.x, self.rect.y, self.idleLeftRects[self.currentFrame][0], self.idleLeftRects[self.currentFrame][1])
                    self.offsetX = self.idleLeftOffset[self.currentFrame]['x']
                    self.offsetY = self.idleLeftOffset[self.currentFrame]['y']
                elif not self.FACING_LEFT:
                    #Se cambia la imagen deacuerdo al sprite escogido segun el tiempo
                    self.currentImage = self.idleRightFrames[self.currentFrame]
                    
                    #Se actualiza el rect correspondiente para cada sprite
                    self.rect.update(self.rect.x, self.rect.y, self.idleRightRects[self.currentFrame][0], self.idleRightRects[self.currentFrame][1])                    
                    self.offsetX = self.idleRightOffset[self.currentFrame]['x']
                    self.offsetY = self.idleRightOffset[self.currentFrame]['y']

        elif (self.state == 'jumping left'):
            #para el salto se hace cada 100 milisegundos para una actualización
            #más fluida para el movimiento de salto
            if ((currentTime - self.lastFrame) > 150):
                self.lastFrame = currentTime #se vuelve a cambiar el frame anterior con el tiempo actual

                #se identifica cual es el sprite siguiente en la animación
                #el operador % permite que se cambie el indice del sprite como un loop
                #si la lista de sprites tiene 4 posiciones, currentFrame varia entre 0 y 3
                self.currentFrame = ((self.currentFrame+1)%len(self.jumpLeftFrames))

                #Se cambia la imagen deacuerdo al sprite escogido segun el tiempo
                self.currentImage = self.jumpLeftFrames[self.currentFrame]

                #Se actualiza el rect correspondiente para cada sprite
                self.rect.update(self.rect.x, self.rect.y, self.jumpLeftRects[self.currentFrame][0], self.jumpLeftRects[self.currentFrame][1])
                self.offsetX = self.jumpLeftOffset[self.currentFrame]['x']
                self.offsetY = self.jumpLeftOffset[self.currentFrame]['y']

        elif (self.state == 'jumping right'):
            #para el salto se hace cada 100 milisegundos para una actualización
            #más fluida para el movimiento de salto
            if ((currentTime - self.lastFrame) > 150):
                self.lastFrame = currentTime #se vuelve a cambiar el frame anterior con el tiempo actual

                #se identifica cual es el sprite siguiente en la animación
                #el operador % permite que se cambie el indice del sprite como un loop
                #si la lista de sprites tiene 4 posiciones, currentFrame varia entre 0 y 3
                self.currentFrame = ((self.currentFrame+1)%len(self.jumpRightFrames))

                #Se cambia la imagen deacuerdo al sprite escogido segun el tiempo
                self.currentImage = self.jumpRightFrames[self.currentFrame]

                #Se actualiza el rect correspondiente para cada sprite
                self.rect.update(self.rect.x, self.rect.y, self.jumpRightRects[self.currentFrame][0], self.jumpRightRects[self.currentFrame][1])
                self.offsetX = self.jumpRightOffset[self.currentFrame]['x']
                self.offsetY = self.jumpRightOffset[self.currentFrame]['y']
               
        else:
            #en este caso se identifica cada 150 milisegundos pues requiere de una actualización
            #más fluida para el movimiento caminando
            if ((currentTime - self.lastFrame) > 150):
                self.lastFrame = currentTime #se vuelve a cambiar el frame anterior con el tiempo actual

                #se identifica cual es el sprite siguiente en la animación
                #el operador % permite que se cambie el indice del sprite como un loop
                #si la lista de sprites tiene 4 posiciones, currentFrame varia entre 0 y 3
                self.currentFrame = ((self.currentFrame+1)%len(self.walkLeftFrames))

                if self.state == 'moving left':   #Se identifica si el movimiento es para la izquierda
                    #Se cambia la imagen deacuerdo al sprite escogido segun el tiempo
                    self.currentImage = self.walkLeftFrames[self.currentFrame]

                    #Se actualiza el rect correspondiente para cada sprite
                    self.rect.update(self.rect.x, self.rect.y, self.walkLeftRects[self.currentFrame][0], self.walkLeftRects[self.currentFrame][1])
                    self.offsetX = self.walkLeftOffset[self.currentFrame]['x']
                    self.offsetY = self.walkLeftOffset[self.currentFrame]['y']

                elif self.state == 'moving right': #se identifica si el movimiento es para la derecha
                    #Se cambia la imagen deacuerdo al sprite escogido segun el tiempo
                    self.currentImage = self.walkRightFrames[self.currentFrame]

                    #Se actualiza el rect correspondiente para cada sprite
                    self.rect.update(self.rect.x, self.rect.y, self.walkRightRects[self.currentFrame][0], self.walkRightRects[self.currentFrame][1])
                    self.offsetX = self.walkRightOffset[self.currentFrame]['x']
                    self.offsetY = self.walkRightOffset[self.currentFrame]['y']

    #---- Carga de los sprites del personaje --------------------------------------------------------       
    def loadFrames(self):
        #SE DEBE COMENTAR
        idleSpritesRobot = sprites('./assets/robot/idle/idle.json', './assets/robot/')
        idleFramesRect = [idleSpritesRobot.spriteDimensions("idle/Idle_01.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_02.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_03.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_04.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_05.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_06.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_07.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_08.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_09.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_10.png")]
        idleFramesRect = np.array(idleFramesRect, dtype=object)

        self.idleLeftFrames = idleFramesRect[:, 0]
        self.idleLeftRects  = idleFramesRect[:, 1]
        self.idleLeftOffset = idleFramesRect[:, 2]

        self.idleRightFrames = []
        self.idleRightRects  = idleFramesRect[:, 1]
        self.idleRightOffset  = idleFramesRect[:, 2]
        for frame in self.idleLeftFrames:
            self.idleRightFrames.append(pygame.transform.flip(frame, True, False))


        walkLeftSpritesRobot = sprites('./assets/robot/walk/walk.json', './assets/robot/')
        walkFramesRect = [walkLeftSpritesRobot.spriteDimensions("walk/Walk_01.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_02.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_03.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_04.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_05.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_06.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_07.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_08.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_09.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_10.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_11.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_12.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_13.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_14.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_15.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_16.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_17.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_18.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_19.png"),
                           walkLeftSpritesRobot.spriteDimensions("walk/Walk_20.png")]
        walkFramesRect = np.array(walkFramesRect, dtype=object)

        self.walkLeftFrames = walkFramesRect[:, 0]
        self.walkLeftRects  = walkFramesRect[:, 1]
        self.walkLeftOffset = walkFramesRect[:, 2]

        self.walkRightFrames = []
        self.walkRightRects  = walkFramesRect[:, 1]
        self.walkRightOffset  = walkFramesRect[:, 2]
        for frame in self.walkLeftFrames:
            self.walkRightFrames.append(pygame.transform.flip(frame, True, False))

        jumpSpritesRobot = sprites('./assets/robot/jump/jump.json', './assets/robot/')
        jumpFramesRect = [jumpSpritesRobot.spriteDimensions("jump/Jump_01.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_02.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_03.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_04.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_05.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_06.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_07.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_08.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_09.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_10.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_11.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_12.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_13.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_14.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_15.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_16.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_17.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_18.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_19.png"),
                           jumpSpritesRobot.spriteDimensions("jump/Jump_20.png")]
        jumpFramesRect = np.array(jumpFramesRect, dtype=object)

        self.jumpLeftFrames = jumpFramesRect[:, 0]
        self.jumpLeftRects  = jumpFramesRect[:, 1]
        self.jumpLeftOffset = jumpFramesRect[:, 2]

        self.jumpRightFrames = []
        self.jumpRightRects  = jumpFramesRect[:, 1]
        self.jumpRightOffset  = jumpFramesRect[:, 2]
        for frame in self.jumpLeftFrames:
            self.jumpRightFrames.append(pygame.transform.flip(frame, True, False))

#----------------------------------------------------------------------------------------------------
#-- 5. Enemigo --------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------
class Enemy(pygame.sprite.Sprite):
    #Se hace uso de pygame.sprite.Sprite que facilita tanto las colisiones como el movimiento y
    #el manejo de sprites (cambios y transiciones)

    #---- Inicialización del enemigo ----------------------------------------------------------------
    def __init__(self, posY):
        pygame.sprite.Sprite.__init__(self)#constructor de la clase padre
        self.loadFrames()                  #se cargan las diferentes images que serán los sprites

        #se inicializan las variables que se utilizan en el personaje
        self.rectPosY = posY   #Coordenadas iniciales Y de acuerdo al parametro proporcionado

        self.direction = np.random.choice([-1,1],1)[0] #Se escoge dirección, movimiento horizontal
        if self.direction == 1: #Se identifica la dirección del movimiento del enemigo
            self.rectPosX = -20 #Si es para la derecha, inicia en la parte izquierda de la ventana
            self.state = 'moving right'
        else:                   #Si es para la izquierda, inicia en la parte derecha de la ventana
            self.rectPosX = SCREEN_WIDTH+20
            self.state = 'moving left'

        self.rect = pygame.Rect(self.rectPosX, self.rectPosY, self.walkLeftRects[0][0], self.walkLeftRects[0][1])
        self.rect.center = (self.rectPosX,self.rectPosY)#Se modifica el centro del rectangulo a las coordenadas

        self.currentFrame = 0
        self.lastFrame = 0
        self.image = self.walkLeftFrames[0]

    #---- Cambio del estado para permitir la animación del enemigo ----------------------------------               
    def setState(self):
        if (self.direction > 0):      #Animación de movimiento a la derecha
            self.state = 'moving right'
        elif (self.direction < 0):      #Animación de movimiento a la izquierda
            self.state = 'moving left'

    #---- Animación del enemigo ---------------------------------------------------------------------               
    def animate(self):
        currentTime = pygame.time.get_ticks() #Se obtiene el tiempo actual de la ventana

        #en este caso se identifica cada 100 milisegundos pues requiere de una actualización
        #más fluida para el desplazamiento del enemigo
        if ((currentTime - self.lastFrame) > 100):
            self.lastFrame = currentTime #Se actualiza el frame con el tiempo actual
            #se identifica cual es el sprite siguiente en la animación
            #el operador % permite que se cambie el indice del sprite como un loop
            #si la lista de sprites tiene 4 posiciones, currentFrame varia entre 0 y 3
            self.currentFrame = ((self.currentFrame+1)%len(self.walkLeftFrames)) 
            if self.state == 'moving left':   #Se identifica si el movimiento es para la izquierda
                #Se cambia la imagen deacuerdo al sprite escogido segun el tiempo
                self.image = self.walkLeftFrames[self.currentFrame]

                #Se actualiza el rect correspondiente para cada sprite
                self.rect.update(self.rect.x, self.rect.y, 
                self.walkLeftRects[self.currentFrame][0], self.walkLeftRects[self.currentFrame][1])
                

            elif self.state == 'moving right': #se identifica si el movimiento es para la derecha
                #Se cambia la imagen deacuerdo al sprite escogido segun el tiempo
                self.image = self.walkRightFrames[self.currentFrame]

                #Se actualiza el rect correspondiente para cada sprite
                self.rect.update(self.rect.x, self.rect.y, 
                self.walkRightRects[self.currentFrame][0], self.walkRightRects[self.currentFrame][1])
                
    #---- Actualización y movimiento del enemigo --------------------------------------------------
    def update(self, Scrolling):
        enemyFx.play() #Se reproduce el efecto de sonido para el enemigo
        #---- Movimiento vertical -----------------------------------------------------------------
        self.rect.y += Scrolling          #El movimiento de los enemigos en Y

        #---- Movimiento horizontal ---------------------------------------------------------------
        self.rect.x += self.direction * np.random.randint(2,4) #El movimiento de los enemigos en X

        #Verificación para determinar si se debe eliminar un enemigo cuando sale de pantalla
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill() #Se elimina el enemigo al salir de pantalla

        self.setState()
        self.animate()
    
    #---- Carga de los sprites del enemigo ----------------------------------------------------------
    def loadFrames(self):
        #Se utiliza un archivo json para recuperar los datos de cada sprite, pues dependiendo
        #de ello cuenta con un tamaño distinto para que el rect siempre este ajustado y se hace
        #uso de la clase sprites diseñada anteriormente
        walkLeftSpritesEnemy = sprites('./assets/enemy/walk/walk.json', './assets/enemy/')
        walkFramesRect = [walkLeftSpritesEnemy.spriteDimensions("walk/walk_01.png"),
                           walkLeftSpritesEnemy.spriteDimensions("walk/walk_02.png"),
                           walkLeftSpritesEnemy.spriteDimensions("walk/walk_03.png"),
                           walkLeftSpritesEnemy.spriteDimensions("walk/walk_04.png"),
                           walkLeftSpritesEnemy.spriteDimensions("walk/walk_05.png"),
                           walkLeftSpritesEnemy.spriteDimensions("walk/walk_06.png"),
                           walkLeftSpritesEnemy.spriteDimensions("walk/walk_07.png"),
                           walkLeftSpritesEnemy.spriteDimensions("walk/walk_08.png")]
        walkFramesRect = np.array(walkFramesRect, dtype=object)

        #Se indexa dependiendo de la información requerida
        self.walkLeftFrames = walkFramesRect[:, 0] #Las imagenes correspondientes a los sprites
        self.walkLeftRects  = walkFramesRect[:, 1] #El rect creado para cada imagen de sprite
        self.walkLeftOffset = walkFramesRect[:, 2] #El offset necesario para centrar el rect

        #Se hace necesario utilizar un efecto espejo para que los sprites se orienten a la derecha
        self.walkRightFrames = []
        self.walkRightRects  = walkFramesRect[:, 1]
        self.walkRightOffset  = walkFramesRect[:, 2]
        for frame in self.walkLeftFrames:
            self.walkRightFrames.append(pygame.transform.flip(frame, True, False))

#----------------------------------------------------------------------------------------------------
#-- 6. Plataformas ----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------

#---- Clase para la creación de cada plataforma como objeto -----------------------------------------
class Platform(pygame.sprite.Sprite): 
    #Se hace uso de pygame.sprite.Sprite que facilita tanto las colisiones como el movimiento y
    #el manejo de sprites (cambios y transiciones). para este caso se puede usar los grupos de 
    #pygame que optimizan la utilización recursiva de la clase

    #---- Inicialización de la plataforma -------------------------------------------------------
    def __init__(self, x, y, width, moving): 
        pygame.sprite.Sprite.__init__(self) #constructor de la clase padre

        self.width = width #Inicilización del tamaño de la plataforma

        #se carga la imagen que se utiliza para la plataforma, con longitud variable
        self.image = pygame.transform.scale(platformImage, (self.width, 30)) 
        self.rect = self.image.get_rect()#se obtiene el rectangulo para la imagen correspondiente

        #Inicialización de coordenadas xy para la plataforma
        self.rect.x = x
        self.rect.y = y

        self.moving = moving  #Se inicializa el tipo de plataforma, movimiento horizontal
        self.counterMoving = np.random.randint(0,5)    #Determina el limite movimiento horizontal
        self.direction = np.random.choice([-1,1],1)[0] #Se escoge dirección, movimiento horizontal
        self.velocityX = 0                             #Inicialización de la velocidad 
        self.accelerationX = np.random.randint(2,6)    #Inicialización random de la aceleración
        self.limitMoving = np.random.randint(200,400)  #Inicialización el limite del movimiento

    #---- Actualización y movimiento de la plataforma --------------------------------------------
    def update(self, Scrolling):
        #---- Movimiento vertical -----------------------------------------------------------------
        self.rect.y += Scrolling          #El movimiento de las plataformas en Y

        #---- Movimiento horizontal ---------------------------------------------------------------
        if self.moving:                   #Si la plataforma es de tipo movimiento horizontal 
            self.velocityX = self.direction * self.accelerationX #la velocidad es aleatoria       
            self.rect.x += self.velocityX #se modifica su posición en X
            self.counterMoving += self.accelerationX#Se incrementa para permitir limitar movimiento
        if self.counterMoving >= self.limitMoving:#Si la plataforma se ha desplazado más de un numero
            self.direction *= -1                  #aleatorio, se invierte el movimiento
            self.counterMoving = 0

        #---- Reconocimiento de limites de pantalla para movimiento horizontal --------------------       
        if self.rect.x + self.velocityX < 0 or (self.rect.x+self.width) + self.velocityX > SCREEN_WIDTH: 
            self.direction *= -1   #Al toparse con algun limite horizontal se invierte el movimiento
            self.counterMoving = 0

        #Verificación para determinar si se debe eliminar una plataforma cuando sale de pantalla
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()                   #Se elimina la plataforma al salir de pantalla
    
    def getHorizontalType(self):
        return self.moving

    def getVelocityX(self):
        return self.velocityX

#---- Función para garantizar que el espacio entre plataforma sea el adecuado -----------------------
def xCoordinate(prevPlatform, nextCoordX, nextWidth):
    prevCoordX = prevPlatform.rect.x    #Se recupera la posición x de la plataforma anterior
    prevWidth = prevPlatform.rect.width #Se recupera el tamaño de la plataforma anterior
    control = True #Variable de control para el ciclo

    #Hasta no encontrar una coordenada X que permita el salto, no se termina el ciclo
    while control:
        if prevCoordX-nextCoordX < 0 : #Se identifica si la plataforma siguiente esta en izq o der
            prevRightEdge = prevCoordX+nextWidth #Coordenada lado derecho, plataforma anterior
            nextLeftEdge  = nextCoordX           #Coordenada lado izquierdo, plataforma siguiente
            #La distancia entre las coordenadas anteriores no debe superar 100
            if abs(prevRightEdge-nextLeftEdge) > 140: 
                nextCoordX = np.random.randint(90, SCREEN_WIDTH-nextWidth-10) #Se calcula una nueva coord
            else:
                control = False #Si no supera la distancia, se puede terminar el ciclo
        else:
            prevLeftEdge  = prevCoordX           #Coordenada lado izquierdo, plataforma anterior
            nextRightEdge = nextCoordX+prevWidth #Coordenada lado derecho, plataforma siguiente
            #La distancia entre las coordenadas anteriores no debe superar 100
            if abs(prevLeftEdge-nextRightEdge) > 140:
                nextCoordX = np.random.randint(90, SCREEN_WIDTH-nextWidth-10) #Se calcula una nueva coord
            else:
                control = False #Si no supera la distancia, se puede terminar el ciclo
    return nextCoordX #Se retorna la coordenada X que cumple las consideraciones

#----------------------------------------------------------------------------------------------------
#-- 7. Instancias -----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------

#---- Creación del personaje ------------------------------------------------------------------------
robotPlayer = Player()

#---- Creación de enemigos --------------------------------------------------------------------------
enemiesGroup = pygame.sprite.Group()  #Instancia del uso de pygame groups

#---- Creación de plataformas -----------------------------------------------------------------------
platformsGroup = pygame.sprite.Group()#Instancia del uso de pygame groups

#Plataforma inicial con coordenadas aproximadamente en la mitad de la ventana
platformI = Platform((SCREEN_WIDTH-150)//2, SCREEN_HEIGHT-100, 150, False)
platformsGroup.add(platformI) #Se agrega la plataforma creada al grupo de plataformas
Score += 1                    #Cada que se agregue una plataforma, se incrementa el score en 1

#----------------------------------------------------------------------------------------------------
#-- 8. Funcionamiento e integración -----------------------------------------------------------------
#----------------------------------------------------------------------------------------------------

#---- Se define el ciclo con el cual se evita el cierre de la ventana principal creada --------------
playing = True #Variable de control para el ciclo mencionado
while playing:
    #------------ Reconocimiento de movimientos por camara con opencv--------------------------------
    finger_counting = 0#Se reinicia el conteo de los dedos cada vez que se entra al ciclo
    #---- Lectura de imagen-video -------------------------------------------------------------------   
    success, frame = video.read() #Se toma del video los valores (imagen) a procesar
    frame = cv2.flip(frame, 1)    #Se utiliza flip para generar el efecto espejo

    #---- Delimitación del area de reconocimiento ---------------------------------------------------
    frameArea = frame[250:480,380:600] #Se selecciona el area de interes de reconocimiento
    #Se muestra el area de interés donde se debe ubicar la mano
    cv2.rectangle(frame,(380,250),(600,480),(0,255,0),1)

    #---- Cambio del espacio de color ---------------------------------------------------------------
    image = cv2.cvtColor(frameArea, cv2.COLOR_BGR2YCR_CB)#Se pasa el frame al espacio de color YCRCB

    #---- Procesado de color de acuerdo a los umbrales y binarización -------------------------------
    skinMask = cv2.inRange(image, min_YCrCb, max_YCrCb) #Se binariza la imagen de acuerdo al umbral
    skinMask = cv2.medianBlur(skinMask, 7)              #Se utiliza para eliminar ruido excesivo

    #---- Morfologia --------------------------------------------------------------------------------
    #Se utiliza el Elemento estructurante ellipse 5x5 para open y close de la imagen
    opening = cv2.morphologyEx(skinMask, cv2.MORPH_OPEN, kernel, iterations=4) #Open
    close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)   #Close
    cv2.imshow("Binarización", close)      #BORRAR PARA LA ENTREGA
    
    #---- Contornos ---------------------------------------------------------------------------------
    #CHAIN_APPROX_SIMPLE toma el minimo de puntos necesarios para el contorno, RETR_EXTERNAL toma el 
    #contorno externo de la forma
    contours, hierarchy = cv2.findContours(close.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    #---- Conteo de dedos levantados presentes en el frame -------------------------------------------
    if len(contours) > 0:  #Se identifica si en el area de interes se ha encontrado contornos
        robotPlayer.LEFT_KEY = False #Se hace necesario reiniciar para simular keyUp
        robotPlayer.RIGHT_KEY = False#Se hace necesario reiniciar para simular keyUp
        robotPlayer.UP_KEY = False   #Se hace necesario reiniciar para simular keyUp
        #Interesa el contorno más grande pues se asume que la mano es la que genera dicho contorno
        hand_segment = max(contours, key=cv2.contourArea) 
        cv2.drawContours(frameArea, contours, 0,(224,255,0),1)

        #Se utiliza convexHull para calcular el espacio abarcado por el contorno de la mano
        hull = cv2.convexHull(hand_segment)
        cv2.drawContours(frameArea, [hull], 0, (0, 170, 255), 2)

        #Es necesario encontrar los defectos del espacio delimitado por convexHull para ajustarlo
        #a el controno de la mano ignorando las areas vacias
        hull = cv2.convexHull(hand_segment, returnPoints = False)

        #covenxityDefects de la forma [start_index, end_index, farthest_pt_index, fixpt_depthint]
        defects = cv2.convexityDefects(hand_segment,hull) 
        
        #Usando start point, end point, farthest point se puede determinar si se reconoce un dedo o no
        #esto aplicando el teorema de coseno para calcular el angulo entre dichos puntos menor a 90
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]#Se recuperan start_index, end_index, farthest_pt_index, fixpt_depth
            start = tuple(hand_segment[s][0]) #Se recuperan los valores indexando el contorno 
            end = tuple(hand_segment[e][0])   #Se recuperan los valores indexando el contorno 
            far = tuple(hand_segment[f][0])   #Se recuperan los valores indexando el contorno 

            #Aplicando teorema del coseno se calculan los lados del posible triangulo formado
            a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

            #Aplicando el teorema del coseno se calcula el angulo del triangulo supuesto
            angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) #Se obtiene en radianes
            angle = np.degrees(angle)#Se pasa a grados para permitir la distinción de Dedo o no dedo
            angle = int(angle)       #Interesa la parte entera (se acepta decimal como error)

            #Se hace necesario filtrar los puntos de tal forma que si la distancia entre el punto inicial y el 
            #punto final sea pequeña, no se tome en cuenta para el conteo
            if c > 20 and angle < 90:  # angle less than 90 degree, treat as fingers
                finger_counting += 1
                cv2.circle(frameArea,tuple(start),4,[0, 0, 255],2)
                cv2.circle(frameArea,tuple(end),4,[0, 255, 0],2)
                cv2.circle(frameArea,tuple(far),4,[255, 0, 0],-1)
        if finger_counting > 0:
            finger_counting += 1
        cv2.putText(frameArea, str(finger_counting), (3, 30), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0) , 2, cv2.LINE_AA)

    #---- Movimiento de acuerdo al número de dedos en video ------------------------------------------
    #Movimiento vertical (salto)
    if finger_counting == 5 and robotPlayer.UnlockJump == True:
        robotPlayer.UP_KEY = True      #Luego de saltar se deshabilita el salto hasta una
        robotPlayer.UnlockJump = False #nueva colisión con una plataforma
    #Movimiento horizontal (Izquierda Derecha)    
    if finger_counting == 4:
        robotPlayer.RIGHT_KEY, robotPlayer.FACING_LEFT = True,False
    elif finger_counting == 3:
        robotPlayer.LEFT_KEY, robotPlayer.FACING_LEFT = True,True

    cv2.imshow("webcam", frame)  # muestra los fotogramas captados por la camara

    #------------ Logica heredada del juego base, sin integración con open cv -----------------------
    #------ Actualización del reloj por frame -------------------------------------------------------
    clock.tick(FPS) #se realiza cada 60 segundos la actualización en pantalla (para animaciones)

    if GAME_OVER == False:
        #------ Cambio del fondo de la ventana con desplazamiento -----------------------------------
        screen.blit(backGroundImage, (0,0))
        
        #------ Actualización y dibujo de personaje -------------------------------------------------
        Scrolling = robotPlayer.moving()
        robotPlayer.draw(screen)

        #------ Creación de las plataformas ---------------------------------------------------------
        if len(platformsGroup) < PLATFOR_NUMBER:
            Score += 1 #Cada que se agregue una plataforma, se incrementa el score en 1
            platformWidth = np.random.randint(150,250) #Se genera un tamaño aleatorio

            #Se asegura el espaciamiento no supera el alcance del salto con la función xCoordinate
            platformX = np.random.randint(50, SCREEN_WIDTH-platformWidth-10)
            platformX = xCoordinate(platformI, platformX, platformWidth)
            
            #Apartir de la ultima plataforma creada se genera una nueva coordenada Y
            platformY = platformI.rect.y - np.random.randint(200,300)

            #Con animos de generar mayor dificultad, se generan plataformas con movimiento horizontal
            platformType = np.random.choice([0,1],1)[0] #Se escoge aleatoriamente, 0 False 1 True
            if platformType and Score > 5:
                #Se crea una plataforma con movimiento horizontal
                platformI = Platform(platformX, platformY, platformWidth, True)
            else:
                #Se crea una plataforma sin movimiento horizontal
                platformI = Platform(platformX, platformY, platformWidth, False)
            platformsGroup.add(platformI) #Se agrega plataforma al grupo  
        #------ Actualización y dibujo de plataformas --------------------------------------------------
        platformsGroup.update(Scrolling)
        platformsGroup.draw(screen)

        #------ Creación de los enemigos ---------------------------------------------------------------
        if len(enemiesGroup) == 0 and Score > 10:
            enemyI = Enemy(np.random.randint(50,400))
            enemiesGroup.add(enemyI)
        #------ Actualización y dibujo de enemigos -----------------------------------------------------
        enemiesGroup.update(Scrolling)
        enemiesGroup.draw(screen)

        #------ Dibujo del panel para el score en pantalla ---------------------------------------------
        screenDrawPanel()

        #------ Inicialización del salto, para evitar vuelo con tecla sostenida ------------------------
        robotPlayer.UP_KEY = False 

        #------ Reconocimiento de fin de juego (fin de partida) ----------------------------------------
        if robotPlayer.rect.top > SCREEN_HEIGHT: #Si el rect del personaje sale de pantalla en caida
            GAME_OVER = True                     #se acaba el juego
            enemyFx.stop()                       #Se pausa el sonido del enemigo para dar paso game over
            gameOverFx.play()                    #Se reproduce el efecto de sonido para game over

        #Si el personaje colisiona con algún enemigo, se acaba el juego. En spritecollide se usa False
        #para no eliminar el sprite una vez se identifica la colisión
        if  pygame.sprite.spritecollide(robotPlayer, enemiesGroup, False):
            #El tipo de colisión con los enemigos es por medio de una mascara, esto para asegurarse de que
            #la colisión no se active si los rect se tocan, si no si la imagen colisiona
            if pygame.sprite.spritecollide(robotPlayer, enemiesGroup, False, pygame.sprite.collide_mask):
                GAME_OVER = True
                enemyFx.stop()               #Se pausa el sonido del enemigo para dar paso al game over
                gameOverFx.play()            #Se reproduce el efecto de sonido para game over
    else:
        #------ Aviso en pantalla GAME OVER  -----------------------------------------------------------
        #Se muestra en pantalla que el juego ha terminado, el puntaje y la instrucción de reinicio

        robotPlayer.LEFT_KEY = False   #Permite que el personaje inicie completamente inmovil
        robotPlayer.RIGHT_KEY = False

        if Fade_background < SCREEN_HEIGHT:
            Fade_background += 12
            pygame.draw.rect(screen, BLACK, (0,0, SCREEN_WIDTH, Fade_background))
        else:
            screenDrawText('~  GAME OVER  ~', FONT_BIG, WHITE, (SCREEN_WIDTH-290)//2, 300)
            screenDrawText('~  SCORE: '+str(Score)+'  ~', FONT_BIG, WHITE, (SCREEN_WIDTH-290)//2, 350)
            screenDrawText('~  HIGH SCORE: '+str(High_score)+'  ~', FONT_BIG, WHITE, (SCREEN_WIDTH-290)//2, 400)
            screenDrawText('~  PRESS ENTER  ~', FONT_BIG, WHITE, (SCREEN_WIDTH-290)//2, 450)

            #------ Actualización de puntaje más alto  -------------------------------------------------
            if Score > High_score: #Se reconoce si el score actual es más alto que el score más alto
                High_score = Score #En caso de ser más alto, se reemplaza
                with open('highScore.txt', 'w') as file: #Se debe almacenar y para ello se usa un txt
                    file.write(str(High_score))

            #Si el usuario presiona enter, se reinicia el juego
            key = pygame.key.get_pressed()
            if key[pygame.K_KP_ENTER]:
                #------ Reinicio de variables  ---------------------------------------------------------
                GAME_OVER = False
                Scrolling = 0
                Scrolling_PlfPosy = []
                Score = 0
                Fade_background = 0
                #------ Reubicación del personaje  -----------------------------------------------------
                robotPlayer.rect.center = ((SCREEN_WIDTH-10)//2,SCREEN_HEIGHT-200)
                #------ Reinicio de plataformas  -------------------------------------------------------
                platformsGroup.empty() #Se eliminan todas las plataformas presentes en el grupo
                #Plataforma inicial con coordenadas aproximadamente en la mitad de la ventana
                platformI = Platform((SCREEN_WIDTH-150)//2, SCREEN_HEIGHT-100, 150, False)
                platformsGroup.add(platformI)        #Se agrega la plataforma al grupo de plataformas
                #------ Reinicio de enemigos  ----------------------------------------------------------
                enemiesGroup.empty() #Se eliminan todas las plataformas presentes en el grupo

    #------ Manejo de eventos  -------------------------------------------------------------------------
    #------ pygame.event.get() obtendrá todos los eventos y los eliminará de la cola -------------------
    for event in pygame.event.get():
        #------ el evento es de tipo QUIT cuando se presiona el boton "X" de la ventana ----------------
        if event.type == pygame.QUIT:

            #------ Actualización de puntaje más alto  -------------------------------------------------
            if Score > High_score: #Se reconoce si el score actual es más alto que el score más alto
                High_score = Score #En caso de ser más alto, se reemplaza
                with open('highScore.txt', 'w') as file: #Se debe almacenar y para ello se usa un txt
                    file.write(str(High_score))

            playing = False #Se termina el ciclo para permitir el cierre de la ventana 

        #------ Eventos para el manejo del personaje, desplazamientos ----------------------------------   
        if event.type == pygame.KEYDOWN:
            #activación de movimiento hacia la izquierda al presionar tecla 'izquierda'
            if event.key == pygame.K_LEFT:      
                robotPlayer.LEFT_KEY, robotPlayer.FACING_LEFT = True,True
            #activación de movimiento hacia la derecha al presionar tecla 'derecha'
            elif event.key == pygame.K_RIGHT:    
                robotPlayer.RIGHT_KEY, robotPlayer.FACING_LEFT = True,False
            #Solo salta cuando la variable UnlockJump está en True
            elif event.key == pygame.K_UP and robotPlayer.UnlockJump == True: 
                robotPlayer.UP_KEY = True     #Luego de saltar se deshabilita el salto hasta una                            
                robotPlayer.UnlockJump = False#nueva colisión con una plataforma
        if event.type == pygame.KEYUP:  
            #desactiva el movimiento hacia la izquierda al soltar la tecla 'izquierda'        
            if event.key == pygame.K_LEFT:       
                robotPlayer.LEFT_KEY = False
            #desactiva el movimiento hacia la derecha al soltar la tecla 'derecha'
            elif event.key == pygame.K_RIGHT:    
                robotPlayer.RIGHT_KEY = False
            #desactiva el movimiento de salto al soltar la tecla de 'arriba'
            elif event.key == pygame.K_UP:       
                robotPlayer.UP_KEY = False
        
    #------ Actualización grafica de la ventana  -----------------------------------------------------
    pygame.display.update() #Actualiza la ventana, al pasar parametro actualiza una porción

pygame.quit() #Desinicializa todos los módulos de pygame que han sido previamente inicializados
#-----------------------------------------------------------------------------------------------------
#---------------------------  FIN DEL PROGRAMA -------------------------------------------------------
#-----------------------------------------------------------------------------------------------------