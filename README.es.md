[Español](README.es.md) | [English](README.en.md)

---

# CodeJump

Navegacion de codigo por intencion para proyectos grandes.

CodeJump es una superposicion de escritorio compacta para Linux y macOS, creada con Python y Flet. No pretende ser un editor ni un IDE: su trabajo es indexar un proyecto, entender consultas cortas de intencion, ordenar archivos, carpetas y simbolos probables, y abrir el resultado en tu editor configurado.

## Inicio rapido

```bash
git clone <your-repo-url>
cd FileJumpOverlay
bash init.sh
```

Si `init.sh` no es ejecutable:

```bash
chmod +x init.sh
./init.sh
```

Despues puedes abrir la app con:

```bash
filejump
```

o:

```bash
python -m codejump.main
```

## Que hace

CodeJump esta optimizado para consultas como:

```text
payment summary
activity controller
login page
firestore user model
```

Indexa archivos, carpetas y simbolos ligeros. Despues puntua resultados con reglas lexicas explicitas: coincidencia exacta de nombre, simbolos, tokens de ruta, previsualizaciones, historial reciente y penalizacion de coincidencias debiles.

## Por que existe

En proyectos grandes, saber el nombre exacto de un archivo no siempre es realista. CodeJump permite buscar por lo que quieres hacer y saltar rapido al sitio probable.

## Instalacion

El instalador crea `.venv`, instala dependencias, registra el lanzador `filejump` y arranca la app. Intenta instalar el lanzador en `/usr/local/bin`, luego en `~/.local/bin` y finalmente en `./.local/bin`.

## Uso esperado

- Abre la app de escritorio.
- Selecciona o indexa un proyecto.
- Escribe una consulta corta de intencion.
- Abre el resultado en tu editor.

## Alcance

El producto principal es la app de escritorio. El comando `filejump` es solo un lanzador de conveniencia.
