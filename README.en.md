[Español](README.es.md) | [English](README.en.md)

---

# CodeJump

Intent-driven desktop code navigation for large projects.

CodeJump is a compact desktop overlay for Linux and macOS built with Python and Flet. It is not an editor, not an IDE, and not a replacement for VS Code or Cursor. Its job is narrow and fast: index a project, understand short developer intent queries, rank likely files, folders and symbols, and jump you straight into your configured editor.

This project is a desktop utility first.

- The main product is the windowed overlay app.
- `filejump` is only a convenience launcher for opening that desktop app.
- The terminal is part of installation and launch, not the core UX.

## Quickstart

```bash
git clone <your-repo-url>
cd FileJumpOverlay
bash init.sh
```

If `init.sh` is not executable:

```bash
chmod +x init.sh
./init.sh
```

Then open the app with either:

```bash
filejump
```

or:

```bash
python -m codejump.main
```

`init.sh` will:

- create `.venv` if it does not exist
- install or refresh dependencies inside that virtualenv
- install a `filejump` launcher
- start the desktop app

Launcher install target order:

- `/usr/local/bin` if writable
- `~/.local/bin` if writable
- `./.local/bin` inside the project as a safe fallback

## What CodeJump Does

CodeJump is optimized for queries like:

```text
payment summary
activity controller
login page
firestore user model
campcash stripe
```

It indexes:

- files
- folders
- lightweight symbols

It then scores results using explicit lexical logic:

- exact file name matches get strong priority
- symbol matches get strong priority
- path token matches matter
- preview token matches help
- recent opens and recent queries add a small boost
- weak/noisy matches are penalized

## Why It Exists

Modern codebases are large, deeply nested, and inconsistent in naming style. Exact-match file search is useful, but it breaks down when the developer only remembers intent or concept.

CodeJump closes that gap by normalizing:

- natural language
- `snake_case`
- `camelCase`
- `kebab-case`
- slash-separated paths

and then ranking candidates that feel semantically close without adding AI, embeddings, AST-heavy parsing, or a heavyweight runtime.

## Installation

Recommended from source:

```bash
git clone <your-repo-url>
cd FileJumpOverlay
bash init.sh
```

Manual setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Requirements:

- Python 3.11+
- Linux or macOS
- one supported editor CLI if you want jump-to-editor behavior:
  - `code`
  - `cursor`
  - `zed`

## Launching The App

Primary launch options:

```bash
filejump
```

or:

```bash
python -m codejump.main
```

`filejump` is not a separate CLI product. It simply opens the CodeJump desktop app after `init.sh` installs the launcher.

## Basic Usage

Typical flow inside the app:

1. Add a project from the header.
2. Set name, root path, and editor command.
3. Reindex the project.
4. Type a short intent query.
5. Move with arrow keys.
6. Press `Enter` to open the selected result.

Keyboard behavior:

- `Arrow Up` / `Arrow Down`: move selection
- `Enter`: open selected result
- `Esc`: clear query, or minimize when query is empty
- `Ctrl+C` / `Cmd+C`: copy selected path

## Project Configuration

Each project stores:

- `name`
- `root_path`
- `editor_command`
- `priority_extensions`
- `ignored_dirs`
- `aliases`

Notes:

- `priority_extensions` is a comma-separated list like `.ts, .tsx, .dart`
- `ignored_dirs` is a comma-separated list of extra ignored folders
- `aliases` is persisted now and reserved for future ranking improvements

If a project path no longer exists, CodeJump keeps the project entry but marks it as missing in the UI.

## Search Behavior

CodeJump uses explicit tokenization and scoring, not opaque ranking.

### Tokenization

The tokenizer normalizes:

- lowercase text
- `snake_case`
- `camelCase`
- `kebab-case`
- dotted names
- route/path segments

So a query like:

```text
payment modes activity
```

can still surface candidates such as:

- `activity_edit_controller.dart`
- `getTurnPaymentModes.js`
- `payment_summary_entity.dart`

### Scoring

Ranking is handled in dedicated core modules, not in the UI.

Signals currently used:

- exact file-name match
- exact or fuzzy symbol-name token match
- token coverage across name/path/preview
- ordered token matches
- preferred extension boost
- recent open boost
- recent query boost
- short path bonus
- weak coverage penalty

The UI also shows a short explanation for why a result matched.

## Indexed Item Types

V1 indexes:

- `file`
- `folder`
- `symbol`

Symbol detection is regex-based and intentionally lightweight.

Supported languages in V1:

- Dart
- Python
- JavaScript
- TypeScript

Examples detected:

- `class X`
- `enum X`
- `extension X`
- `typedef X`
- `def x(...)`
- `async def x(...)`
- `function x(...)`
- `const x =`
- `exports.x =`
- `module.exports`
- `router.get(...)`
- `app.post(...)`

## Editor Integration

File opening is implemented in `codejump/core/opener.py`.

Supported commands:

- `code`
- `cursor`
- `zed`

Line-aware behavior:

- `code -g path:line`
- `cursor -g path:line`
- `zed path:line`

If the editor command is missing or fails, the app shows a visible message instead of crashing.

## Window Behavior

CodeJump is designed as a desktop overlay:

- resizable
- minimizable
- usable in narrow vertical layouts
- usable in wider desktop layouts
- supports always-on-top

Defaults:

- dark theme
- geometry remembered by default
- start with last project enabled
- start with last query disabled

Geometry persistence includes:

- width
- height
- left
- top
- always-on-top state
- selected project
- last query

If saved geometry is invalid, CodeJump falls back to a safe default overlay position.

## Storage

CodeJump uses plain JSON files. No database is required for V1.

Tracked runtime files:

- `codejump/config/settings.json`
- `codejump/config/projects.json`
- `codejump/data/history.json`

Per-project index cache:

- `codejump/data/index_cache/<project_id>.json`

## Bootstrap Script

`init.sh` is intentionally idempotent.

You can run it repeatedly:

```bash
./init.sh
```

That will:

- reuse the local virtualenv if present
- reinstall dependencies into that same environment
- refresh the `filejump` launcher
- launch the desktop app

This is useful when:

- you pulled new changes
- dependencies changed
- your shell launcher was not created before

## Architecture

Project layout:

```text
codejump/
  main.py
  app/
    ui/
      main_view.py
      header.py
      search_bar.py
      results_list.py
      preview_panel.py
      settings_dialog.py
      project_dialog.py
      theme.py
    controllers/
      app_controller.py
      search_controller.py
      settings_controller.py
      project_controller.py
  core/
    models.py
    enums.py
    search_engine.py
    scorer.py
    tokenizer.py
    symbol_extractors.py
    project_indexer.py
    opener.py
    geometry.py
  storage/
    settings_store.py
    projects_store.py
    history_store.py
    index_store.py
  utils/
    paths.py
    validators.py
    platform_helpers.py
    logging_setup.py
  assets/
```

Layer responsibilities:

- `core`: search/index/open logic
- `storage`: JSON persistence
- `controllers`: application state orchestration
- `ui`: Flet controls and view composition
- `utils`: platform, validation, paths, logging

## Result Display

Each result can expose:

- display name
- item type
- relative path
- short preview
- line number
- match explanation

The preview panel shows:

- full path
- type / symbol metadata
- line if available
- preview excerpt
- quick actions

## Ignored Paths

Default ignored paths:

- `.git`
- `node_modules`
- `build`
- `dist`
- `.dart_tool`
- `.next`
- `coverage`
- `.venv`
- `venv`
- `__pycache__`
- `ios/Pods`
- `android/.gradle`

You can add more ignored directories per project.

## Example Queries

Use short, intent-heavy phrases:

```bash
payment summary
user firestore model
login page
activity controller
stripe campcash
window geometry
```

The engine is better with concept words than with full sentences.

## Development Notes

Useful commands:

```bash
python3 -m compileall codejump
bash -n init.sh
```

Rebuild environment and relaunch:

```bash
./init.sh
```

## Limitations

V1 intentionally does not include:

- AI search
- embeddings
- AST-heavy parsing
- filesystem watchers
- cloud sync
- login
- analytics
- editor features

Known boundaries:

- symbol extraction is regex-based
- search quality depends on naming quality and token overlap
- only a small set of editor CLIs are supported

## Roadmap

Natural next extensions without changing the product shape:

- alias-aware ranking
- file watchers for automatic reindex hints
- more editor adapters
- result filters by type
- smarter path preference heuristics
- project groups / workspaces

## Philosophy

CodeJump is meant to feel like a utility you keep open beside the editor, not a destination product. It should stay compact, direct, and technical.
