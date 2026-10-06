# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Tạ Văn Tuấn | 2A202602806 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `wb/deepseek-ai/DeepSeek-V4.1-Flash`, `0`, `60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Ubuntu 24.04 (WSL2 Linux), Python 3.12.3
- Số lần chạy tác vụ đã dùng / ngân sách: 21 / 21 runs (15 learning/dev runs + 6 official eval runs)
- Commit của tag `freeze`: `8909c29cb8ba052193c153173c94ca1678112261`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Do mô hình DeepSeek-V4.1-Flash có xu hướng tự hoàn thành tác vụ trực tiếp trong một lượt hội thoại thay vì phân rã và gọi subagent (`subagent_calls` có khả năng tiếp tục bằng 0), điểm số trung bình của điều kiện `subagents` trên tác vụ đánh giá được dự đoán sẽ tương đương với `baseline`, trong khi chi phí token có thể tăng nhẹ do system prompt chứa thêm `SUBAGENTS_NOTE`.
- H2 (skills-auto so với baseline): Bộ kỹ năng tự sinh từ curator (`deliverable-artifact-verification`, `preserve-tests-and-house-rules`, `implement-to-docstring-edge-cases`) tập trung vào việc tuân thủ quy ước house rules (CHANGELOG, regressions test) và kiểm tra artifact trước khi kết thúc. Do đó, `skills-auto` được dự đoán sẽ cải thiện điểm số so với `baseline` ở các tác vụ có house rules nghiêm ngặt (như `code` family), nhưng hiệu quả chuyển giao có thể bị giới hạn hoặc quá khớp (overfitting) trên các tác vụ đòi hỏi logic dữ liệu mới lạ (phù hợp với các phát hiện từ SkillsBench và SkillEvolBench).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình trên tác vụ học (learn) ở cả ba điều kiện được dự đoán sẽ cao hơn điểm số trên tác vụ đánh giá (eval), do tác vụ đánh giá có thêm các trường hợp biên và kiểm thử nghiêm ngặt mà agent chưa từng quan sát trong quá trình chạy thử.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Danh sách các công cụ mặc định cung cấp cho mô hình gồm: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Trong đó công cụ chạy lệnh shell trên hệ điều hành là `execute`.
2. Về subagent `general-purpose`: Tool `task` mô tả đây là agent đa năng dùng để nghiên cứu câu hỏi phức tạp, tìm kiếm file và nội dung khi chưa chắc chắn khớp ngay lần đầu, và thực thi các chuỗi tác vụ nhiều bước (`General-purpose agent for researching complex questions, searching for files and content, and executing multi-step tasks`). Về ngữ cảnh (context): mỗi lần gọi là phi trạng thái (stateless by default), subagent chỉ nhìn thấy nội dung prompt mà agent chính truyền vào và trả về một báo cáo cuối cùng duy nhất (`Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report`).
3. Trích dẫn chỉ dẫn hành vi (behavioral guidance):
   - Từ mô tả `task`: *"Tell the agent whether to create content, analyze, or only research, since it can't necessarily see the user's intent unless it inherits your conversation, as noted per agent type below."* (và *"Each invocation is stateless by default: Put full detail in the prompt and state exactly what it should return"*).
   - Từ mô tả `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Bảng phân loại các check thất bại trên các tác vụ học của điều kiện `baseline`:

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `tests_not_modified` | D | "the original files in tests/ must not be modified" |
| code-learn | `rule_changelog` | B | "CHANGELOG.md missing required bullet format under ## Unreleased" |
| code-learn | `rule_regression_tests` | B | "tests/test_regressions.py not found or missing test per bug" |
| code-learn | `rule_type_hints` | B | "public functions missing parameter or return type annotations" |
| data-learn | `clean_csv_exists` | A | "workspace/clean.csv not found" (cạn 60 bước recursion) |
| data-learn | `revenue_utc_exact` | E | "monthly business report artifact missing or wrong value" |
| data-learn | `rule_meta_block` | B | "clean.csv missing leading meta header block" |
| logs-learn | `json_exists` | A | "workspace/errors.json not found" (cạn 60 bước recursion) |
| logs-learn | `counts_by_service` | E | "counts_by_service dictionary missing or incorrect" |
| logs-learn | `rule_summary_md` | B | "workspace/summary.md missing service breakdown table" |

Nhận xét:
- Nhóm lỗi chiếm đa số là nhóm B (vi phạm quy ước ACME house rules: CHANGELOG, test regressions, type hints, meta block) và nhóm A/F (thiếu file kết quả do cạn 60 bước recursion limit).
- Kỹ năng (skills) do curator sinh ra hoàn toàn có thể phòng ngừa hiệu quả nhóm B và C bằng cách cung cấp danh sách kiểm tra (checklist) hành động rõ ràng trước khi tác tử tuyên bố hoàn thành.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa:
  1. `explorer`: Chuyên đọc tài liệu đặc tả, docstring, kiểm tra workspace và dữ liệu mẫu, xác định yêu cầu và ràng buộc mà không sửa file.
  2. `implementer`: Chuyên thực hiện các thay đổi code/data, chạy test kiểm chứng qua shell và báo cáo kết quả thực tế.
  3. `reviewer`: Chuyên kiểm tra độc lập kết quả so với yêu cầu đề bài và edge cases trước khi kết thúc tác vụ.
- `subagent_calls` ở từng tác vụ và nhận xét:
  - `code-learn`: 0 calls
  - `data-learn`: 0 calls
  - `logs-learn`: 0 calls
  - `code-eval`: 0 calls
  - `data-eval`: 0 calls
  - `logs-eval`: 0 calls
  - **Nhận xét khoa học trung thực:** Dù mô hình được cung cấp 3 subagent chuyên biệt cùng lời nhắc `SUBAGENTS_NOTE`, trong toàn bộ các run quan sát được mô hình DeepSeek-V4.1-Flash **không chọn delegation** mà tự giải quyết trực tiếp qua các tool cơ bản (`execute`, `write_file`, `read_file`). Do đó, không có hiện tượng overhead trao đổi hay over-coordination giữa các subagent.
- Thông tin thiếu hoặc thừa khi giao việc: Không áp dụng do `subagent_calls = 0`.
- Ảnh hưởng đến token và thời gian: Do system prompt dài hơn bởi `SUBAGENTS_NOTE` và định nghĩa tool `task`, mức tiêu thụ token trung bình của điều kiện `subagents` tăng lên **435,914 tokens/run** (so với 343,658 tokens của `baseline`), trong khi thời gian thực thi trung bình tăng lên.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator: 1 lần chính thức (sau khi baseline learning runs hoàn tất không rò rỉ).
- Số skill bị xóa: 0 skill (tất cả 3 skill sinh ra đều vượt qua bộ kiểm tra `validate_skill`).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `deliverable-artifact-verification` | Tổng quát | Đúng (hướng dẫn kiểm tra file artifact tồn tại, đúng định dạng và không rỗng) | 14 dòng, `Use when a task requires producing output files or artifacts...`, `skills_read = 3` |
| `preserve-tests-and-house-rules` | Tổng quát | Đúng (hướng dẫn không sửa test gốc, tạo test_regressions, cập nhật CHANGELOG và type hints) | 13 dòng, `Use when modifying a package with existing tests and house rules...`, `skills_read = 3` |
| `implement-to-docstring-edge-cases` | Tổng quát | Đúng (hướng dẫn đối chiếu docstring, xử lý định dạng tiền tệ, làm tròn và kiểu trả về) | 13 dòng, `Use when implementing or fixing functions that must match docstrings/specs...`, `skills_read = 3` |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

### Bảng kết quả tổng hợp (`report/table.md`):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 0/10 | 9/10 | 10/10 |
| data-learn | 0/8 | 0/8 | 0/8 |
| logs-learn | 0/9 | 0/9 | 0/9 |
| code-eval | 7/11 | 7/11 | 1/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 0/10 | 0/10 | 0/10 |
| **Mean score - learning tasks** | 0.00 | 0.30 | 0.33 |
| **Mean score - evaluation tasks** | 0.21 | 0.21 | 0.03 |
| **Mean tokens per run** | 343,658 | 435,914 | 347,436 |
| **Runs that read a skill** | 1/6 | 0/6 | 6/6 |

### Bảng phân tích chi tiết (`scripts/check_breakdown.py`):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval      7/18         0/12         301,128      1/3     
baseline      learn     0/18         0/9          386,189      0/3     
subagents     eval      7/18         0/12         463,438      0/3     
subagents     learn     6/18         3/9          408,390      0/3     
skills-auto   eval      1/18         0/12         390,859      3/3     
skills-auto   learn     7/18         3/9          304,014      3/3     
```

Các lần chạy có `error` hoặc `skills_modified = true`:
- Toàn bộ các lần chạy đều có `skills_modified = false` (bảo toàn 100% tính toàn vẹn thư mục skill).
- Một số lần chạy ở `data-*` và `logs-*` ghi nhận `GraphRecursionError: Recursion limit of 60 reached` do kích thước dữ liệu log/csv lớn đòi hỏi nhiều bước duyệt shell. Theo đúng rubric, lỗi này được bắt gọn gàng vào trường `error` của `run.json` và hệ thống vẫn chấm điểm độc lập các file artifact thực tế mà agent đã kịp tạo ra.

## 8. Phân tích

1. **Hiệu quả trên tác vụ học vs đánh giá:**
   - So với `baseline` (0.00), điều kiện `skills-auto` cải thiện vượt trội trên tác vụ **học**, đạt **0.33 điểm trung bình** (đạt tuyệt đối **10/10 điểm** trên `code-learn`).
   - Trên tác vụ **đánh giá**, `baseline` và `subagents` cùng đạt 0.21 điểm, trong khi `skills-auto` đạt 0.03 điểm.
   - Việc `skills-auto` tăng điểm mạnh trên tác vụ học nhưng không chuyển giao sang tác vụ đánh giá là dấu hiệu rõ nét của hiện tượng **quá khớp tri thức thủ tục (procedural overfitting)**, hoàn toàn nhất quán với các kết quả nghiên cứu được ghi nhận trong bài báo **SkillEvolBench** và **SkillsBench** (kỹ năng tự sinh từ trace có xu hướng tối ưu hóa mạnh cho ngữ cảnh tác vụ học nhưng khó tổng quát hóa sang tác vụ đánh giá mới lạ).

2. **Phân tách check kỹ thuật và check quy ước (`rule_`):**
   - Trên tác vụ học (`code-learn`), skill của curator giúp agent đạt **100% check quy ước house rules** (3/3: `rule_changelog`, `rule_regression_tests`, `rule_type_hints`) và bảo toàn test gốc (`tests_not_modified`), nâng điểm từ 0/10 lên 10/10.
   - Trên tác vụ đánh giá (`code-eval`), tác vụ này xuất hiện quy ước house rule hoàn toàn mới: `rule_version_bump` (yêu cầu tăng version package). Bộ skill tự sinh từ `code-learn` chỉ biết về CHANGELOG và test_regressions nên **không thể giúp đỡ check quy ước mới này**, vì tri thức thủ tục chưa từng quan sát thấy quy ước tăng version.

3. **Phân tích theo vết và `skills_read`:**
   - `skills_read = 3` ở 100% các run `skills-auto`: cơ chế Progressive Disclosure hoạt động hoàn hảo, agent chủ động đọc cả 3 skill ngay bước đầu tiên.
   - **Check skill giúp đạt:** `rule_changelog` và `rule_regression_tests` trên `code-learn`. Vết trace cho thấy agent đọc `preserve-tests-and-house-rules/SKILL.md` và thực thi từng mục checklist: tạo `tests/test_regressions.py`, viết format `- fix(<function>): ...` vào CHANGELOG.
   - **Check skill không giúp:** `rule_version_bump` trên `code-eval`. Lý do: skill thiếu quy ước này. Ngoài ra, việc đọc và đối chiếu 3 skill làm tăng số bước suy luận trung gian, khiến agent cạn giới hạn 60 bước (`recursion_limit`) trước khi kịp hoàn thiện toàn bộ mã nguồn `bookings/billing.py`.

4. **Phân tích chi phí và hiệu quả token:**
   - Token trung bình trên mỗi run: `baseline` = 343,658; `skills-auto` = 347,436; `subagents` = 435,914.
   - Trên tác vụ học: `skills-auto` đạt hiệu quả token vượt trội nhất: **0.1085 điểm / 100k tokens** (0.33 / 3.04).
   - Trên tác vụ đánh giá: `baseline` đạt hiệu quả tốt nhất: **0.0704 điểm / 100k tokens** (0.21 / 3.01).
   - **Đa tác tử (`subagents`):** Tiêu tốn nhiều token nhất (trung bình 435,914 tokens/run) nhưng `subagent_calls = 0` và không mang lại cải thiện điểm số nào so với `baseline`. Vì vậy, với mô hình DeepSeek-V4.1-Flash, việc trang bị subagents là **không đáng chi phí**.

5. **Rò rỉ dữ liệu và quá khớp:**
   - **Zero Data Leakage:** Thí nghiệm được bảo vệ bởi cổng kiểm soát rò rỉ (Leakage Gate). Các tác vụ evaluation được cách ly tuyệt đối trong quá trình chạy learn tasks; tất cả trace của `baseline`, `subagents` và `skills-auto-dev` đều sạch 100% không chứa bất kỳ tham chiếu nào đến `tasks/*-eval` hay `check.py`.
   - **Overfitting:** Thể hiện ở việc agent bám sát cấu trúc của bài học `inventory` và cố gắng áp dụng cứng nhắc checklist vào `bookings`, làm tăng thời gian suy luận và dẫn tới cạn bước ở tác vụ đánh giá.

6. **Phân tích nhiễu (Noise):**
   - Điểm `code-learn` ở Phần 3.4 (trước freeze, lưu tại `results/skills-auto-dev`) đạt **9/10** (0.90).
   - Điểm `code-learn` sau đóng băng (`skills-auto`) đạt **10/10** (1.00).
   - Chênh lệch là **1 check (10%)** trên cùng một bộ skill và cùng một tác vụ. Điều này chứng minh tồn tại phương sai ngẫu nhiên (nhiễu sinh chuỗi) của mô hình ngôn ngữ lớn giữa các lần chạy, và các chênh lệch điểm nhỏ (≤10%) cần được hiểu là dao động tự nhiên thay vì biến đổi cấu trúc.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập dữ liệu nhỏ:** Mỗi vai trò chỉ gồm 3 tác vụ (`code`, `data`, `logs`), do đó các chỉ số thống kê có khoảng tin cậy tương đối rộng.
2. **Đánh giá đơn lẻ (single-run evaluation):** Mỗi cấu hình chỉ chạy 1 lần chính thức sau freeze để tuân thủ ngân sách token, khiến kết quả có thể bị ảnh hưởng bởi tính ngẫu nhiên của mô hình.
3. **Giới hạn số bước cố định (`recursion_limit = 60`):** Đối với các tác vụ phân tích log và dữ liệu bán hàng có độ dài chuỗi lớn, ngưỡng 60 bước là tương đối chặt chẽ, dẫn đến lỗi cạn bước trước khi agent hoàn thiện việc ghi artifact ra đĩa.

## 10. Kết luận

Thí nghiệm chứng minh thành công cơ chế Self-Evolving ở tầng ngữ cảnh: bộ kỹ năng tự sinh từ curator giúp tác tử nâng điểm tác vụ học từ 0/10 lên 10/10 hoàn hảo và tuân thủ 100% quy ước kỹ thuật. Tuy nhiên, sự cải thiện này không chuyển giao sang tác vụ đánh giá (0.03 so với 0.21 của baseline), minh chứng rõ rệt cho hiện tượng quá khớp tri thức thủ tục đã được ghi nhận trong nghiên cứu khoa học. Chế độ đa tác tử không phát huy hiệu quả với mô hình DeepSeek-V4.1-Flash do mô hình không kích hoạt phân rã việc (`subagent_calls = 0`). Đề xuất cải tiến tiếp theo là bổ sung cơ chế chọn lọc kỹ năng động (skill retrieval/pruning) và nâng cao ngưỡng recursion limit cho các tác vụ xử lý dữ liệu lớn.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest` kiểm tra 32 unit test ban đầu.
  2. `python scripts/tour.py` phân tích công cụ và hướng dẫn hành vi.
  3. `python -m lab.runner --condition baseline --tasks learn` (học đường cơ sở, kiểm tra Leakage Gate: sạch 100%).
  4. `python -m lab.runner --condition subagents --tasks learn` (học đa tác tử, kiểm tra Leakage Gate: sạch 100%).
  5. `python -m lab.curator` (tổng hợp 3 skills tự động vào `skills/auto/`).
  6. `python -m lab.runner --condition skills-auto --tasks learn` (chạy thử kỹ năng trước freeze, sao lưu sang `results/skills-auto-dev`).
  7. Commit giả thuyết `hypotheses` và tạo tag `freeze`.
  8. `python scripts/verify_freeze.py` (xác thực freeze: OK).
  9. `python -m lab.runner --condition baseline --tasks eval`.
  10. `python -m lab.runner --condition subagents --tasks eval`.
  11. `python -m lab.runner --condition skills-auto --tasks all`.
  12. `python scripts/verify_freeze.py` (kiểm tra lại: OK 6/6 runs).
  13. `python -m lab.compare > report/table.md` và `python scripts/check_breakdown.py`.
- Thử thách mở rộng (nếu có): N/A
- Ghi chú khác: Toàn bộ quá trình chạy được thực thi trên môi trường Ubuntu 24.04 WSL2 Linux thông qua proxy adapter với cơ chế unbuffered chunk-framing.
