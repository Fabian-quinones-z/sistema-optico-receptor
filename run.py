import os , subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

def ejecutar(modulo):
    subprocess.run(
        [sys.executable, "-m", modulo],
        check=False
    )

while True:

    print("\n========== OPTICAL MODEM ==========")
    print("1. Transmitir")
    print("2. Recibir")
    print("3. Test librerías")
    print("4. Test render")
    print("5. Test cámara")
    print("6. Test imagen estática")
    print("7. Test video")
    print("8. Test realtime")
    print("9. Setup")
    print("0. Salir")

    accion = input("\nOpción: ")

    if accion == "1":
        ejecutar("tx.transmitter")

    elif accion == "2":
        ejecutar("rx.receiver")

    elif accion == "3":
        ejecutar("tests.librerias")

    elif accion == "4":
        ejecutar("tests.render")

    elif accion == "5":
        ejecutar("tests.cam")

    elif accion == "6":
        ejecutar("tests.static_image_test")

    elif accion == "7":
        ejecutar("tests.video_test")

    elif accion == "8":
        ejecutar("tests.realtime_test")

    elif accion == "9":
        os.system("bash scripts/setup.sh")

    elif accion == "0":
        break

    else:
        print("Opción inválida")
