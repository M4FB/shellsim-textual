registros = []
FILE = "fat_db.txt"

def cargar_registro():
    with open(FILE,"r",encoding="utf-8") as file:
        for linea in file:
            linea = linea.strip()
            print(linea)
            if not linea:
                continue
            partes = [p.strip() for p in linea.split("|")]
            if len(partes)!= 6:
                continue
            registros.append({
                "id": int(partes[0]),
                "nombre": partes[1],
                "tipo": partes[2],
                "padre": int(partes[3]),
                "permisos": partes[4],
                "tamanio": partes[5],
            })
    return registros 

registro = cargar_registro()
hijos = [r for r in registros]
for r in hijos:
    print(r["nombre"])

# print([registros[x]["nombre"] for x in range (10) if registros[x]["tipo"] == "FILE"])