import getpass
import traceback

from spinqit import Circuit, H
from spinqit import get_nmr, get_compiler, NMRConfig

# La Gemini va por USB a la PC-B (Dell), que en la red es 192.168.0.100
ip = input("IP [Enter = 192.168.0.100]: ").strip() or "192.168.0.100"
puerto = int(input("Puerto: ").strip())
usuario = input("Usuario: ").strip()
clave = getpass.getpass("Clave (no se muestra): ")

# Circuito mínimo: 1 qubit y una puerta H.
# En NMR no se usa la puerta MEASURE: la medición se pide con
# configure_measure_qubits.
circ = Circuit()
q = circ.allocateQubits(1)
circ << (H, q[0])

config = NMRConfig()
config.configure_ip(ip)
config.configure_port(puerto)
config.configure_account(usuario, clave)
config.configure_task("prueba_h_1q", "Prueba minima: H en 1 qubit")
config.configure_shots(1024)
config.configure_measure_qubits([0])

try:
    print("PASO: compilando", flush=True)
    comp = get_compiler("native")
    exe = comp.compile(circ, 0)

    print("PASO: enviando a la Gemini", flush=True)
    engine = get_nmr()
    result = engine.execute(exe, config)

    print("PASO: resultado", flush=True)
    print("result:", result)
    print("counts:", getattr(result, "counts", None))
    print("probabilities:", getattr(result, "probabilities", None))
except Exception as e:
    # No se imprime la clave.
    print("ERROR:", type(e).__name__, str(e))
    traceback.print_exc()
