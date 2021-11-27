#------------------------------------------------------------------------------------------------
#------- Videojuego headUP ----------------------------------------------------------------------
#------- Por: Santiago Taborda E   santiago.tabordae@udea.edu.co --------------------------------
#-------      Estudiante de Ingeniería de Telecomunicaciones  -----------------------------------
#-------      CC 1000393907, Wpp 3108983553 -----------------------------------------------------
#------------------------------------------------------------------------------------------------
#-------      Santiago Taborda E   santiago.tabordae@udea.edu.co --------------------------------
#-------      Estudiante de Ingeniería de Telecomunicaciones  -----------------------------------
#-------      CC 1000393907, Wpp 3108983553 -----------------------------------------------------
#------- Curso Básico de Procesamiento de Imágenes y Visión Artificial---------------------------
#------- V2 Abril de 2021------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------
#-- 1. Librerías --------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------
import pygame  #Conjunto de modulos de python diseñado para el desarrollo de videojuegos

#------------------------------------------------------------------------------------------------
#-- 2. Inicialización ---------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------

#Inicialización de pygame
pygame.init()

#---- Se define las dimensiones de la ventana principal del juego -------------------------------
SCREEN_WIDTH = 512  #ancho
SCREEN_HEIGHT = 512  #alto

#---- Se crea la ventana principal del juego ----------------------------------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#creación de la ventana pygame
pygame.display.set_caption('headUpGame')                       #cambio del titulo de la ventana

#---- Se carga la imagen de fondo para la ventana y se configura para mantener la posible -------
#---- transparencia de la imagen png cargada ----------------------------------------------------
backGroundImage = pygame.image.load('./assets/smallBlueNebula.png').convert_alpha()



#------------------------------------------------------------------------------------------------
#-- 3. Logica para el videojuego ----------------------------------------------------------------
#------------------------------------------------------------------------------------------------

#---- Se define el ciclo con el cual se evita el cierre de la ventana principal creada ----------
playing = True #Variable de control para el ciclo mencionado
while playing:
    #------ Cambio del fondo de la ventana  -----------------------------------------------------
    screen.blit(backGroundImage, (0,0)) #Cambia los pixeles de la ventana, (recurso, coordenada)

    #------ Manejo de eventos  ------------------------------------------------------------------
    #------ pygame.event.get() obtendrá todos los eventos y los eliminará de la cola ------------
    for event in pygame.event.get():
        #------ el evento es de tipo QUIT cuando se presiona el boton "X" de la ventana ---------
        if event.type == pygame.QUIT:
            playing = False #Se termina el ciclo para permitir el cierre de la ventana

    #------ Actualización grafica de la ventana  ------------------------------------------------
    pygame.display.update() #Actualiza la ventana, al pasar parametro actualiza una porción

pygame.quit() #Desinicializa todos los módulos de pygame que han sido previamente inicializados.
#------------------------------------------------------------------------------------------------
#---------------------------  FIN DEL PROGRAMA --------------------------------------------------
#------------------------------------------------------------------------------------------------