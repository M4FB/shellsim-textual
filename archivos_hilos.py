import threading
import time
import random
from datetime import datetime
import os

lock = threading.Lock()
FILE = "fat_db.txt"

# directorio actual (0 = raíz)
GPWD = 0

def _cargar_registros() -> list[dict]:
    """Lee fat_db.txt y devuelve todos los registros como lista de dicts."""
    registros = []
    with lock:
        with open(FILE, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                partes = [p.strip() for p in linea.split("|")]
                if len(partes) != 6:
                    continue
                registros.append({
                    "id":       int(partes[0]),
                    "nombre":   partes[1],
                    "tipo":     partes[2],
                    "padre":    int(partes[3]),
                    "permisos": partes[4],
                    "tamanio":  partes[5],
                })
    return registros


def _guardar_registros(registros: list[dict]) -> None:
    """Sobreescribe fat_db.txt con la lista de registros dada."""
    with lock:
        with open(FILE, "w", encoding="utf-8") as f:
            for r in registros:
                linea = (f"{r['id']} | {r['nombre']} | {r['tipo']} | "
                         f"{r['padre']} | {r['permisos']} | {r['tamanio']}\n")
                f.write(linea)


def _siguiente_id() -> int:
    """Devuelve el próximo ID disponible (max actual + 1)."""
    registros = _cargar_registros()
    if not registros:
        return 1
    return max(r["id"] for r in registros) + 1


# Inicialización del sistema FAT
def inicializar_fat() -> None:
    """Crea fat_db.txt con el directorio raíz si no existe o está vacío."""
    if not os.path.exists(FILE) or os.path.getsize(FILE) == 0:
        with open(FILE, "w", encoding="utf-8") as f:
            f.write("0 | / | DIR | -1 | rwx | -\n")


# Funciones de escritura 
def escritura(id: int, nombre: str, tipo: str, padre: int, permisos: str, tamanio):
    linea = f"{id} | {nombre} | {tipo} | {padre} | {permisos} | {tamanio}\n"
    with lock:
        with open(FILE, "a", encoding="utf-8") as f:
            f.write(linea)


def ejecutar(fn, args: tuple):
    resultado = {}
    hilo = threading.Thread(target=fn, args=(*args, resultado))
    hilo.start()
    hilo.join()
    return resultado


def _imprimir_resultado(resultado: dict) -> str:
    if "error" in resultado:
        return (f"  ✗ {resultado['error']}")
    elif "ok" in resultado:
        return (f"  ✓ {resultado['ok']}")
    elif "salida" in resultado:
        return (resultado["salida"])

#Comandos de navegación y creación
def cmd_mkdir(nombre: str) -> str:
    global GPWD
    registros = _cargar_registros()
    # Verificar que no exista ya un directorio con ese nombre en el directorio actual
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD and r["tipo"] == "DIR":
            return (f"Error: el directorio '{nombre}' ya existe.")
    nuevo_id = _siguiente_id()
    escritura(nuevo_id, nombre, "DIR", GPWD, "rwx", "-")
    return (f"Directorio '{nombre}' creado correctamente.")

def cmd_cd(destino: str) -> str:
    global GPWD
    registros = _cargar_registros()

    if destino == "..":
        if GPWD == 0:
            return ("Ya estás en el directorio raíz.")
        actual = next((r for r in registros if r["id"] == GPWD), None)
        if actual:
            GPWD = actual["padre"]
            ruta = _ruta_actual(registros)
            return (f"Directorio actual cambiado a: {ruta}")

    # Buscar el directorio destino dentro del directorio actual
    for r in registros:
        if r["nombre"] == destino and r["padre"] == GPWD and r["tipo"] == "DIR":
            GPWD = r["id"]
            ruta = _ruta_actual(registros)
            return (f"Directorio actual cambiado a: {ruta}")

    return (f"Error: directorio '{destino}' no encontrado.")


def cmd_touch(nombre: str) -> str:
    global GPWD
    registros = _cargar_registros()
    # Verificar que no exista ya un archivo con ese nombre en el directorio actual
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD and r["tipo"] == "FILE":
            return (f"Error: el archivo '{nombre}' ya existe.")
    nuevo_id = _siguiente_id()
    escritura(nuevo_id, nombre, "FILE", GPWD, "rw-", "0")
    return (f"Archivo '{nombre}' creado correctamente.")


def _ruta_actual(registros: list[dict]) -> str:
    """Construye la ruta absoluta del directorio actual recorriendo padres."""
    partes = []
    nodo = GPWD
    while nodo != 0:
        r = next((x for x in registros if x["id"] == nodo), None)
        if not r:
            break
        partes.append(r["nombre"])
        nodo = r["padre"]
    partes.reverse()
    return "/" + "/".join(partes) if partes else "/"

#Comandos de consulta y modificación
def cmd_ls(detallado: bool = False) -> str:
    registros = _cargar_registros()
    hijos = [r for r in registros if r["padre"] == GPWD]
    if not hijos:
        return("(directorio vacío)")
    
    lineas = []

    if detallado:
        lineas.append(f"{'ID':<4} | {'TIPO':<4} | {'PERMISOS':<8} | {'TAMAÑO':<6} | NOMBRE")
        for r in hijos:
            lineas.append(f"{r['id']:<4} | {r['tipo']:<4} | {r['permisos']:<8} | {r['tamanio']:<6} | {r['nombre']}")
    else:
        for r in hijos:
            lineas.append(r["nombre"])
    return "\n".join(lineas)

def cmd_chmod(permisos: str, nombre: str) -> str:
    if len(permisos) != 3 or not all(c in "rwx-" for c in permisos):
        return ("Error: permisos inválidos. Formato esperado: rwx, r--, rw-, etc.")
    registros = _cargar_registros()
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD:
            r["permisos"] = permisos
            _guardar_registros(registros)
            return (f"Permisos de '{nombre}' cambiados a {permisos}.")
    return (f"Error: '{nombre}' no encontrado en el directorio actual.")

def cmd_rm(nombre: str) -> str:
    registros = _cargar_registros()
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD and r["tipo"] == "FILE":
            registros.remove(r)
            _guardar_registros(registros)
            return (f"Archivo '{nombre}' eliminado correctamente.")
    return (f"Error: archivo '{nombre}' no encontrado en el directorio actual.")

def _crear_archivo_hilo(n: int, mensajes: list) -> None:
    nombre = f"hilo_{n}.txt"
    nuevo_id = _siguiente_id()
    escritura(nuevo_id, nombre, "FILE", GPWD, "rw-", "0")
    mensajes.append(f"Hilo {n} creando archivo {nombre}")

def cmd_test_hilos() -> str:
    mensajes = []
    hilos = [threading.Thread(target=_crear_archivo_hilo, args=(i, mensajes)) for i in range(1, 6)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    return "Iniciando prueba concurrente ...\n" + "\n".join(mensajes) + "\nTodos los hilos finalizaron."

def _mostrar_cabecera() -> str:
    cabecera = []
    cabecera.append("========================================")
    cabecera.append("       SIMULADOR FAT EN PYTHON          ")
    cabecera.append("========================================")
    cabecera.append("Sistema FAT inicializado correctamente.")
    registros = _cargar_registros()
    cabecera.append(f"Directorio actual: {_ruta_actual(registros)}")
    cabecera.append("Comandos disponibles:")
    cabecera.append("  mkdir <nombre>   cd <nombre>   cd ..")
    cabecera.append("  touch <nombre>   ls            ls -l")
    cabecera.append("  chmod <permisos> <nombre>      rm <nombre>")
    cabecera.append("  test_hilos       exit")
    return "\n".join(cabecera)

def main() -> None:
    inicializar_fat()
    _mostrar_cabecera()

    while True:
        registros = _cargar_registros()
        ruta = _ruta_actual(registros)
        try:
            entrada = input(f"\n[{ruta}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo del simulador FAT...")
            break

        if not entrada:
            continue

        partes = entrada.split()
        cmd = partes[0]

        if cmd == "exit":
            print("Saliendo del simulador FAT...")
            break
        elif cmd == "mkdir" and len(partes) == 2:
            print(cmd_mkdir(partes[1]))
        elif cmd == "cd" and len(partes) == 2:
            print(cmd_cd(partes[1]))
        elif cmd == "touch" and len(partes) == 2:
            print(cmd_touch(partes[1]))
        elif cmd == "ls" and len(partes) == 1:
            print(cmd_ls())
        elif cmd == "ls" and len(partes) == 2 and partes[1] == "-l":
            print(cmd_ls(detallado=True))
        elif cmd == "chmod" and len(partes) == 3:
            print(cmd_chmod(partes[1], partes[2]))
        elif cmd == "rm" and len(partes) == 2:
            print(cmd_rm(partes[1]))
        elif cmd == "test_hilos":
            print(cmd_test_hilos())
        else:
            print(f"Comando no reconocido: '{entrada}'")

if __name__ == "__main__":
    main()
