#------------------------------------------------------------------------------------------------
#------- Videojuego headUP ----------------------------------------------------------------------
#------- Por: Santiago Taborda E   santiago.tabordae@udea.edu.co --------------------------------
#-------      Estudiante de Ingeniería de Telecomunicaciones  -----------------------------------
#-------      CC 1000393907, Wpp 3108983553 -----------------------------------------------------
#------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
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
from platform import platform
from wsgiref.util import request_uri
import pygame      #Conjunto de modulos de python diseñado para el desarrollo de videojuegos
import json        #Modulo de python para el manejo de datos de formato JSON
import numpy as np #Librería fundamental para la computación científica en Python
from scipy.spatial import distance #Función de la biblioteca scipy para el calculo de distancia 

#------------------------------------------------------------------------------------------------
#-- 2. Inicialización ---------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
pygame.init()               #Inicialización de pygame
clock = pygame.time.Clock() #inicialización del reloj, util para las animaciones y actualización

#---- Se define las dimensiones de la ventana principal del juego -------------------------------
SCREEN_WIDTH = 1024  #ancho
SCREEN_HEIGHT = 1000 #alto

#---- Se definen las VARIABLES Y CONSTANTES del juego --------------------------------------------
FPS = 80                #Constante que controla los frames por segundo para actualizar pantalla
GRAVITY = 1             #Constante que simula la gravedad para el movimiento fisico
WHITE = (255, 255, 255) #Constante de color
PLATFOR_NUMBER = 10     #Constante que permite decidir el número de plataformas en pantalla
SCROLLING_LIMIT = 300   #Constante para determinar cuando se activa el desplazamiento de pantalla
Scrolling = 0           #No es una constante, desplaza las plataformas
Scrolling_PlfPosy = []  #No es una constante, permite evitar que las plataformas se generen con
                        #una misma coordenada de acuerdo al eje Y

#---- Se crea la ventana principal del juego ----------------------------------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#creación de la ventana pygame
pygame.display.set_caption('headUpGame')                       #cambio del titulo de la ventana

#---- Se cargan las imagenes y se configura para mantener la posible transparencia de la --------
#---- imagen png cargada ------------------------------------------------------------------------
backGroundImage = pygame.image.load('./assets/background/space2.jpg').convert_alpha()#Fondo
platformImage = pygame.image.load('./assets/platform/Tile.png').convert_alpha()#Plataformas

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

    def draw(self, display):
        #---- Actualización del personaje en la pantalla ------------------------------------------
        #Se utilizan las coordenadas del rectangulo para el dibujo del personaje con un offset
        #el offset evita problemas de colisión, es el rectangulo el que se toma en cuenta
        #screen.blit(image, (rect.x-offset['x'], rect.y-offset['y']))
        display.blit(self.currentImage, (self.rect.x-self.offsetX, self.rect.y-self.offsetY))

        #BORRAR SIGUIENTE LINEA PARA ENTREGAR
        pygame.draw.rect(display, WHITE, self.rect, 2)#se dibuja el rectangulo BORRAR PARA ENTREGAR

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
        
        if self.rect.bottom+self.velocityY > SCREEN_HEIGHT:
            self.velocityY = -20

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

        return Scrolling

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
                    
                    self.rect.update(self.rect.x, self.rect.y, self.idleLeftRects[self.currentFrame][0], self.idleLeftRects[self.currentFrame][1])
                    self.offsetX = self.idleLeftOffset[self.currentFrame]['x']
                    self.offsetY = self.idleLeftOffset[self.currentFrame]['y']

                elif not self.FACING_LEFT:
                    self.currentImage = self.idleRightFrames[self.currentFrame]
                    
                    self.rect.update(self.rect.x, self.rect.y, self.idleRightRects[self.currentFrame][0], self.idleRightRects[self.currentFrame][1])                    
                    self.offsetX = self.idleRightOffset[self.currentFrame]['x']
                    self.offsetY = self.idleRightOffset[self.currentFrame]['y']

        elif (self.state == 'jumping left'):
            #para el salto se hace cada 100 milisegundos para una actualización
            #más fluida para el movimiento de salto
            if ((currentTime - self.lastFrame) > 150):
                self.lastFrame = currentTime
                self.currentFrame = ((self.currentFrame+1)%len(self.jumpLeftFrames))
                self.currentImage = self.jumpLeftFrames[self.currentFrame]
                self.rect.update(self.rect.x, self.rect.y, self.jumpLeftRects[self.currentFrame][0], self.jumpLeftRects[self.currentFrame][1])
                self.offsetX = self.jumpLeftOffset[self.currentFrame]['x']
                self.offsetY = self.jumpLeftOffset[self.currentFrame]['y']

        elif (self.state == 'jumping right'):
            #para el salto se hace cada 100 milisegundos para una actualización
            #más fluida para el movimiento de salto
            if ((currentTime - self.lastFrame) > 150):
                self.lastFrame = currentTime
                self.currentFrame = ((self.currentFrame+1)%len(self.jumpRightFrames))
                self.currentImage = self.jumpRightFrames[self.currentFrame]
                self.rect.update(self.rect.x, self.rect.y, self.jumpRightRects[self.currentFrame][0], self.jumpRightRects[self.currentFrame][1])
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

                    self.rect.update(self.rect.x, self.rect.y, self.walkLeftRects[self.currentFrame][0], self.walkLeftRects[self.currentFrame][1])
                    self.offsetX = self.walkLeftOffset[self.currentFrame]['x']
                    self.offsetY = self.walkLeftOffset[self.currentFrame]['y']

                elif self.state == 'moving right':
                    self.currentImage = self.walkRightFrames[self.currentFrame]

                    self.rect.update(self.rect.x, self.rect.y, self.walkRightRects[self.currentFrame][0], self.walkRightRects[self.currentFrame][1])
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


#------------------------------------------------------------------------------------------------
#-- 5. Plataformas ------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

#---- Clase para la creación de cada plataforma como objeto -------------------------------------
class Platform(pygame.sprite.Sprite): 
    #Se hace uso de pygame.sprite.Sprite que facilita tanto las colisiones como el movimiento y
    #el manejo de sprites (cambios y transiciones). para este caso se puede usar los grupos de 
    #pygame que optimizan la utilización recursiva de la clase

    #---- Inicialización de la plataforma -------------------------------------------------------
    def __init__(self, x, y, width): 
        pygame.sprite.Sprite.__init__(self) #constructor de la clase padre

        #se carga la imagen que se utiliza para la plataforma, con longitud variable
        self.image = pygame.transform.scale(platformImage, (width, 30)) 
        self.rect = self.image.get_rect()#se obtiene el rectangulo para la imagen correspondiente

        #Inicialización de coordenadas xy para la plataforma
        self.rect.x = x
        self.rect.y = y

    def update(self, Scrolling):
        self.rect.y += Scrolling              #El movimiento de las plataformas se hace en Y

        #Verificación para determinar si se debe eliminar una plataforma cuando sale de pantalla
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()                       #Se elimina la plataforma al salir de pantalla

#---- Función para garantizar que el espacio entre plataforma sea el adecuado -------------------
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
            if abs(prevRightEdge-nextLeftEdge) > 190: 
                nextCoordX = np.random.randint(100, SCREEN_WIDTH-nextWidth-10) #Se calcula una nueva coord
            else:
                control = False #Si no supera la distancia, se puede terminar el ciclo
        else:
            prevLeftEdge  = prevCoordX           #Coordenada lado izquierdo, plataforma anterior
            nextRightEdge = nextCoordX+prevWidth #Coordenada lado derecho, plataforma siguiente
            #La distancia entre las coordenadas anteriores no debe superar 100
            if abs(prevLeftEdge-nextRightEdge) > 190:
                nextCoordX = np.random.randint(100, SCREEN_WIDTH-nextWidth-10) #Se calcula una nueva coord
            else:
                control = False #Si no supera la distancia, se puede terminar el ciclo
    return nextCoordX #Se retorna la coordenada X que cumple las consideraciones

#------------------------------------------------------------------------------------------------
#-- 6. Instancias -------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
robotPlayer = Player() #Creación del personaje

#---- Creación de plataformas -------------------------------------------------------------------
platformsGroup = pygame.sprite.Group()#Instancia del uso de pygame groups

#Plataforma inicial con coordenadas aproximadamente en la mitad de la ventana
platformI = Platform((SCREEN_WIDTH-150)//2, SCREEN_HEIGHT-100, 150)
Scrolling_PlfPosy.append(SCREEN_HEIGHT-100)#Se agrega la coordenada de la plataforma inicial
platformsGroup.add(platformI)        #Se agrega la plataforma creada al grupo de plataformas

#------------------------------------------------------------------------------------------------
#-- 8. Funcionamiento e integración -------------------------------------------------------------
#------------------------------------------------------------------------------------------------

#---- Se define el ciclo con el cual se evita el cierre de la ventana principal creada ----------
playing = True #Variable de control para el ciclo mencionado
while playing:
    #------ Actualización del reloj por frame ---------------------------------------------------
    clock.tick(FPS) #se realiza cada 60 segundos la actualización en pantalla (para animaciones)

    #------ Cambio del fondo de la ventana con desplazamiento -----------------------------------
    screen.blit(backGroundImage, (0,0))
    
    #------ Actualización y dibujo de personaje -------------------------------------------------
    Scrolling = robotPlayer.moving()
    robotPlayer.draw(screen)

    #------ Creación de las plataformas ---------------------------------------------------------
    if len(platformsGroup) < PLATFOR_NUMBER:
        platformWidth = np.random.randint(150,250) #Se genera un tamaño aleatorio

        #Se asegura el espaciamiento no supera el alcance del salto con la función xCoordinate
        platformX = np.random.randint(50, SCREEN_WIDTH-platformWidth-10)
        platformX = xCoordinate(platformI, platformX, platformWidth)
        
        #Apartir de la ultima plataforma creada se genera una nueva coordenada Y
        platformY = platformI.rect.y - np.random.randint(200,300)
        
        platformI = Platform(platformX, platformY, platformWidth)#Se crea una plataforma
        platformsGroup.add(platformI)                            #Se agrega plataforma al grupo  

    #------ Actualización y dibujo de plataformas -----------------------------------------------
    platformsGroup.update(Scrolling)
    platformsGroup.draw(screen)

    #------ Inicialización del salto, para evitar vuelo con tecla sostenida ---------------------
    robotPlayer.UP_KEY = False 

    #------ Manejo de eventos  ------------------------------------------------------------------
    #------ pygame.event.get() obtendrá todos los eventos y los eliminará de la cola ------------
    for event in pygame.event.get():
        #------ el evento es de tipo QUIT cuando se presiona el boton "X" de la ventana ---------
        if event.type == pygame.QUIT:
            playing = False #Se termina el ciclo para permitir el cierre de la ventana     
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

    #------ Actualización grafica de la ventana  ------------------------------------------------
    pygame.display.update() #Actualiza la ventana, al pasar parametro actualiza una porción

pygame.quit() #Desinicializa todos los módulos de pygame que han sido previamente inicializados
#------------------------------------------------------------------------------------------------
#---------------------------  FIN DEL PROGRAMA --------------------------------------------------
#------------------------------------------------------------------------------------------------