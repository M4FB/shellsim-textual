from textual.app import App, ComposeResult
from textual.widgets import Tree


class TreeApp(App):
    def cargar_registro(self):
        registros = []
        FILE = "fat_db.txt"

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

    def _construir_nodos(self, nodo_padre, id_padre, registros):
        hijos = [r for r in registros if r["padre"] == id_padre]
        for r in hijos:
                if r["tipo"] == "DIR":
                    nodo_nuevo = nodo_padre.add(r["nombre"], expand = True) 
                    self._construir_nodos(nodo_nuevo,r["id"], registros)
                else:
                    nodo_padre.add_leaf(r["nombre"])
                    
    def compose(self) -> ComposeResult:
        registro = self.cargar_registro()
        raiz = next(r for r in registro if r["padre"] == -1)
        tree: Tree[str] = Tree(raiz["nombre"])
        tree.root.expand()
        self._construir_nodos(tree.root, raiz["id"],registro)
        yield tree


if __name__ == "__main__":
    app = TreeApp()
    app.run()