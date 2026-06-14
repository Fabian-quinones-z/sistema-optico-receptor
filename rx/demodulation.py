import cv2
import numpy as np

def muestrear_grid(binaria, grid_size=8):
    """
    Muestrea la imagen binaria en una grid de grid_size x grid_size
    
    Retorna: matriz de bits (0 o 1)
    """
    h, w = binaria.shape
    cell_h = h // grid_size
    cell_w = w // grid_size
    
    bits = np.zeros((grid_size, grid_size), dtype=np.uint8)
    
    for i in range(grid_size):
        for j in range(grid_size):
            # Area de cada celda
            y1 = i * cell_h
            y2 = (i + 1) * cell_h
            x1 = j * cell_w
            x2 = (j + 1) * cell_w
            
            # Extraer celda
            celda = binaria[y1:y2, x1:x2]
            
            # Promedio de blancos (255) vs negros (0)
            promedio = np.mean(celda)
            
            # Si mas del 50% es blanco -> 1, sino 0
            bits[i, j] = 1 if promedio > 127 else 0
    
    return bits



def demodular_frame(binaria_rectificada, debug=False):
    """
    Demodula un frame rectificado a bits y luego a texto
    """
    # 1. Muestrear grid 8x8
    bits = muestrear_grid(binaria_rectificada)
    
    if debug:
        print("\n📊 Bits detectados (8x8):")
        for i in range(8):
            fila = bits[i]
            print(f"   Fila {i}: {''.join(str(b) for b in fila)}")
    
    # 2. Convertir bits a texto
    texto, bytes_data = bits_a_texto(bits)
    
    return bits, texto, bytes_data


def bits_a_texto(bits_array, invertir=False, revertir_byte=False):
    """Convierte matriz de bits 8x8 a texto"""
    bits_plano = bits_array.flatten()
    
    if invertir:
        bits_plano = 1 - bits_plano
    
    bytes_data = []
    for i in range(0, 64, 8):
        byte_val = 0
        if revertir_byte:
            # Leer bits al revés (de derecha a izquierda)
            for j in range(7, -1, -1):
                if i + j < 64:
                    byte_val = (byte_val << 1) | int(bits_plano[i + j])
        else:
            # Lectura normal
            for j in range(8):
                if i + j < 64:
                    byte_val = (byte_val << 1) | int(bits_plano[i + j])
        bytes_data.append(byte_val)
    
    # Mostrar bytes para debug
    print(f"Bytes decodificados: {bytes_data}")
    
    texto = ''.join(chr(b) for b in bytes_data if 32 <= b <= 126)
    
    return texto, bytes_data
