=============================================================
          PROYECTO: BrickScript - Un Lenguaje para Juegos Retro
=============================================================

BrickScript es un lenguaje de programación simple (un "DSL" o Lenguaje de Dominio Específico) diseñado para crear juegos clásicos de estilo "Brick Game", como Tetris y Snake, con un enfoque moderno en Diseño de Experiencia de Usuario (UX) y Accesibilidad.

Este proyecto incluye el compilador (`compiler.py`) que traduce el código BrickScript a un formato JSON intermedio, y el motor de juego (`runtime.py`) en Python 3 + Tkinter que lo ejecuta.

-------------------------------------------------------------
                      CÓMO JUGAR
-------------------------------------------------------------

Para compilar y ejecutar un juego, puedes usar el script automatizado `jugar.bat` (o correr los comandos con Python directamente).

1. Abre una consola de comandos (PowerShell o cmd.exe) en la carpeta principal del proyecto.

2. Ejecuta `jugar.bat` seguido del nombre del juego que deseas ejecutar (sin la extensión `.brick`):

   PARA JUGAR LAS VERSIONES ORIGINALES (BASE):
   .\jugar.bat snake
   .\jugar.bat tetris

   PARA JUGAR LAS VERSIONES INCLUSIVAS (REMAKES CON ACCESIBILIDAD):
   .\jugar.bat snake_remake
   .\jugar.bat tetris_remake

3. El script compilará automáticamente el archivo `.brick` de la carpeta `games/` y lanzará la interfaz gráfica.

-------------------------------------------------------------
                  NUEVAS CARACTERÍSTICAS DE ACCESIBILIDAD
-------------------------------------------------------------

La versión inclusiva introduce elementos diseñados para personas con limitaciones visuales (daltonismo, baja visión) o sensibilidad a la ansiedad (Andrés y Doña Martha):

1. **Botón de Pausa**: Se ha añadido un botón interactivo "PAUSAR / REANUDAR" en el panel lateral y se puede controlar también con las teclas 'P' o 'ESC'.
2. **Redundancia Geométrica**: La comida en Snake ahora se dibuja como un círculo para distinguirla del cuerpo de la serpiente y las paredes por su forma.
3. **Wall Kick en Tetris**: Las piezas ya no se bloquean al rotar contra las paredes; el motor las empuja automáticamente hacia el centro para evitar frustración.
4. **Prevención de Suicidio 180° en Snake**: Se bloquean giros instantáneos en la dirección opuesta, evitando muertes por pánico o pulsaciones rápidas.

-------------------------------------------------------------
            SINTAXIS DE BRICKSCRIPT PARA DISEÑO INCLUSIVO
-------------------------------------------------------------

Los diseñadores pueden utilizar las siguientes etiquetas de configuración opcionales al inicio de sus archivos `.brick`:

* `COLOR_CONTRAST [HIGH | DEFAULT]`
    - Activa la paleta de colores de alto contraste (blanco, amarillo, cyan, neon y magenta).
    - Ej: COLOR_CONTRAST HIGH

* `PATTERN_TYPE [STRIPES | DOTS | NONE]`
    - Agrega texturas internas (rayas o puntos) a los bloques para que el usuario diferencie las piezas sin depender exclusivamente del color.
    - Ej: PATTERN_TYPE STRIPES

* `TICK_MULTIPLIER [Número]`
    - Factor de velocidad que ralentiza (valores > 1.0) o acelera (valores < 1.0) el juego.
    - Ej: TICK_MULTIPLIER 2.0 (Duplica el tiempo de reacción para Doña Martha)

* `COLOR_FOOD [Nombre o Hexadecimal]` (Específico para Snake)
    - Define un color personalizado para la comida.
    - Ej: COLOR_FOOD FFFF00 (Amarillo brillante)

* `COLOR_PALETTE [PASTEL | DEFAULT]` (Específico para Tetris)
    - Define una paleta de colores pastel relajante.
    - Ej: COLOR_PALETTE PASTEL