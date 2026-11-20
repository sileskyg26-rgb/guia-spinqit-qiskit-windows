import csv
import getpass
import math
import os
import time
import traceback
from datetime import datetime

from spinqit import Circuit, H, Ry
from spinqit import get_nmr, get_compiler, NMRConfig

ARCHIVO = "datos_gemini.csv"
MAQUINA = "Gemini (PC-B USB)"

# --- Datos de conexión ---
ip = input("IP [Enter = 192.168.0.100]: ").strip() or "192.168.0.100"
puerto = int(input("Puerto [Enter = 55444]: ").strip() or "55444")
usuario = input("Usuario: ").strip()
clave = getpass.getpass("Clave (no se muestra): ")

# --- Qué circuito y cuántas corridas ---
tipo = (input("Circuito (h / ry) [h]: ").strip().lower() or "h")
grados = 0.0
if tipo == "ry":
    grados = float(input("Ángulo de Ry en grados [60]: ").strip() or "60")
n_corridas = int(input("Cuántas corridas [3]: ").strip() or "3")
shots = 1024


def armar_circuito():
    circ = Circuit()
    q = circ.allocateQubits(1)
    if tipo == "ry":
        circ << (Ry, q[0], math.radians(grados))
    else:
        circ << (H, q[0])
    return circ


def configurar(num):
    config = NMRConfig()
    config.configure_ip(ip)
    config.configure_port(puerto)
    config.configure_account(usuario, clave)
    config.configure_task("corrida_%d" % num, "Prueba %s 1 qubit" % tipo)
    config.configure_shots(shots)
    config.configure_measure_qubits([0])
    return config


nuevo = not os.path.exists(ARCHIVO)
with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if nuevo:
        w.writerow(["fecha_hora", "maquina", "circuito", "grados",
                    "shots", "counts", "probabilities", "segundos"])
    for i in range(1, n_corridas + 1):
        try:
            print("--- Corrida %d de %d ---" % (i, n_corridas), flush=True)
            t0 = time.time()
            comp = get_compiler("native")
            exe = comp.compile(armar_circuito(), 0)
            engine = get_nmr()
            result = engine.execute(exe, configurar(i))
            dt = round(time.time() - t0, 1)
            counts = getattr(result, "counts", None)
            probs = getattr(result, "probabilities", None)
            print("counts:", counts)
            print("probabilities:", probs)
            print("segundos:", dt, flush=True)
            w.writerow([datetime.now().isoformat(timespec="seconds"), MAQUINA,
                        tipo, grados, shots, counts, probs, dt])
            f.flush()
        except Exception as e:
            # No se imprime la clave.
            print("ERROR:", type(e).__name__, str(e))
            traceback.print_exc()
            break

print("Listo. Datos guardados en", os.path.abspath(ARCHIVO))
