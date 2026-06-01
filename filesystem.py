from textual.app import App, ComposeResult
from textual import events,on
from textual.containers import Container 
from textual.widgets import Input,Log,Tree,Placeholder
from datetime import datetime
from archivos_hilos import *
from archivos_hilos import _cargar_registros, _ruta_actual, _mostrar_cabecera
from tests.tree import construir_nodos

class PlaceholderApp(App):
    CSS_PATH="filesystem.tcss"

    def compose(self) -> ComposeResult:
        registros = _cargar_registros()
        ruta = _ruta_actual(registros)
        
        #Parte del arbol de carpetas
        raiz = next(r for r in registros if r["padre"] == -1)
        tree: Tree[str] = Tree(raiz["nombre"])
        tree.root.expand()
        construir_nodos(tree.root, raiz["id"],registros)

        with Container(id = "main_container"):
                yield Log(id = "p1")
                with Container (id = "p2"):
                    yield tree
                yield Log(id= "p3")
                yield Input(placeholder=f"[{ruta}]>",
                            id = "p4",
                            valid_empty=False)
    
    def _update_tree(self) -> None:
        registros = _cargar_registros()        
        raiz = next(r for r in registros if r["padre"] == -1)
        tree = self.query_one(Tree)
        tree.clear()
        tree.root.expand()
        construir_nodos(tree.root, raiz["id"],registros)

    def on_ready(self) -> None:
        log = self.query_one("#p1",Log)
        log.write_line(_mostrar_cabecera())

        log = self.query_one("#p3",Log)
        log.write_line("Marcelo Avendaño Fernandez Baca")
        log.write_line("Cod: 2023800251")
         
    @on(Input.Submitted) 
    def on_input_submitted(self, event: Input.Submitted) -> None:
        registros = _cargar_registros()
        ruta = _ruta_actual(registros)
        inputUsed = self.query_one(Input)
        inputUsed.placeholder = f"[{ruta}]>"
        log = self.query_one(Log)
        log.write_line("[" + str(ruta) + "]> " + event.value)
        



        partes = event.value.strip().split()
        cmd = partes[0]

        if cmd == "exit":
            log.write_line("Saliendo del simulador FAT...")
        elif cmd == "mkdir" and len(partes) == 2:
            log.write_line(cmd_mkdir(partes[1]))
            self._update_tree()
        elif cmd == "cd" and len(partes) == 2:
            log.write_line(cmd_cd(partes[1]))
            self._update_tree()
        elif cmd == "touch" and len(partes) == 2:
            log.write_line(cmd_touch(partes[1]))
            self._update_tree()
        elif cmd == "ls" and len(partes) == 1:
            log.write_line(cmd_ls())
        elif cmd == "ls" and len(partes) == 2 and partes[1] == "-l":
            log.write_line(cmd_ls(detallado=True))
        elif cmd == "chmod" and len(partes) == 3:
            log.write_line(cmd_chmod(partes[1], partes[2]))
        elif cmd == "rm" and len(partes) == 2:
            log.write_line(cmd_rm(partes[1]))
            self._update_tree()
        elif cmd == "test_hilos":
            log.write_line(cmd_test_hilos())
        else:
            log.write_line(f"Comando no reconocido: '{event.value}'")

        event.input.clear()

if __name__ == "__main__":
    app = PlaceholderApp()
    app.run()
