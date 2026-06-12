# -*- coding: utf-8 -*-
# runtime.py (VERSION CON INTERFAZ GRAFICA USANDO Tkinter y caracteres ASCII unicamente)

import json
import random
import sys
import time
import tkinter as tk
from tkinter import messagebox as tkMessageBox


class Juego:
    def __init__(self, datos_juego):
        self.datos_juego = datos_juego
        self.tipo_juego = self.datos_juego.get("tipo_juego", "TETRIS")
        config = self.datos_juego.get("config", {})
        self.ancho = config.get("grid_size", [10, 20])[0]
        self.alto = config.get("grid_size", [10, 20])[1]
        self.grid = [[0 for _ in range(self.ancho)] for _ in range(self.alto)]
        self.puntuacion = 0
        self.juego_terminado = False

        # --- Configuracion de la GUI ---
        self.root = tk.Tk()
        self.root.title("BrickScript - " + self.tipo_juego)
        # Configurar la accion al cerrar la ventana ('X' de la barra de titulo)
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self.taman_celda = 25  # Pixeles por celda
        self.ancho_canvas = self.ancho * self.taman_celda
        self.alto_canvas = self.alto * self.taman_celda

        # Canvas para dibujar el juego
        self.canvas = tk.Canvas(
            self.root, width=self.ancho_canvas, height=self.alto_canvas, bg="#111111"
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Marco lateral para la puntuacion y controles
        self.marco_score = tk.Frame(
            self.root, width=150, height=self.alto_canvas, bg="#222222"
        )
        self.marco_score.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.label_score = tk.Label(
            self.marco_score,
            text="PUNTUACION\n0",
            bg="#222222",
            fg="white",
            font=("Consolas", 16, "bold"),
        )
        self.label_score.pack(pady=40, padx=10)

        # Verificar si es version inclusiva (remake)
        config = self.datos_juego.get("config", {})
        self.es_inclusivo = any(k in config for k in ["color_contrast", "pattern_type", "tick_multiplier", "color_food", "color_palette"])

        self.label_controles = tk.Label(
            self.marco_score,
            text="CONTROLES\nFlechas: Mover/Rotar\nP / ESC: Pausar" if self.es_inclusivo else "CONTROLES\nFlechas: Mover/Rotar",
            bg="#222222",
            fg="gray",
            font=("Consolas", 10),
        )
        self.label_controles.pack(pady=20, padx=10)

        # Boton de Pausa Interactivo (solo para version inclusiva)
        self.pausado = False
        if self.es_inclusivo:
            self.boton_pausa = tk.Button(
                self.marco_score,
                text="PAUSAR",
                bg="#333333",
                fg="white",
                font=("Consolas", 12, "bold"),
                command=self.alternar_pausa,
                activebackground="#555555",
                activeforeground="white",
                bd=0,
                padx=10,
                pady=5
            )
            self.boton_pausa.pack(pady=10, padx=10)

        # Configurar eventos de teclado. Usamos <Key> para capturar cualquier tecla
        self.root.bind("<Key>", self.manejar_input_gui)
        
        if self.es_inclusivo:
            self.root.bind("<Escape>", lambda e: self.alternar_pausa())
            self.root.bind("<p>", lambda e: self.alternar_pausa())
            self.root.bind("<P>", lambda e: self.alternar_pausa())

        # Leer TICK_MULTIPLIER desde config (default 1.0)
        multiplier = self.datos_juego.get("config", {}).get("tick_multiplier", 1.0)
        try:
            multiplier = float(multiplier)
        except (ValueError, TypeError):
            multiplier = 1.0

        if self.tipo_juego == "TETRIS":
            self.pieza_actual = None
            self.pieza_x, self.pieza_y, self.pieza_rotacion = 0, 0, 0
            self.velocidad_gravedad = 0.4 * multiplier

        if self.tipo_juego == "SNAKE":
            self.serpiente_cuerpo = []
            self.serpiente_direccion = (1, 0)
            self.serpiente_ultima_direccion = (1, 0)
            self.posicion_comida = None
            self.velocidad_gravedad = 0.15 * multiplier

        self.timer_gravedad = 0
        self.ejecutar_evento("ON_START")
        self.timer_id = None  # Para controlar el loop de Tkinter

    def run(self):
        # Inicia el ciclo principal de juego de Tkinter
        self.root.after(50, self.game_loop)
        self.root.mainloop()

    def alternar_pausa(self):
        if not self.es_inclusivo or self.juego_terminado:
            return
        self.pausado = not self.pausado
        if self.pausado:
            if hasattr(self, "boton_pausa"):
                self.boton_pausa.config(text="REANUDAR", bg="#FF5555")
            self.dibujar_pausa()
        else:
            if hasattr(self, "boton_pausa"):
                self.boton_pausa.config(text="PAUSAR", bg="#333333")
            self.dibujar()

    def dibujar_pausa(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            self.ancho_canvas // 2,
            self.alto_canvas // 2 - 20,
            text="JUEGO PAUSADO",
            fill="#FF5555",
            font=("Consolas", 16, "bold"),
            justify=tk.CENTER
        )
        self.canvas.create_text(
            self.ancho_canvas // 2,
            self.alto_canvas // 2 + 20,
            text="Presione REANUDAR\no tecla 'P'/'ESC'\npara continuar.",
            fill="white",
            font=("Consolas", 10),
            justify=tk.CENTER
        )

    def game_loop(self):
        if self.juego_terminado:
            self.mostrar_game_over()
            return

        if not self.pausado:
            # Logica de TICK/Gravedad
            # El loop se ejecuta cada 50ms (0.05 segundos)
            self.timer_gravedad += 0.05
            if self.timer_gravedad >= self.velocidad_gravedad:
                self.timer_gravedad = 0
                self.ejecutar_evento("ON_TICK")

            self.dibujar()
        else:
            self.dibujar_pausa()

        # Programa el siguiente ciclo de juego
        self.timer_id = self.root.after(50, self.game_loop)

    def cerrar_ventana(self):
        # Detiene el loop de juego de forma segura
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.root.destroy()
        sys.exit(0)

    def manejar_input_gui(self, event):
        if self.pausado:
            return
        key = event.keysym.upper()

        # Mapeo de teclas de flecha
        if self.tipo_juego == "TETRIS":
            if key == "UP":
                self.ejecutar_evento("ON_KEY_UP")
            elif key == "DOWN":
                self.ejecutar_evento("ON_KEY_DOWN")
            elif key == "LEFT":
                self.ejecutar_evento("ON_KEY_LEFT")
            elif key == "RIGHT":
                self.ejecutar_evento("ON_KEY_RIGHT")
        elif self.tipo_juego == "SNAKE":
            if key == "UP":
                self.snake_cambiar_direccion("UP")
            elif key == "DOWN":
                self.snake_cambiar_direccion("DOWN")
            elif key == "LEFT":
                self.snake_cambiar_direccion("LEFT")
            elif key == "RIGHT":
                self.snake_cambiar_direccion("RIGHT")

    def dibujar(self):
        self.canvas.delete("all")  # Borrar todo en cada frame
        self.label_score.config(text="PUNTUACION\n" + str(self.puntuacion))

        # Configuracion de Colores y Accesibilidad
        high_contrast = self.datos_juego.get("config", {}).get("color_contrast", "DEFAULT") == "HIGH"
        color_palette = self.datos_juego.get("config", {}).get("color_palette", "DEFAULT")
        color_food_config = self.datos_juego.get("config", {}).get("color_food")

        if high_contrast:
            COLOR_GRID_FIJA = "#FFFFFF"      # Blanco para alto contraste
            COLOR_PIEZA = "#FFFF00"          # Amarillo brillante
            COLOR_SNAKE_CABEZA = "#00FFFF"   # Cyan brillante
            COLOR_SNAKE_CUERPO = "#00FF00"   # Verde neon
            COLOR_FOOD = "#FF00FF"           # Magenta brillante
        else:
            if color_palette == "PASTEL":
                COLOR_GRID_FIJA = "#AEC6CF"  # Azul pastel
                COLOR_PIEZA = "#FFB347"      # Naranja pastel
            else:
                COLOR_GRID_FIJA = "#343434"  # Gris oscuro
                COLOR_PIEZA = "#00FFFF"      # Cyan
            
            COLOR_SNAKE_CABEZA = "#00FF00"   # Verde
            COLOR_SNAKE_CUERPO = "#33CC33"   # Verde normal
            COLOR_FOOD = "#FF0000"           # Rojo

        if color_food_config:
            import re
            if re.match(r"^[0-9a-fA-F]{6}$", color_food_config):
                COLOR_FOOD = "#" + color_food_config
            else:
                COLOR_FOOD = color_food_config

        # 1. Dibujar la cuadricula estatica (grid base)
        for y in range(self.alto):
            for x in range(self.ancho):
                if self.grid[y][x] == 1:
                    self.dibujar_celda(x, y, COLOR_GRID_FIJA)

        # 2. Dibujar la pieza actual de Tetris
        if self.tipo_juego == "TETRIS" and self.pieza_actual:
            matriz_pieza = self.pieza_actual[self.pieza_rotacion]
            for y_offset, fila in enumerate(matriz_pieza):
                for x_offset, celda in enumerate(fila):
                    if celda == 1:
                        self.dibujar_celda(
                            self.pieza_x + x_offset,
                            self.pieza_y + y_offset,
                            COLOR_PIEZA,
                        )

        # 3. Dibujar Snake y Comida
        if self.tipo_juego == "SNAKE":
            # Comida
            if self.posicion_comida:
                x, y = self.posicion_comida
                self.dibujar_celda(x, y, COLOR_FOOD, es_comida=True)
            # Cuerpo de la Serpiente
            for i, segmento in enumerate(self.serpiente_cuerpo):
                x, y = segmento
                color = COLOR_SNAKE_CABEZA if i == 0 else COLOR_SNAKE_CUERPO
                self.dibujar_celda(x, y, color)

    def dibujar_celda(self, x, y, color, es_comida=False):
        ts = self.taman_celda  # Alias para taman de celda
        x1, y1 = x * ts, y * ts
        x2, y2 = x1 + ts, y1 + ts

        # Si es comida, usar forma ovalada para redundancia geometrica
        if self.tipo_juego == "SNAKE" and es_comida:
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="#FFFFFF", width=2)
            return

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#000000")

        # Dibujar patrones para redundancia de diseño
        pattern_type = self.datos_juego.get("config", {}).get("pattern_type", "NONE")
        if pattern_type == "STRIPES":
            # Rayas diagonales
            self.canvas.create_line(x1, y1 + 5, x1 + ts - 5, y2, fill="#FFFFFF", width=1)
            self.canvas.create_line(x1 + 5, y1, x1 + ts, y2 - 5, fill="#FFFFFF", width=1)
        elif pattern_type == "DOTS":
            # Punto central
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            r = 3
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#FFFFFF", outline="#FFFFFF")

    def ejecutar_evento(self, nombre_evento):
        if nombre_evento in self.datos_juego["events"]:
            for accion in self.datos_juego["events"][nombre_evento]:
                verbo, objeto = accion.get("accion"), accion.get("objeto")

                if verbo == "INCREASE_SCORE":
                    self.puntuacion += int(objeto)
                if verbo == "GAME_OVER":
                    self.juego_terminado = True

                if self.tipo_juego == "TETRIS":
                    if verbo == "SPAWN":
                        self.tetris_spawn_pieza()
                    if verbo == "MOVE":
                        self.tetris_mover_pieza(accion["params"][0])
                    if verbo == "ROTATE":
                        self.tetris_rotar_pieza()

                if self.tipo_juego == "SNAKE":
                    if verbo == "SPAWN" and objeto == "PLAYER":
                        self.snake_spawn_jugador(accion)
                    if verbo == "SPAWN" and objeto == "FOOD":
                        self.snake_spawn_comida()
                    if verbo == "MOVE" and objeto == "PLAYER":
                        self.snake_mover_jugador()
                    if verbo == "GROW":
                        self.snake_crecer()

    # METODOS DE LOGICA DE JUEGO
    # ---------------------------------------------------------------------

    def tetris_spawn_pieza(self):
        nombre_pieza = random.choice(list(self.datos_juego["shapes"].keys()))
        self.pieza_actual = self.datos_juego["shapes"][nombre_pieza]
        self.pieza_x, self.pieza_y, self.pieza_rotacion = self.ancho // 2 - 2, 0, 0
        if self.tetris_verificar_colision(
            self.pieza_x, self.pieza_y, self.pieza_rotacion
        ):
            self.juego_terminado = True

    def tetris_mover_pieza(self, direccion):
        if not self.pieza_actual:
            return
        dx, dy = 0, 0
        if direccion == "LEFT":
            dx = -1
        elif direccion == "RIGHT":
            dx = 1
        elif direccion == "DOWN":
            dy = 1
        if not self.tetris_verificar_colision(
            self.pieza_x + dx, self.pieza_y + dy, self.pieza_rotacion
        ):
            self.pieza_x += dx
            self.pieza_y += dy
        elif dy > 0:
            self.tetris_fijar_pieza()

    def tetris_rotar_pieza(self):
        if not self.pieza_actual:
            return
        nueva_rotacion = (self.pieza_rotacion + 1) % len(self.pieza_actual)
        # Intentar rotar en la posicion actual
        if not self.tetris_verificar_colision(
            self.pieza_x, self.pieza_y, nueva_rotacion
        ):
            self.pieza_rotacion = nueva_rotacion
            return

        # Wall Kick: Intentar desplazar a la izquierda o derecha (solo en la version inclusiva/remake)
        if self.es_inclusivo:
            desplazamientos = [-1, 1, -2, 2]
            for dx in desplazamientos:
                if not self.tetris_verificar_colision(
                    self.pieza_x + dx, self.pieza_y, nueva_rotacion
                ):
                    self.pieza_x += dx
                    self.pieza_rotacion = nueva_rotacion
                    return

    def tetris_fijar_pieza(self):
        matriz_pieza = self.pieza_actual[self.pieza_rotacion]
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    if (
                        0 <= self.pieza_y + y_offset < self.alto
                        and 0 <= self.pieza_x + x_offset < self.ancho
                    ):
                        self.grid[self.pieza_y + y_offset][self.pieza_x + x_offset] = 1
        self.pieza_actual = None
        self.tetris_limpiar_lineas()
        self.ejecutar_evento("ON_START")

    def tetris_verificar_colision(self, x, y, rotacion):
        if not self.pieza_actual:
            return False
        matriz_pieza = self.pieza_actual[rotacion]
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    nuevo_x, nuevo_y = x + x_offset, y + y_offset
                    if not (
                        0 <= nuevo_x < self.ancho
                        and 0 <= nuevo_y < self.alto
                        and self.grid[nuevo_y][nuevo_x] == 0
                    ):
                        return True
        return False

    def tetris_limpiar_lineas(self):
        nuevo_grid = [fila for fila in self.grid if not all(fila)]
        lineas_limpias = self.alto - len(nuevo_grid)
        if lineas_limpias > 0:
            self.grid = [[0] * self.ancho for _ in range(lineas_limpias)] + nuevo_grid
            for _ in range(lineas_limpias):
                self.ejecutar_evento("ON_LINE_CLEAR")

    def snake_spawn_jugador(self, accion):
        coords = (
            accion["params"][0]
            if accion["params"]
            else [self.ancho // 2, self.alto // 2]
        )
        self.serpiente_cuerpo = [(coords[0], coords[1])]
        self.serpiente_direccion = (1, 0)
        self.serpiente_ultima_direccion = (1, 0)

    def snake_spawn_comida(self):
        while True:
            x, y = random.randint(0, self.ancho - 1), random.randint(0, self.alto - 1)
            if (x, y) not in self.serpiente_cuerpo:
                self.posicion_comida = (x, y)
                break

    def snake_mover_jugador(self):
        if not self.serpiente_cuerpo:
            return
        cabeza_x, cabeza_y = self.serpiente_cuerpo[0]
        dir_x, dir_y = self.serpiente_direccion
        nueva_cabeza = (cabeza_x + dir_x, cabeza_y + dir_y)

        if not (0 <= nueva_cabeza[0] < self.ancho and 0 <= nueva_cabeza[1] < self.alto):
            self.ejecutar_evento("ON_COLLISION_WALL")
            return

        if nueva_cabeza in self.serpiente_cuerpo[:-1]:
            self.ejecutar_evento("ON_COLLISION_SELF")
            return

        self.serpiente_cuerpo.insert(0, nueva_cabeza)
        self.serpiente_ultima_direccion = self.serpiente_direccion

        if nueva_cabeza == self.posicion_comida:
            self.ejecutar_evento("ON_EAT_FOOD")
        else:
            self.serpiente_cuerpo.pop()

    def snake_cambiar_direccion(self, direccion):
        # En la version inclusiva se usa serpiente_ultima_direccion para evitar el bug.
        # En la version original se usa serpiente_direccion, permitiendo el bug.
        dir_ref = self.serpiente_ultima_direccion if self.es_inclusivo else self.serpiente_direccion
        if direccion == "UP" and dir_ref[1] != 1:
            self.serpiente_direccion = (0, -1)
        elif direccion == "DOWN" and dir_ref[1] != -1:
            self.serpiente_direccion = (0, 1)
        elif direccion == "LEFT" and dir_ref[0] != 1:
            self.serpiente_direccion = (-1, 0)
        elif direccion == "RIGHT" and dir_ref[0] != -1:
            self.serpiente_direccion = (1, 0)

    def snake_crecer(self):
        pass

    # METODOS DE SALIDA (ADAPTADOS A GUI)
    # -----------------------------------

    def mostrar_game_over(self):
        tkMessageBox.showinfo(
            "Juego Terminado", "Puntuacion Final: " + str(self.puntuacion)
        )
        self.root.destroy()
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python runtime.py <archivo_juego.json>")
        sys.exit(1)
    archivo_juego = sys.argv[1]
    try:
        with open(archivo_juego, "r") as f:
            datos_juego = json.load(f)
    except IOError:
        print("Error: No se pudo encontrar el archivo " + archivo_juego)
        sys.exit(1)
    juego = Juego(datos_juego)
    juego.run()
