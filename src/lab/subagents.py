"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when starting a task to inspect the workspace, read specifications, "
                "README files, docstrings, schema, or sample data, and identify requirements "
                "and edge cases before modifying anything. Do NOT modify files."
            ),
            "system_prompt": (
                "You are an exploration subagent. Your role is strictly read-only: inspect the workspace, "
                "read instruction specifications, READMEs, docstrings, code, and sample data. "
                "Identify all exact requirements, constraints, conventions, and edge cases. "
                "Report verified facts and file paths clearly to the caller. Do not edit or create files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use when you have clear requirements and need to execute code changes, data processing, "
                "or log analysis, run tests or scripts, and report back modified files and execution results."
            ),
            "system_prompt": (
                "You are an implementation subagent. Your role is to perform code modifications, data cleaning, "
                "or log parsing according to instructions. Run validation scripts and tests using the shell "
                "to confirm your changes. In your final report, list the exact files created or modified "
                "and the actual test/execution output."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use before concluding a task to independently verify that all requirements, house rules, "
                "and edge cases from the instructions are satisfied and tests pass. Do NOT modify files."
            ),
            "system_prompt": (
                "You are a review subagent. Your role is to independently verify results against "
                "the task specification, check for missing edge cases, formatting errors, or broken rules. "
                "Do not modify files. Run checks or tests to verify. Do not claim tests pass "
                "unless you have actually verified the output."
            ),
        },
    ]
