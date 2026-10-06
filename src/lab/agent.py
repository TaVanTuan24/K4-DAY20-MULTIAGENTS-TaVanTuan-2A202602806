"""GUIDE Phần 1 - Dựng tác tử (agent) bằng Deep Agents.   >>> SINH VIÊN CÀI ĐẶT make_backend VÀ build_agent <<<

Pseudo-code: guides/pseudocode/01_agent.md
Kiểm tra:    pytest tests/test_02_agent.py
"""
import os
import shutil
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

from .model import make_model
from .subagents import get_subagents

# ---- CÓ SẴN, KHÔNG SỬA: system prompt dùng chung cho mọi sinh viên (để đường cơ sở so sánh được) ----
PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)
# --------------------------------------------------------------------------------------------------


import subprocess
from deepagents.backends.protocol import ExecuteResponse


class ShShellBackend(LocalShellBackend):
    """LocalShellBackend that pipes commands to sh on Windows when a POSIX shell is available."""

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        sh_path = shutil.which("sh") or shutil.which("bash")
        if sys.platform == "win32" and sh_path:
            effective_timeout = timeout if timeout is not None else self._default_timeout
            try:
                proc = subprocess.Popen(
                    [sh_path, "-c", command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=str(self.cwd),
                    env=self._env,
                )
                try:
                    stdout, stderr = proc.communicate(timeout=effective_timeout)
                except subprocess.TimeoutExpired:
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        capture_output=True,
                        check=False,
                    )
                    try:
                        stdout, stderr = proc.communicate(timeout=5)
                    except Exception:
                        pass
                    msg = f"Error: Command timed out after {effective_timeout} seconds."
                    return ExecuteResponse(output=msg, exit_code=124, truncated=False)

                output_parts = []
                if stdout:
                    output_parts.append(stdout)
                if stderr:
                    for line in stderr.strip().split("\n"):
                        if line:
                            output_parts.append(f"[stderr] {line}")
                output = "\n".join(output_parts) if output_parts else "<no output>"
                truncated = False
                if len(output) > self._max_output_bytes:
                    output = output[: self._max_output_bytes] + f"\n\n... Output truncated at {self._max_output_bytes} bytes."
                    truncated = True
                if proc.returncode != 0:
                    output = f"{output.rstrip()}\n\nExit code: {proc.returncode}"
                return ExecuteResponse(
                    output=output,
                    exit_code=proc.returncode,
                    truncated=truncated,
                )
            except Exception as e:
                return ExecuteResponse(output=f"Error executing command ({type(e).__name__}): {e}", exit_code=1, truncated=False)
        return super().execute(command, timeout=timeout)


def make_backend(sandbox: Path):
    """Tạo backend (môi trường thực thi) cho tác tử.

    Yêu cầu:
      - Thư mục gốc (root_dir) là `sandbox`; đường dẫn tương đối `workspace/...` và `skills/...`
        phải dùng được ở CẢ công cụ tệp lẫn shell (shell chạy với thư mục làm việc = `sandbox`).
      - Tác tử chạy được lệnh shell và gọi được `python` (cần đặt PATH).
      - KHÔNG chuyển biến môi trường của bạn vào shell của tác tử (khóa API không được lộ).
    """
    python_dir = str(Path(sys.executable).parent)
    path_parts = [python_dir]
    git_path = shutil.which("git")
    if git_path:
        git_usr_bin = Path(git_path).resolve().parent.parent / "usr" / "bin"
        if git_usr_bin.exists():
            path_parts.append(str(git_usr_bin))
    if sys.platform == "win32":
        path_parts.append(r"C:\Windows\System32")
    path_parts.extend(["/usr/local/bin", "/usr/bin", "/bin"])
    path_str = os.pathsep.join(path_parts) if sys.platform == "win32" else ":".join([python_dir, "/usr/local/bin", "/usr/bin", "/bin"])
    if sys.platform == "win32":
        path_str = path_str + ":/usr/local/bin:/usr/bin:/bin"

    env = {
        "PATH": path_str,
        "HOME": str(sandbox),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if sys.platform == "win32":
        for var in ("SystemRoot", "COMSPEC", "PATHEXT", "TEMP", "TMP"):
            if var in os.environ:
                env[var] = os.environ[var]

    return ShShellBackend(
        root_dir=sandbox,
        virtual_mode=True,
        inherit_env=False,
        env=env,
        timeout=120,
    )


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Tạo tác tử Deep Agents.

    Tham số:
      sandbox:    thư mục chứa `workspace/` (và `skills/` nếu có).
      mode:       "single"    -> tác tử mặc định (có subagent `general-purpose` sẵn của Deep Agents)
                  "subagents" -> thêm các subagent từ `get_subagents()` (nối PATHS_NOTE vào `system_prompt` của MỖI subagent,
                                 vì subagent không nhận BASE_PROMPT) và thêm SUBAGENTS_NOTE vào prompt chính
      use_skills: True -> nạp thư mục "/skills/" qua tham số `skills=` của create_deep_agent
                  và thêm SKILLS_NOTE vào prompt.
      model:      mô hình ngôn ngữ; None -> dùng `make_model()`.
    mode không hợp lệ -> ném ValueError.
    Trả về: đồ thị (graph) đã biên dịch, gọi bằng `.invoke({"messages": [...]})`.
    """
    if mode not in {"single", "subagents"}:
        raise ValueError(f"Unknown mode: {mode}")

    kwargs = {}
    prompt = BASE_PROMPT

    if mode == "subagents":
        kwargs["subagents"] = [
            {**sub, "system_prompt": sub["system_prompt"] + " " + PATHS_NOTE}
            for sub in get_subagents()
        ]
        prompt = prompt + SUBAGENTS_NOTE

    if use_skills:
        kwargs["skills"] = ["/skills/"]
        prompt = prompt + SKILLS_NOTE

    resolved_model = model if model is not None else make_model()
    if hasattr(resolved_model, "streaming"):
        resolved_model.streaming = True

    return create_deep_agent(
        model=resolved_model,
        system_prompt=prompt,
        backend=make_backend(sandbox),
        **kwargs,
    )
