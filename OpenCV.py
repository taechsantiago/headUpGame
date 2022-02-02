#-----------------------------------------------------------------------------------------------------
#----------------------------------- 1. Librerías ----------------------------------------------------
#-----------------------------------------------------------------------------------------------------

import cv2
import numpy as np 

# Lower es el umbral bajo del color seleccionado, Upper es el umbral superior, esto otorga cierta flexibilidad
lower = np.array([15,150,20])   #[HUE, SATURATION, VALUE] el primero valor es el color entre (0-180)
upper = np.array([35,255,255])  #el segundo valor es que tanta saturación de color se espera (de 150 a 255 es el ideal)
                                #el tercer valor es la referencia al brillo del color selección

video = cv2.VideoCapture(0)     # guarda la captura de la webcam en la variable

while True:
  success, img = video.read()   # toma de valores del video capturado
  image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  #conversión de la imagen tomada por la camara a HSV
  mask = cv2.inRange(image, lower, upper)       #encuentra el color escogido en las imagenes de la camara


  #----------------------------------------- 2. contorno de la figura ---------------------------------------------
  #
  # las siguienets encuentra las coordenadas del color detectado, CHAIN_APPROX_SIMPLE permite tomar los puntos necesarios
  # del contorno no toma cada punto de las coordenadas, RETR_EXTERNAL toma el contorno externo de la forma con el color

  contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  

  if len(contours) != 0:
    for contour in contours:
      if cv2.contourArea(contour) > 30000:
        print("jump")

      if cv2.contourArea(contour) > 1000:        # evita que se pinte el contorno de fragmentos con areas muy pequeñas
        x, y, w, h = cv2.boundingRect(contour)  # genera rectangulo de contorno de la forma
        cv2.rectangle(img, (x,y), (x + w, y + h), (0, 0, 255), 3) # muestra el rectangulo en pantalla

        if x<150:               # umbrales de decisión para el movimiento horizontal
          print('izquierda')
        elif x>300:
          print('derecha')
        else:
          print('medio')

  #-------- se puede borrar luego de terminado -------------------------------------
  #cv2.imshow("mask", mask)    # muestra en pantalla la identificación del color
  cv2.imshow("webcam", img)   # muestra los fotogramas captados por la camara

  cv2.waitKey(10)              # tiempo entre captura de fotogramas

