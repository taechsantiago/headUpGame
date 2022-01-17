 #------------------------------------------------------------------------------------------------
#------- Videojuego headUP ----------------------------------------------------------------------
#------- Por: Santiago Taborda E   santiago.tabordae@udea.edu.co --------------------------------
#-------      Estudiante de Ingeniería de Telecomunicaciones  -----------------------------------
#-------      CC 1000393907, Wpp 3108983553 -----------------------------------------------------
#--------                                      --------------------------------------------------
#-------      Emmanuel Arango A    emmanuel.arango@udea.edu.co  ---------------------------------
#-------      Estidiante de Ingeniería de Telecomunicaciones ------------------------------------
#-------      CC 1017214646, Wpp 3122859327 -----------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
#------- Curso Básico de Procesamiento de Imágenes y Visión Artificial---------------------------
#------- V2 Abril de 2021------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------
#-- 1. Librerías --------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
import pygame      #Conjunto de modulos de python diseñado para el desarrollo de videojuegos
import json        #Modulo de python para el manejo de datos de formato JSON
import numpy as np #Librería fundamental para la computación científica en Python

#------------------------------------------------------------------------------------------------
#-- 2. Inicialización ---------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
pygame.init()               #Inicialización de pygame
clock = pygame.time.Clock() #inicialización del reloj, util para las animaciones y actualización



#---- Se define las dimensiones de la ventana principal del juego -------------------------------
SCREEN_WIDTH = 1024  #ancho
SCREEN_HEIGHT = 1024 #alto

#---- Se definen las variables CONSTANTES del juego ---------------------------------------------
GRAVEDAD = 1            #Constante que simula la gravedad para el movimiento fisico
WHITE = (255, 255, 255) #Constante de color

#---- Se crea la ventana principal del juego ----------------------------------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#creación de la ventana pygame
pygame.display.set_caption('headUpGame')                       #cambio del titulo de la ventana

#---- Se cargan las imagenes y se configura para mantener la posible transparencia de la --------
#---- imagen png cargada ------------------------------------------------------------------------
backGroundImage = pygame.image.load('./assets/largeBlueNebula.png').convert_alpha()#Fondo


#------------------------------------------------------------------------------------------------
#-- 3. Sprites ----------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
class sprites:
    #Clase para la carga y la definición de las imagenes que se usan como sprites en animación
    def __init__(self, filename):
        #Lectura del archivo JSON para determinar los parametros del sprite
        self.filename = filename
        with open(self.filename) as f: #Se abre el archivo para su lectura
            self.data = json.load(f)   #Se mapea el archivo a la variable data
        f.close                        #Se cierra el archivo para ahorrar recursos

    def spriteDimensions(self, imageName):
        escale = self.data[imageName]['escale']         #valores para el escalado de la imagen
        downsizing = self.data[imageName]['downsizing'] #valores para el ajuste del rectangulo
        offset = self.data[imageName]['offset']         #valores para el offset de la imagen

        image = pygame.image.load('./assets/robot/'+imageName).convert_alpha()

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

#------------------------------------------------------------------------------------------------
#-- 4. Personaje --------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    #Se hace uso de pygame.sprite.Sprite que facilita tanto las colisiones como el movimiento y
    #el manejo de sprites (cambios y transiciones)

    #---- Inicialización del personaje ----------------------------------------------------------
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)#constructor de la clase padre
        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT, self.UP_KEY = False, False, False, False
        self.loadFrames()                  #se cargan las diferentes images que serán los sprites
        
        #se inicializan las variables que se utilizan en el personaje
        self.rectPosX = 255
        self.rectPosY = 350
        self.rect = pygame.Rect(self.rectPosX, self.rectPosY, self.idleLeftRects[0][0], self.idleLeftRects[0][1])
        self.rect.center = (self.rectPosX,self.rectPosY)#Se modifica el centro del rectangulo a las coordenadas
        self.currentFrame = 0
        self.lastFrame = 0
        self.velocity_y = 0
        self.velocity = 0
        self.state = 'idle'
        self.currentImage = self.idleLeftFrames[0]
        self.offsetX = 0
        self.offsetY = 0

    def draw(self, display):
        #---- Actualización del personaje en la pantalla ------------------------------------------
        #Se utilizan las coordenadas del rectangulo para el dibujo del personaje con un offset
        #el offset evita problemas de colisión, es el rectangulo el que se toma en cuenta
        #screen.blit(image, (rect.x-offset['x'], rect.y-offset['y']))
        display.blit(self.currentImage, (self.rect.x-self.offsetX, self.rect.y-self.offsetY))

        #BORRAR SIGUIENTE LINEA PARA ENTREGAR
        pygame.draw.rect(display, WHITE, self.rect, 2)#se dibuja el rectangulo BORRAR PARA ENTREGAR

    def moving(self):
        #SE DEBE COMENTAR MEJOR
        self.velocity = 0

        if self.UP_KEY:
            self.rectPosY = 348    # permite cumplir pasar la condición y darle aplicarle gravedad en y 
            self.velocity_y = -20
        if self.LEFT_KEY:
            self.velocity = -2
        elif self.RIGHT_KEY:
            self.velocity = 2
        self.rectPosX += self.velocity

        # GRAVEDAD y control de movimiento vertical
      
                                        # condición que limita el movimiento y la aplicación de gravedad
        if (self.rectPosY >= 350):      # de esta forma no cae infinitiamente y la gravedad solo aplica al saltar
            self.velocity_y = 0
            self.rectPosY = 350
        elif (self.rectPosY < 350) :
            self.velocity_y += GRAVEDAD

        self.rectPosY += self.velocity_y

        

        self.setState()
        self.animate()

    def setState(self):
        self.state = 'idle'
        if (self.velocity_y != 0 and self.velocity < 0): 
            self.state = 'jumping left'
        elif (self.velocity_y != 0 and self.velocity > 0):
            self.state = 'jumping right'
        elif (self.velocity_y != 0 and self.velocity == 0):
            self.state = 'jumping right'
        elif (self.velocity > 0):
            self.state = 'moving right'
        elif (self.velocity < 0):
            self.state = 'moving left'
        
    
    def animate(self):
        #SE DEBE COMENTAR MEJOR
        
        currentTime = pygame.time.get_ticks()
        if (self.state == 'idle'):
            #se identifica cada 200 milisegundos para efectuar la actualización de los sprites
            if ((currentTime - self.lastFrame) > 300):
                self.lastFrame = currentTime #se vuelve a cambiar el tiempo con el tiempo actual
                #se identifica cual es el sprite siguiente en la animación
                #el operador % permite que se cambie el indice del sprite como un loop
                #si la lista de sprites tiene 4 posiciones, currentFrame varia entre 0 y 3
                self.currentFrame = ((self.currentFrame+1)%len(self.idleLeftFrames))
                if self.FACING_LEFT:
                    self.currentImage = self.idleLeftFrames[self.currentFrame]
                    
                    self.rect.update(self.rectPosX, self.rectPosY, self.idleLeftRects[self.currentFrame][0], self.idleLeftRects[self.currentFrame][1])
                    self.offsetX = self.idleLeftOffset[self.currentFrame]['x']
                    self.offsetY = self.idleLeftOffset[self.currentFrame]['y']

                elif not self.FACING_LEFT:
                    self.currentImage = self.idleRightFrames[self.currentFrame]
                    
                    self.rect.update(self.rectPosX, self.rectPosY, self.idleRightRects[self.currentFrame][0], self.idleRightRects[self.currentFrame][1])                    
                    self.offsetX = self.idleRightOffset[self.currentFrame]['x']
                    self.offsetY = self.idleRightOffset[self.currentFrame]['y']

        elif (self.state == 'jumping left'):
            #para el salto se hace cada 100 milisegundos para una actualización
            #más fluida para el movimiento de salto
            if ((currentTime - self.lastFrame) > 150):
                self.lastFrame = currentTime
                self.currentFrame = ((self.currentFrame+1)%len(self.jumpLeftFrames))
                self.currentImage = self.jumpLeftFrames[self.currentFrame]
                self.rect.update(self.rectPosX, self.rectPosY, self.jumpLeftRects[self.currentFrame][0], self.jumpLeftRects[self.currentFrame][1])
                self.offsetX = self.jumpLeftOffset[self.currentFrame]['x']
                self.offsetY = self.jumpLeftOffset[self.currentFrame]['y']

        elif (self.state == 'jumping right'):
            #para el salto se hace cada 100 milisegundos para una actualización
            #más fluida para el movimiento de salto
            if ((currentTime - self.lastFrame) > 150):
                self.lastFrame = currentTime
                self.currentFrame = ((self.currentFrame+1)%len(self.jumpRightFrames))
                self.currentImage = self.jumpRightFrames[self.currentFrame]
                self.rect.update(self.rectPosX, self.rectPosY, self.jumpRightRects[self.currentFrame][0], self.jumpRightRects[self.currentFrame][1])
                self.offsetX = self.jumpRightOffset[self.currentFrame]['x']
                self.offsetY = self.jumpRightOffset[self.currentFrame]['y']
               
        else:
            #en este caso se identifica cada 100 milisegundos pues requiere de una actualización
            #más fluida para el movimiento caminando
            if ((currentTime - self.lastFrame) > 150):
                self.lastFrame = currentTime
                self.currentFrame = ((self.currentFrame+1)%len(self.walkLeftFrames))
                if self.state == 'moving left':
                    self.currentImage = self.walkLeftFrames[self.currentFrame]

                    self.rect.update(self.rectPosX, self.rectPosY, self.walkLeftRects[self.currentFrame][0], self.walkLeftRects[self.currentFrame][1])
                    self.offsetX = self.walkLeftOffset[self.currentFrame]['x']
                    self.offsetY = self.walkLeftOffset[self.currentFrame]['y']

                elif self.state == 'moving right':
                    self.currentImage = self.walkRightFrames[self.currentFrame]

                    self.rect.update(self.rectPosX, self.rectPosY, self.walkRightRects[self.currentFrame][0], self.walkRightRects[self.currentFrame][1])
                    self.offsetX = self.walkRightOffset[self.currentFrame]['x']
                    self.offsetY = self.walkRightOffset[self.currentFrame]['y']
           
    def loadFrames(self):
        #SE DEBE COMENTAR
        idleSpritesRobot = sprites('./assets/robot/idle/idle.json')
        idleFramesRect = [idleSpritesRobot.spriteDimensions("idle/Idle_01.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_02.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_03.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_04.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_05.png"),
                           idleSpritesRobot.spriteDimensions("idle/Idle_06.png")]
        idleFramesRect = np.array(idleFramesRect, dtype=object)

        self.idleLeftFrames = idleFramesRect[:, 0]
        self.idleLeftRects  = idleFramesRect[:, 1]
        self.idleLeftOffset = idleFramesRect[:, 2]

        self.idleRightFrames = []
        self.idleRightRects  = idleFramesRect[:, 1]
        self.idleRightOffset  = idleFramesRect[:, 2]
        for frame in self.idleLeftFrames:
            self.idleRightFrames.append(pygame.transform.flip(frame, True, False))


        walkLeftSpritesRobot = sprites('./assets/robot/walk/walk.json')
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

        jumpSpritesRobot = sprites('./assets/robot/jump/jump.json')
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


robotPlayer = Player() #Creación del personaje

#------------------------------------------------------------------------------------------------
#-- 5. Funcionamiento e integración -------------------------------------------------------------
#------------------------------------------------------------------------------------------------

#---- Se define el ciclo con el cual se evita el cierre de la ventana principal creada ----------
playing = True #Variable de control para el ciclo mencionado
while playing:
    #------ Actualización del reloj por frame ---------------------------------------------------
    clock.tick(60) #se realiza cada 60 segundos la actualización en pantalla (para animaciones)

    #------ Cambio del fondo de la ventana  -----------------------------------------------------
    screen.blit(backGroundImage, (0,0)) #Cambia los pixeles de la ventana, (recurso, coordenada)

    #------ Actualización y dibujo de sprites ---------------------------------------------------
    robotPlayer.moving()
    robotPlayer.draw(screen)

    #------ Inicialización del salto, para evitar vuelo con tecla sostenida ---------------------
    robotPlayer.UP_KEY = False 

    #------ Manejo de eventos  ------------------------------------------------------------------
    #------ pygame.event.get() obtendrá todos los eventos y los eliminará de la cola ------------
    for event in pygame.event.get():
        #------ el evento es de tipo QUIT cuando se presiona el boton "X" de la ventana ---------
        if event.type == pygame.QUIT:
            playing = False #Se termina el ciclo para permitir el cierre de la ventana
        
        #SE DEBE COMENTAR MEJOR LAS SIGUIENTES LINEAS
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                robotPlayer.LEFT_KEY, robotPlayer.FACING_LEFT = True,True
            elif event.key == pygame.K_RIGHT:
                robotPlayer.RIGHT_KEY, robotPlayer.FACING_LEFT = True,False
            elif event.key == pygame.K_UP:    # se debe reiniciar UP_KEY con False en el ciclo while
                robotPlayer.UP_KEY = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                robotPlayer.LEFT_KEY = False
            elif event.key == pygame.K_RIGHT:
                robotPlayer.RIGHT_KEY = False
            elif event.key == pygame.K_UP:
                robotPlayer.UP_KEY = False
    #------ Actualización grafica de la ventana  ------------------------------------------------
    pygame.display.update() #Actualiza la ventana, al pasar parametro actualiza una porción

pygame.quit() #Desinicializa todos los módulos de pygame que han sido previamente inicializados.
#------------------------------------------------------------------------------------------------
#---------------------------  FIN DEL PROGRAMA --------------------------------------------------
#------------------------------------------------------------------------------------------------