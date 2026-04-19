# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

BrickScript is a small DSL for building retro brick-style games (Tetris, Snake). The toolchain is two scripts: `compiler.py` translates `.brick` source into a JSON AST, and `runtime.py` interprets that JSON in a Tkinter GUI. Games live in `games/`; formal grammars are in `gramaticas bnf/`.

Source comments, identifiers, and user-facing strings are in Spanish — match that style when editing.

## Runtime environment

- Python **3.13+** managed by **uv** (see `pyproject.toml`, `.python-version`). There are no third-party dependencies — only the stdlib + Tkinter.
- `README.txt` and `INSTALL.txt` describe an older Python 2.7 + `msvcrt` console version. The current code has already been migrated to Python 3 + Tkinter. If you edit those docs, update them accordingly rather than reverting the code.

## Common commands

Compile and run a game (Windows, from repo root):

```
jugar.bat snake
jugar.bat tetris
```

Manual two-step (any platform):

```
uv run compiler.py games/snake.brick     # produces games/snake.json
uv run runtime.py games/snake.json
```

There is no test suite, linter, or build step configured. To sanity-check a change, recompile both sample games and launch each — the round-trip exercises lexer, parser, AST shape, and both game-type branches of the runtime.

## Architecture

### Compiler (`compiler.py`)

Single-file pipeline, no classes beyond `Parser`:

1. **Lexer** — regex (`\b[A-Z_]+\b|\d+|[\[\](),:]`) after stripping `#` comments. All keywords are uppercase; there are no string literals.
2. **Parser** — recursive descent over a flat token list with a `posicion` cursor and a `consumir(expected)` helper. Top-level dispatch on `GAME_TYPE` / `GAME_GRID` / `DEFINE` / `ON`.
3. **Emitter** — `json.dump` of the AST.

The AST schema (consumed by the runtime) is fixed:

```
{
  "tipo_juego": "TETRIS" | "SNAKE",
  "config":    { "grid_size": [w, h] },
  "shapes":    { NAME: [ state_matrix, ... ] },   # each state is a list of rows of 0/1
  "events":    { "ON_<NAME>": [ { "accion", "objeto", "params" }, ... ] }
}
```

When adding a new verb, both sides must change: extend `parsear_evento` (note the hard-coded verb list used as a lookahead terminator around line 128) **and** add a branch in `Juego.ejecutar_evento`. The `GAME_OVER` special-case exists because it takes no object.

### Runtime (`runtime.py`)

Single `Juego` class. Key structure:

- Tkinter `Canvas` re-rendered every frame (`canvas.delete("all")` + redraw — no sprite caching).
- Main loop is `root.after(50, game_loop)` → ~20 FPS. Game speed is decoupled: `timer_gravedad` accumulates and fires `ON_TICK` when it exceeds `velocidad_gravedad` (0.4s Tetris, 0.15s Snake).
- `ejecutar_evento(name)` is the single interpreter entry point — it walks the actions for that event and dispatches on `(tipo_juego, verbo, objeto)`. All game logic lives in `tetris_*` / `snake_*` methods on the same class.
- Tetris fixes a piece by calling `tetris_fijar_pieza`, which re-fires `ON_START` to spawn the next piece — so `ON_START` doubles as "respawn."

### Adding a new game type

You cannot add one purely in BrickScript. The runtime dispatches on `self.tipo_juego` in `__init__`, `manejar_input_gui`, `dibujar`, and `ejecutar_evento`; each needs a new branch plus a set of `<type>_*` logic methods. Also add a BNF in `gramaticas bnf/` to keep documentation in sync.
