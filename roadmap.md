
  ---
  # El problema central
  
  **filesystem.py** ya importa todo de archivos_hilos.py, pero hay un mismatch fundamental: todas las funciones cmd_* usan print(), y el TUI necesita escribir en el widget Log. Eso es lo que
  hay que resolver primero, el resto cae solo.

  ---
  ## Roadmap

  Paso 1 — Refactorizar las funciones cmd_* para que devuelvan strings

  Hoy hacen print(...) y devuelven None. Hay que cambiarlas para que devuelvan el texto:

  # ANTES
  def cmd_mkdir(nombre):
      ...
      print(f"Directorio '{nombre}' creado.")

  # DESPUÉS
  def cmd_mkdir(nombre) -> str:
      ...
      return f"Directorio '{nombre}' creado."

  Esto afecta: cmd_mkdir, cmd_cd, cmd_touch, cmd_ls, cmd_chmod, cmd_rm, cmd_test_hilos. La función main() en archivos_hilos.py simplemente pasa a hacer print(cmd_mkdir(...)) para no
  romper el CLI existente.

  ---
  Paso 2 — Arreglar _mostrar_cabecera()

  filesystem.py:29 hace log.write_line(_mostrar_cabecera()), pero esa función devuelve None (usa print). Misma solución: que devuelva un string multi-línea.

  ---
  Paso 3 — Completar el handler de comandos en filesystem.py
  
  Hoy solo maneja cd. Hay que agregar todos los comandos, siguiendo el mismo patrón que ya existe:

  @on(Input.Submitted)
  def on_input_submitted(self, event):
      ...
      resultado = ""
      if cmd == "cd" and len(partes) == 2:
          resultado = cmd_cd(partes[1])
          # actualizar placeholder del input
      elif cmd == "mkdir" and len(partes) == 2:
  Paso 3 — Completar el handler de comandos en filesystem.py

  Hoy solo maneja cd. Hay que agregar todos los comandos, siguiendo el mismo patrón que ya existe:

  @on(Input.Submitted)
  def on_input_submitted(self, event):
      ...
      resultado = ""
      if cmd == "cd" and len(partes) == 2:
          resultado = cmd_cd(partes[1])
          # actualizar placeholder del input
      elif cmd == "mkdir" and len(partes) == 2:
          resultado = cmd_mkdir(partes[1])
      elif cmd == "ls":
          resultado = cmd_ls(detallado=len(partes) == 2)
      # ... etc

      log.write_line(resultado)

  ---
  Paso 4 — Manejar cmd_test_hilos en el TUI

  cmd_test_hilos lanza threads que actualmente hacen print(). Para el TUI, los threads no pueden escribir directo al widget. Necesitás usar app.call_from_thread():

  def _crear_archivo_hilo(n, app, log):
      nombre = f"hilo_{n}.txt"
      # ... escritura ...
      app.call_from_thread(log.write_line, f"Hilo {n} creó {nombre}")

  Esto es el único caso donde hay que pasar referencias del TUI hacia la lógica — o bien que cmd_test_hilos devuelva un generador de mensajes y el TUI los muestre.

  ---
  Paso 5 — Definir qué van los 3 Placeholder de p2

  Ahora mismo son placeholders vacíos (p2a1, p2a2, p2a3). Opciones naturales:
  - p2a1: árbol de directorios (reactivo al GPWD)
  - p2a2: detalles del archivo seleccionado 
  - p2a3: stats del sistema (total archivos, directorios, etc.)

  Eso sí, para que sean reactivos van a necesitar que GPWD dispare un evento cuando cambia — lo más limpio es que filesystem.py llame a refresh() o use reactive de Textual.

  ---
  Resumen de cambios por archivo
  
  ┌───────────────────────────────────────────────┬───────────────────┬────────────────┐
  │                      Qué                      │  En qué archivo   │ Tipo de cambio │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ cmd_* devuelven str en vez de print           │ archivos_hilos.py │ Refactor       │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ _mostrar_cabecera() devuelve str              │ archivos_hilos.py │ Refactor       │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  - p2a3: stats del sistema (total archivos, directorios, etc.)

  Eso sí, para que sean reactivos van a necesitar que GPWD dispare un evento cuando cambia — lo más limpio es que filesystem.py llame a refresh() o use reactive de Textual.

  ---
  Resumen de cambios por archivo

  ┌───────────────────────────────────────────────┬───────────────────┬────────────────┐
  │                      Qué                      │  En qué archivo   │ Tipo de cambio │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ cmd_* devuelven str en vez de print           │ archivos_hilos.py │ Refactor       │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ _mostrar_cabecera() devuelve str              │ archivos_hilos.py │ Refactor       │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ main() hace print(cmd_*(..))                  │ archivos_hilos.py │ Ajuste mínimo  │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ Handler completo de comandos                  │ filesystem.py     │ Nuevo código   │
  │ cmd_* devuelven str en vez de print           │ archivos_hilos.py │ Refactor       │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ _mostrar_cabecera() devuelve str              │ archivos_hilos.py │ Refactor       │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ main() hace print(cmd_*(..))                  │ archivos_hilos.py │ Ajuste mínimo  │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ Handler completo de comandos                  │ filesystem.py     │ Nuevo código   │
  │ Handler completo de comandos                  │ filesystem.py     │ Nuevo código   │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ Threading con call_from_thread                │ ambos             │ Coordinación   │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ Reemplazar los Placeholder por widgets reales │ filesystem.py     │ Feature nueva  │
  └───────────────────────────────────────────────┴───────────────────┴────────────────┘

  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  ┌───────────────────────────────────────────────┬───────────────────┬────────────────┐
  │                      Qué                      │  En qué archivo   │ Tipo de cambio │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ cmd_* devuelven str en vez de print           │ archivos_hilos.py │ Refactor       │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ _mostrar_cabecera() devuelve str              │ archivos_hilos.py │ Refactor       │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ main() hace print(cmd_*(..))                  │ archivos_hilos.py │ Ajuste mínimo  │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ Handler completo de comandos                  │ filesystem.py     │ Nuevo código   │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ Threading con call_from_thread                │ ambos             │ Coordinación   │
  ├───────────────────────────────────────────────┼───────────────────┼────────────────┤
  │ Reemplazar los Placeholder por widgets reales │ filesystem.py     │ Feature nueva  │
  └───────────────────────────────────────────────┴───────────────────┴────────────────┘

  ---
  Por dónde empezar: el Paso 1 y 2 primero — una vez que las funciones devuelven strings, el Paso 3 es mecánico y todo lo demás se puede ir agregando encima sin romper nada.

✻ Brewed for 47s

※ recap: Combining archivos_hilos.py with filesystem.py into a working Textual TUI. The plan is ready — start by refactoring the cmd_* functions in archivos_hilos.py to return strings
  instead of calling print(). (disable recaps in /config)
