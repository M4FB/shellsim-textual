from textual.app import App, ComposeResult
from textual import events,on
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Placeholder,Input,Log
from datetime import datetime
from archivos_hilos import *
from archivos_hilos import _cargar_registros, _ruta_actual, _mostrar_cabecera

class PlaceholderApp(App):
    CSS_PATH="filesystem.tcss"

    def compose(self) -> ComposeResult:
        registros = _cargar_registros()
        ruta = _ruta_actual(registros)
        with Container(id = "main_container"):
                yield Log(id = "p1")
                with Container (id = "p2"):
                     yield Placeholder(id = "p2a1")
                     yield Placeholder(id = "p2a2")
                     yield Placeholder(id = "p2a3")
                yield Placeholder(id= "p3")
                yield Input(placeholder=f"[{ruta}]>",
                            id = "p4",
                            valid_empty=False)

    def on_ready(self) -> None:
        log = self.query_one(Log)
        log.write_line("Hello World")
        log.write_line(_mostrar_cabecera())

    @on(Input.Submitted) 
    def on_input_submitted(self, event: Input.Submitted) -> None:
        now = datetime.now()
        log = self.query_one(Log)
        log.write_line(str(now) + "]> " + event.value)

        partes = event.value.strip().split()
        cmd = partes[0]

        if cmd == "exit":
            log.write_line("Saliendo del simulador FAT...")
        elif cmd == "mkdir" and len(partes) == 2:
            log.write_line(cmd_mkdir(partes[1]))
        elif cmd == "cd" and len(partes) == 2:
            log.write_line(cmd_cd(partes[1]))
        elif cmd == "touch" and len(partes) == 2:
            log.write_line(cmd_touch(partes[1]))
        elif cmd == "ls" and len(partes) == 1:
            log.write_line(cmd_ls())
        elif cmd == "ls" and len(partes) == 2 and partes[1] == "-l":
            log.write_line(cmd_ls(detallado=True))
        elif cmd == "chmod" and len(partes) == 3:
            log.write_line(cmd_chmod(partes[1], partes[2]))
        elif cmd == "rm" and len(partes) == 2:
            log.write_line(cmd_rm(partes[1]))
        elif cmd == "test_hilos":
            log.write_line(cmd_test_hilos())
        else:
            log.write_line(f"Comando no reconocido: '{event.value}'")



        event.input.clear()

#zapatos bisturi
if __name__ == "__main__":
    app = PlaceholderApp()
    app.run()