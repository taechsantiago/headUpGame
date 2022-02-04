#-----------------------------------------------------------------------------------------------------
#----------------------------------- 1. Librerías ----------------------------------------------------
#-----------------------------------------------------------------------------------------------------

import cv2
import numpy as np 

#Umbrales de color de acuerdo con el espacio de color YCrCb [Y, Cr, Cb] 
min_YCrCb54 = np.array([80,135,85],np.uint8)   #El valor Y es el color entre (16-235)
max_YCrCb54 = np.array([235,180,135],np.uint8) #El valor Cb Cr es el color entre (16-240)

video = cv2.VideoCapture(0)     # guarda la captura de la webcam en la variable

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))

while True:
    success, frame = video.read() #Se toma del video los valores (imagen) a procesar
    frame = cv2.flip(frame, 1)    #Se utiliza flip para generar el efecto espejo

    frameArea = frame[250:480,380:600] #Se selecciona el area de interes de reconocimiento
    cv2.imshow("imgArea", frameArea)   #Se muestra el area de interés donde se debe ubicar la mano
    cv2.rectangle(frame,(380,250),(600,480),(0,255,0),1) #Se dibuja el area de interes

    image = cv2.cvtColor(frameArea, cv2.COLOR_BGR2YCR_CB)#Se convierte el frame al espacio de color a usar

    #Procesado de color de acuerdo a los umbrales y binarización
    skinMask = cv2.inRange(image, min_YCrCb54, max_YCrCb54) #Se binariza la imagen de acuerdo al umbral
    skinMask = cv2.medianBlur(skinMask, 7)                  #Se utiliza para eliminar ruido excesivo
    cv2.imshow("mask", skinMask)    #BORRAR PARA LA ENTREGA

    #Morfologia 
    #Con el Elemento estructurante ellipse 5x5 para open y close de la imagen
    opening = cv2.morphologyEx(skinMask, cv2.MORPH_OPEN, kernel, iterations=4) #Open
    cv2.imshow("opening", opening) #BORRAR PARA LA ENTREGA

    close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)   #Close
    cv2.imshow("close", close)      #BORRAR PARA LA ENTREGA
    
    #Calculo de contornos
    contours, hierarchy = cv2.findContours(close.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)   

    if len(contours) > 0:   #Se identifica si en el area de interes se ha encontrado contornos
        finger_counting = 0 #Variable que se encarga de contar el número de dedos presentes en pantalla
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
        #esto aplicando el teorema de coseno para calcular el angulo entre dichos puntos menor a 90 es un dedo
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0] #Se recuperan los indices start_index, end_index, farthest_pt_index, fixpt_depth
            start = tuple(hand_segment[s][0]) #Se recuperan los valores indexando el contorno 
            end = tuple(hand_segment[e][0])   #Se recuperan los valores indexando el contorno 
            far = tuple(hand_segment[f][0])   #Se recuperan los valores indexando el contorno 

            #Aplicando la formula de pitagoras se encuentra, a partir de los puntos anteriores, los lados
            a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

            #Aplicando el teorema del coseno se calcula el angulo del triangulo rectangulo supuesto
            angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) #Se obtiene en radianes
            angle = np.degrees(angle) #Se pasa a grados para permitir la distinción de Dedo o no dedo
            angle = int(angle)        #Interesa la parte entera del angulo calculado (se acepta decimal como error)

            #Se hace necesario filtrar los puntos de tal forma que si la distancia entre el punto inicial y el 
            #punto final sea pequeña, no se tome en cuenta para el conteo
            if c > 20 and angle < 90:  # angle less than 90 degree, treat as fingers
                finger_counting += 1
                cv2.circle(frameArea,tuple(start),4,[0, 0, 255],2)
                cv2.circle(frameArea,tuple(end),4,[0, 255, 0],2)
                cv2.circle(frameArea,tuple(far),4,[255, 0, 0],-1)
        if finger_counting > 0:
            finger_counting += 1
        cv2.putText(frameArea, str(finger_counting), (0, 50), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 0, 0) , 2, cv2.LINE_AA)

    key = cv2.waitKey(20) #Espera por 'ESC' para cerrar el programa cada 20
    if key & key == 27:   #Se reconoce que se ha presionado la tecla 'ESC'
        break;            #Se termina el ciclo y por tanto el programa

    cv2.imshow("webcam", frame)  # muestra los fotogramas captados por la camara
    cv2.waitKey(10)              # tiempo entre captura de fotogramas