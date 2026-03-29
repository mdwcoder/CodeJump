from __future__ import annotations

import shutil
import subprocess

from codejump.core.models import IndexItem, OpenResult, Project


class EditorOpener:
    def open_item(self, project: Project, item: IndexItem) -> OpenResult:
        command_name = project.editor_command.strip() or "code"
        executable = command_name.split()[0]
        if not shutil.which(executable):
            return OpenResult(False, f"Editor command not found: {command_name}")

        command = self._build_command(command_name, item.full_path, item.line)
        try:
            subprocess.Popen(command)
        except OSError as exc:
            return OpenResult(False, f"Failed to open editor: {exc}")
        return OpenResult(True, f"Opened {item.display_name}")

    def _build_command(self, command_name: str, file_path: str, line: int | None) -> list[str]:
        command_parts = command_name.split()
        executable = command_parts[0]
        extra_args = command_parts[1:]
        target = file_path

        if line and executable in {"code", "cursor"}:
            return [executable, *extra_args, "-g", f"{file_path}:{line}"]
        if line and executable == "zed":
            target = f"{file_path}:{line}"
        return [executable, *extra_args, target]

