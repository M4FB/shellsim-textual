from textual.app import App, ComposeResult
from textual.widgets import Tree

def construir_nodos(nodo_padre, id_padre, registros):
    hijos = [r for r in registros if r["padre"] == id_padre]
    for r in hijos:
            if r["tipo"] == "DIR":
                nodo_nuevo = nodo_padre.add(r["nombre"], expand = True) 
                construir_nodos(nodo_nuevo,r["id"], registros)
            else:
                nodo_padre.add_leaf(r["nombre"])



