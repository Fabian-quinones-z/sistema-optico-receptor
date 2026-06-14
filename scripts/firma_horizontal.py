import numpy as np

def firma_horizontal(img):

    perfil = np.mean(
        img,
        axis=0
    )

    mitad = len(perfil) // 2

    izquierda = np.mean(
        perfil[:mitad]
    )

    derecha = np.mean(
        perfil[mitad:]
    )

    return izquierda, derecha
