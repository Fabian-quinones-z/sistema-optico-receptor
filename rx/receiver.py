import cv2
import numpy as np

<<<<<<< HEAD
from common.config import *

from rx.sync import detectar_sync
from rx.motion import detectar_cambio
from rx.demodulation import demodular_frame
from rx.geometry import erosionar_bits, detectar_lienzo
from rx.equalizador import *

cap = cv2.VideoCapture(
    VIDEO_FILE
)
=======
from rx.config_rx import *
from rx.sync import detectar_sync
from rx.motion import detectar_cambio
from rx.geometry import erosionar_bits

from rx.cuadrado import ordenar_esquinas

from rx.signal import es_pulso_valido 
from rx.demodulation import demodular_frame

cap = cv2.VideoCapture(0)  #VIDEO_FILE)   #0) # cambiamos entre video archivo y camara*(0)
>>>>>>> 7e98f76dff979d5ab70aeda61bff2ab6b8b3f77b

estado0 = None
estado1 = None

<<<<<<< HEAD
sync_realizado = False
=======
def equalizar(gris):
    """Versión optimizada para comunicación óptica"""
    kernel = np.array([[1, 0, 1],
                       [0, 1, 1],
                       [0, 1, 0]], dtype=np.uint8)
    
    gris = cv2.bilateralFilter(gris, 8, 170, 180)
    gris = cv2.medianBlur(gris, 3)
    #input("pausa")
    
    clahe = cv2.createCLAHE(clipLimit=4.3, tileGridSize=(4, 4))
    gris = clahe.apply(gris)
    gris = cv2.morphologyEx(gris, cv2.MORPH_CLOSE, kernel)
    
    gris = cv2.normalize(gris, None, 30, 124, cv2.NORM_MINMAX)
    
    return gris
>>>>>>> 7e98f76dff979d5ab70aeda61bff2ab6b8b3f77b

roi_lienzo = None

lienzo_referencia = None

mensaje_completo = ""

print("\n" + "="*60)
print("RECEPTOR OPTICO")
print("SYNC POR CAMBIO DE ESTADO")
print("="*60)
estado0 = None
estado1 = None

sync_realizado = False

roi_lienzo = None
lienzo_referencia = None

<<<<<<< HEAD
resta_canal = None
=======
    h, w = diff.shape
    area_total = h * w
    
    kernel = np.ones((4, 4), np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, kernel, iterations=2)
>>>>>>> 7e98f76dff979d5ab70aeda61bff2ab6b8b3f77b

mensaje_completo = ""
maxScore=0
score=0
relacion=[]

contadorframes=0 
framesbandera=[]
diferencia=[]
while True:
    #Capturar fotograma
    ret, frame = cap.read()

    if not ret:
        break
    # Definir Area(R) de(O) Interés (I) 
    roi = frame[
        ROI_Y1:ROI_Y2,
        ROI_X1:ROI_X2
    ]

    roi = cv2.resize(
        roi,
        ROI_SIZE
    )
    #Colorear 
    gris = cv2.cvtColor(
        roi,
        cv2.COLOR_BGR2GRAY
    )
    #Equalizar 
    if USE_OTSU:

        gris_eq = equalizar(
            gris
        )

        _, binaria = cv2.threshold(
            gris_eq,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

    else:

        _, binaria = cv2.threshold(
            gris,
            THRESHOLD_BINARIO,
            255,
            cv2.THRESH_BINARY
        )

    kernel = np.ones(
        (2,2),
        np.uint8
    )
    #Binarizar
    binaria = cv2.morphologyEx(
        binaria,
        cv2.MORPH_OPEN,
        kernel
    )

    score, maxScore, diff_mov = detectar_cambio(
        binaria, maxScore
    )
    blancos = np.count_nonzero(diff_mov)
    try:
        total = diff_mov.size
    except:
        total=1
    relacion.append(blancos / total)
    
    contadorframes = contadorframes+1
    if relacion[-1] > 0.23:
        print(f"SYNC DETECTADO {relacion[-1] }")
        framesbandera.append(contadorframes)
        try: 
            diferencia.append(contadorframes-framesbandera[-2])
        except:
            diferencia.append(0)
        print(f"{framesbandera} - {diferencia}")
        #Verificar que sea la tercera bandera similar a las dos anteriores y que los tiempos entre frames sean similares 
        
        if len(framesbandera) >= 3:

         d1 = diferencia[-1]
         d2 = diferencia[-2]

         tolerancia = 5
         
         if d2 > 0:

            ratio = d1 / d2

            if 0.85 <= ratio <= 1.15:

                print("ambas diferencias se parecen")

                print(
                    f"valor absoluto = "
                    f"{abs(d1-d2)}"
                )

                print("\nSYNC PERIODICO CONFIRMADO")

                print(
                    f"Banderas: "
                    f"{framesbandera[-3:]}"
                )

                print(
                    f"Periodos: "
                    f"{d1}, {d2}"
                )

                periodo_sync = int(
                    (d1+d2)/2
                )

                frame_sync = framesbandera[-1]

                print(
                    f"Periodo estimado: "
                    f"{periodo_sync}"
                )

                print(
                    f"Frame referencia: "
                    f"{frame_sync}"
                )
                roi_lienzo = detectar_lienzo(diff_mov)
                print("lienzo detectado!")
                if roi_lienzo is not None:
                    try: 
                     xold,yold,  wold,hold=(x,y,w,h)
                    except:
                     pass   
                    x,y,w,h = roi_lienzo
                    #hacer un asnálisi de la varianza 
                    lienzo_referencia = diff_mov[
                        y:y+h,
                        x:x+w
                    ].copy()
                    cv2.imshow("Ref",lienzo_referencia)
                    sync_realizado = True

                    print(
                        f"log ROI FIJADO {roi_lienzo}"
                    )
                
        
        
                sync_realizado = True
    # ==================================================
    # DEBUG
    # ==================================================

    debug = roi.copy()

    cv2.putText(
        debug,
        f"S={score}",
        (10,20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0,255,0),
        2
    )

    if roi_lienzo is not None:

        x,y,w,h = roi_lienzo

        cv2.rectangle(
            debug,
            (x,y),
            (x+w,y+h),
            (255,0,0),
            2
        )

        cv2.putText(
            debug,
            "LIENZO",
            (x,y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255,0,0),
            2
        )

    cv2.imshow(
        "RECEPTOR",
        debug
    )

    cv2.imshow(
        "BINARIA",
        binaria
    )

    if diff_mov is not None:

        cv2.imshow(
            "MOVIMIENTO",
            diff_mov
        )

    if sync_realizado:

        cv2.imshow(
            "LIENZO",
            lienzo_referencia
        )
        if (
                resta_canal is not None
                and
                resta_canal.size > 0
            ):
            cv2.imshow(
            "RESTA",
            resta_canal
            )
    
    tecla = cv2.waitKey(30)

    if tecla == 27:
        break


print()
print("="*60)
print("MENSAJE FINAL")
print("="*60)
print(mensaje_completo)

cap.release()

#print(f" _maxScore: {maxScore}")
#print(f" relacion {relacion}")

cv2.destroyAllWindows()
