#!/usr/bin/env python3
import http.server
import shutil
import socketserver
import subprocess
import sys
import textwrap
import threading
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOSCRIPT = ROOT / "doscript.py"
TMP_ROOT = ROOT / ".regression_tmp"


def make_temp_dir(prefix: str) -> Path:
    TMP_ROOT.mkdir(exist_ok=True)
    path = TMP_ROOT / f"{prefix}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_case(name: str, script_text: str, expected: str, extra_files=None, dry_run: bool = False) -> None:
    extra_files = extra_files or {}
    temp_dir = make_temp_dir("doscript-reg")
    try:
        script_path = temp_dir / "case.do"
        script_path.write_text(script_text, encoding="utf-8")
        for rel, content in extra_files.items():
            file_path = temp_dir / rel
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        cmd = [sys.executable, str(DOSCRIPT), str(script_path)]
        if dry_run:
            cmd.insert(3, "--dry-run")
        result = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)
        if result.returncode != 0:
            raise AssertionError(f"{name} failed with exit {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        combined = (result.stdout + result.stderr).strip()
        if expected not in combined:
            raise AssertionError(f"{name} missing expected text {expected!r}\nOUTPUT:\n{combined}")
        print(f"[PASS] {name}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_remote_case() -> None:
    temp_dir = make_temp_dir("doscript-remote-reg")
    try:
        script_path = temp_dir / "remote.do"
        script_path.write_text("\ufeffsay \"remote ok\"\n", encoding="utf-8")

        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(temp_dir), **kwargs)
        with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
            port = httpd.server_address[1]
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{port}/remote.do"
                result = subprocess.run(
                    [sys.executable, str(DOSCRIPT), url],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise AssertionError(f"remote execution failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
                combined = (result.stdout + result.stderr).strip()
                if "remote ok" not in combined:
                    raise AssertionError(f"remote execution missing expected output\nOUTPUT:\n{combined}")
                print("[PASS] remote execution")
            finally:
                httpd.shutdown()
                thread.join(timeout=2)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(ROOT / ".doscript_remote_cache", ignore_errors=True)
        shutil.rmtree(TMP_ROOT, ignore_errors=True)


def main() -> int:
    run_case(
        "nested for_each_line",
        textwrap.dedent(
            """
            global_variable = count, total
            count = 0
            total = 0
            for_each file_in here
                if file_name == "data.txt"
                    for_each_line line in "data.txt"
                        total = total + 1
                    end_for
                    count = count + 10
                end_if
            end_for
            say '{count}:{total}'
            """
        ).strip() + "\n",
        "10:3",
        extra_files={"data.txt": "a\nb\nc\n"},
    )

    run_case(
        "else_if and loop index",
        textwrap.dedent(
            """
            global_variable = label, total
            label = ""
            total = 0
            if false
                label = "bad"
            else_if true
                label = "good"
            else
                label = "fallback"
            end_if
            loop 3 as i
                total = total + i
            end_loop
            say '{label}:{total}'
            """
        ).strip() + "\n",
        "good:6",
    )

    run_case(
        "string helpers",
        textwrap.dedent(
            """
            global_variable = raw, clean, loud, chars
            raw = "  Alice  "
            clean = trim(raw)
            loud = upper(clean)
            chars = length(clean)
            say '{loud}:{chars}'
            """
        ).strip() + "\n",
        "ALICE:5",
    )

    run_case(
        "execute_command dry-run",
        "execute_command \"py\" \"--version\"\n",
        "[DRY] execute_command py --version",
        dry_run=True,
    )

    run_remote_case()
    print("All regressions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
