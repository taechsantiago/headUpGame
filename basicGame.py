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
SCREEN_WIDTH = 400   #ancho
SCREEN_HEIGHT = 600  #alto

#---- Se crea la ventana principal del juego ----------------------------------------------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#creación de la ventana pygame
pygame.display.set_caption('headUpGame')                       #cambio del titulo de la ventana

#---- Se define el ciclo con el cual se evita el cierre de la ventana principal creada ----------
playing = True #Variable de control para el ciclo mencionado
while playing:
    #------ Manejo de eventos  ------------------------------------------------------------------
    #------ pygame.event.get() obtendrá todos los eventos y los eliminará de la cola ------------
    for event in pygame.event.get():
        #------ el evento es de tipo QUIT cuando se presiona el boton "X" de la ventana ---------
        if event.type == pygame.QUIT:
            playing = False #Se termina el ciclo para permitir el cierre de la ventana

pygame.quit() #Desinicializa todos los módulos de pygame que han sido previamente inicializados.
#------------------------------------------------------------------------------------------------
#---------------------------  FIN DEL PROGRAMA --------------------------------------------------
#------------------------------------------------------------------------------------------------