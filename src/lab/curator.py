"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    if out_dir is None:
        out_dir = ROOT / "skills" / "auto"
    out_dir = Path(out_dir)

    runs = []
    base_path = Path(results_dir) / source_condition
    if base_path.exists():
        for run_file in sorted(base_path.glob("*/run.json")):
            try:
                r = json.loads(run_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            if r.get("role") != "learn":
                continue

            failed = [(c["name"], c.get("detail", "")) for c in r.get("checks", []) if not c.get("passed")]
            trace_file = run_file.parent / "trace.md"
            trace_text = ""
            if trace_file.exists():
                try:
                    trace_text = trace_file.read_text(encoding="utf-8")[-6000:]
                except Exception:
                    pass

            runs.append({
                "task": r.get("task", run_file.parent.name),
                "failed": failed,
                "trace": trace_text,
            })

    # Check if there are any failed checks
    has_failed = any(bool(run["failed"]) for run in runs)
    if not has_failed:
        print("Warning: Không có check thất bại ở tác vụ học. Bỏ qua việc tạo skill.")
        return []

    # Build prompt
    run_blocks = []
    for r in runs:
        if not r["failed"]:
            continue
        failed_lines = "\n".join(f"- {name}: {detail}" for name, detail in r["failed"])
        run_blocks.append(
            f"### Task: {r['task']}\n"
            f"Failed checks:\n{failed_lines}\n\n"
            f"Execution trace (tail):\n{r['trace']}"
        )
    runs_prompt_text = "\n\n".join(run_blocks)

    prompt = (
        "You are writing reusable, procedural SKILL guidelines for a software engineering and data analysis agent.\n"
        "Below are the failed verification checks (check name and review bot feedback detail) along with execution traces from learning runs.\n"
        f"Identify common procedural errors and write at most {max_skills} concise skills to prevent these errors on NEW tasks of the same kind.\n\n"
        "Rules:\n"
        "- Skills must be general: do NOT mention specific task IDs, specific filenames from the task workspace, or specific numbers/answers.\n"
        "- Acme house rules and conventions (such as CHANGELOG.md, tests/test_regressions.py, clean.csv, meta block conventions) ARE allowed and encouraged when mentioned in review bot feedback.\n"
        "- Each skill must have YAML frontmatter with `name` (lowercase, numbers, and hyphens only, max 64 chars) and `description` (one sentence starting with 'Use when ...').\n"
        "- The body must be concise (maximum 40 lines), actionable, imperative checklists.\n"
        "- Format output exactly as follows for each skill:\n"
        "=== SKILL: <name> ===\n"
        "---\n"
        "name: <name>\n"
        "description: Use when <trigger condition>\n"
        "---\n"
        "# <Title>\n\n"
        "1. <Actionable rule 1>\n"
        "2. <Actionable rule 2>\n"
        "=== END ===\n\n"
        f"{runs_prompt_text}"
    )

    resolved_model = model if model is not None else make_model()
    if hasattr(resolved_model, "streaming"):
        resolved_model.streaming = True

    reply = resolved_model.invoke(prompt)
    content = reply.content if hasattr(reply, "content") else str(reply)

    written = []
    for name, text in parse_skill_blocks(content):
        if len(written) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            continue
        skill_path = out_dir / name / "SKILL.md"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(text, encoding="utf-8")
        written.append(skill_path)

    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
