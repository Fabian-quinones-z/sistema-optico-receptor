import numpy as np
import cv2

def calcular_psd(diff):
    """Densidad espectral de potencia"""
    proyeccion = np.sum(diff, axis=0)
    if len(proyeccion) == 0 or np.sum(proyeccion) == 0:
        return np.array([0])
    
    fft = np.fft.fft(proyeccion)
    psd = np.abs(fft[:len(fft)//2])**2
    if np.max(psd) > 0:
        psd = psd / np.max(psd)
    return psd


def frecuencia_dominante(diff, fps=30):
    """Frecuencia dominante del pulso"""
    proyeccion = np.sum(diff, axis=0)
    
    if len(proyeccion) == 0 or np.sum(proyeccion) == 0:
        return 0
    
    fft = np.fft.fft(proyeccion)
    frecuencias = np.fft.fftfreq(len(proyeccion), d=1/fps)
    magnitud = np.abs(fft[1:len(fft)//2])
    
    if len(magnitud) > 0 and np.max(magnitud) > 0:
        idx = np.argmax(magnitud)
        return abs(frecuencias[1:][idx])
    return 0


def es_pulso_valido(diff, score):
    """Versión simple: valida por score y área"""
    if diff is None or score < 100:
        return False
    
    h, w = diff.shape
    area_total = h * w
    proporcion = score / area_total
    
    # Pulso válido: entre 5% y 60% del área
    return 0.05 < proporcion < 0.60
