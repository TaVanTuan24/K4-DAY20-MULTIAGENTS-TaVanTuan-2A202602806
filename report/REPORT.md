# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Tạ Văn Tuấn | 2A202602806 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `wb/deepseek-ai/DeepSeek-V4.1-Flash`, `0`, `60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Ubuntu 24.04 (WSL2 Linux), Python 3.12.3
- Số lần chạy tác vụ đã dùng / ngân sách: 21 / 21 runs (9 pre-freeze development runs: 3 baseline learn, 3 subagents learn, 3 skills-auto-dev learn; và 12 post-freeze official runs: 3 baseline eval, 3 subagents eval, 6 skills-auto all)
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

Bảng phân loại các check thất bại trên các tác vụ học của điều kiện `baseline` (trích xuất trực tiếp từ `results/baseline/*-learn/run.json`):

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `visible_suite_passes` | B | "2 failed, 4 passed in 0.05s" (kết thúc mà không kiểm chứng/chạy lại test suite) |
| code-learn | `tests_not_modified` | A | "the original files in tests/ must not be modified" (bỏ qua đặc tả không sửa test gốc) |
| code-learn | `parse_price_all_formats` | D | "wrong for: ['$1,299.50', '(12.00)', '$1,000,000.00']" (bỏ sót định dạng số âm ngoặc đơn, dấu phẩy) |
| code-learn | `other_caller_fixed` | C | "to_csv_row returned '<InvalidOperation>'" (vá triệu chứng: sửa hàm làm gãy caller khác) |
| code-learn | `discount_rounds_half_up` | D | "wrong for: [('10.05', 10, '9.05'), ('0.05', 50, '0.03'), ('2.665', 0, '2.67')]" (bỏ sót quy tắc làm tròn nửa lên) |
| code-learn | `low_stock_follows_docstring` | A | "low_stock returned ['b', 'A', 'c']" (bỏ qua đặc tả docstring về thứ tự sắp xếp theo tồn kho) |
| code-learn | `csv_quoting_follows_docstring` | D | "to_csv_row returned 'Desk, large \"oak\",10.00,2'" (bỏ sót định dạng escape trích dẫn CSV) |
| code-learn | `rule_type_hints` | E | "RULE: every public function... has type annotations on all parameters and on the return value." |
| code-learn | `rule_regression_tests` | E | "RULE: add tests/test_regressions.py with one test function per bug you fixed... must pass." |
| code-learn | `rule_changelog` | E | "RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>'." |
| data-learn | `north_q1_revenue` | G | "FileNotFoundError: .../workspace/answer.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| data-learn | `north_q1_orders` | G | "FileNotFoundError: .../workspace/answer.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| data-learn | `top_region` | G | "FileNotFoundError: .../workspace/answer.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| data-learn | `missing_amount_orders` | G | "FileNotFoundError: .../workspace/answer.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| data-learn | `duplicate_rows_removed` | G | "FileNotFoundError: .../workspace/answer.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| data-learn | `rule_money_in_cents` | G | "FileNotFoundError: .../workspace/answer.json" (chưa thể xác định lỗi quy ước vì artifact không được tạo sau GraphRecursionError) |
| data-learn | `rule_meta_block` | G | "FileNotFoundError: .../workspace/answer.json" (chưa thể xác định lỗi quy ước vì artifact không được tạo sau GraphRecursionError) |
| data-learn | `rule_clean_csv` | E | "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents..." |
| logs-learn | `valid_structure` | G | "FileNotFoundError: .../workspace/errors.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| logs-learn | `entry_count` | G | "FileNotFoundError: .../workspace/errors.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| logs-learn | `timestamps_utc` | G | "FileNotFoundError: .../workspace/errors.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| logs-learn | `exception_fields` | G | "FileNotFoundError: .../workspace/errors.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| logs-learn | `repeat_counts` | G | "FileNotFoundError: .../workspace/errors.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| logs-learn | `counts_by_service` | G | "FileNotFoundError: .../workspace/errors.json" (chưa hoàn thành do GraphRecursionError cạn 60 bước / thiếu artifact) |
| logs-learn | `rule_service_names` | G | "FileNotFoundError: .../workspace/errors.json" (chưa thể xác định lỗi quy ước vì artifact không được tạo sau GraphRecursionError) |
| logs-learn | `rule_sorted_errors` | G | "FileNotFoundError: .../workspace/errors.json" (chưa thể xác định lỗi quy ước vì artifact không được tạo sau GraphRecursionError) |
| logs-learn | `rule_schema_header` | G | "FileNotFoundError: .../workspace/errors.json" (chưa thể xác định lỗi quy ước vì artifact không được tạo sau GraphRecursionError) |

Nhận xét:
- Phân bố nhóm lỗi: Trong 27 check thất bại của baseline trên 3 tác vụ học:
  + Nhóm G (Khác / chưa hoàn thành do `GraphRecursionError` cạn giới hạn 60 bước khiến tệp artifact không kịp ghi ra đĩa): chiếm đa số với **16/27 check** (7 check ở `data-learn`, 9 check ở `logs-learn`). Trong đó, bao gồm 5 check `rule_*` có detail là `FileNotFoundError` thay vì `RULE:`, do tác tử cạn bước trước khi tạo artifact nên không đủ bằng chứng để phân loại thành vi phạm quy ước tổ chức. Theo đúng hướng dẫn và rubric, lỗi hạ tầng không được suy diễn tùy tiện thành lỗi nhận thức của tác tử khi vết trace chưa lưu lại được bằng chứng.
  + Nhóm E (Vi phạm quy ước tổ chức theo tiêu chuẩn GUIDE: tên bắt đầu bằng `rule_` VÀ `detail` bắt đầu bằng `RULE:`): chiếm **4/27 check** (3 check ở `code-learn`: `rule_type_hints`, `rule_regression_tests`, `rule_changelog`; và 1 check ở `data-learn`: `rule_clean_csv`).
  + Nhóm kỹ thuật (A, B, C, D trên `code-learn`): chiếm **7/27 check** (A: 2 check, B: 1 check, C: 1 check, D: 3 check).
- Khả năng phòng ngừa của Skill:
  + Kỹ năng (skills) do curator sinh ra (như `preserve-tests-and-house-rules` và `deliverable-artifact-verification`) có khả năng phòng ngừa đặc biệt hiệu quả đối với **nhóm E** (quy ước tổ chức có checklist rõ ràng) và một phần nhóm D/B bằng cách cung cấp danh sách kiểm tra hành động và yêu cầu tạo đúng các tệp quy ước (`tests/test_regressions.py`, `CHANGELOG.md`, type hints) trước khi kết thúc tác vụ (minh chứng qua việc `skills-auto` sau đó đạt tuyệt đối 10/10 trên `code-learn`).
  + Tuy nhiên, kỹ năng không thể giải quyết triệt để **nhóm G** do giới hạn bước thực thi (`recursion_limit = 60`) là rào cản hạ tầng; khi dữ liệu đầu vào lớn, việc đọc thêm skill thậm chí có thể làm tăng số bước suy luận trung gian.

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
  - **Nhận xét khoa học trung thực:** Dù mô hình được cung cấp 3 subagent chuyên biệt cùng lời nhắc `SUBAGENTS_NOTE`, trong toàn bộ 6 run quan sát được mô hình DeepSeek-V4.1-Flash **không chọn delegation** (`subagent_calls = 0`) mà tự giải quyết trực tiếp qua các tool cơ bản (`execute`, `write_file`, `read_file`). Do đó, không có hiện tượng overhead trao đổi hay over-coordination giữa các subagent.
- Thông tin thiếu hoặc thừa khi giao việc: Không áp dụng do `subagent_calls = 0`.
- Ảnh hưởng đến token và thời gian: Cấu hình `subagents` tiêu thụ nhiều token hơn (trung bình 435,914 tokens/run so với 343,658 tokens của `baseline`). Tuy nhiên, do `subagent_calls` hoàn toàn bằng 0 ở cả 6 lần chạy, sự gia tăng token này không thể quy cho chi phí trao đổi hay điều phối giữa các tác tử (inter-agent communication). Thay vào đó, nó phản ánh chi phí phụ trội của system prompt (chứa thêm `SUBAGENTS_NOTE` và định nghĩa tool `task`) cùng phương sai ngẫu nhiên giữa các lần chạy.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: 1 lần chính thức (sau khi baseline learning runs hoàn tất và không phát hiện evaluation marker trong các artifacts được lưu). Số skill bị xóa: 0 skill (tất cả 3 skill sinh ra đều vượt qua bộ kiểm tra `validate_skill`).
- Đầu vào của curator: Do các vết học của baseline trước freeze bị rỗng sau khi gặp `GraphRecursionError`, việc sinh kỹ năng của curator trong thí nghiệm này được định hướng chủ yếu bởi tên các check thất bại (`name`) và chi tiết phản hồi (`detail`) từ các baseline learn run, chứ không dựa vào các vết thực thi (execution traces) phong phú.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `deliverable-artifact-verification` | Tổng quát | Đúng (hướng dẫn kiểm tra file artifact tồn tại, đúng định dạng và không rỗng) | 14 dòng, `Use when a task requires producing output files or artifacts...`. Ở dev run trước freeze, runner ghi `skills_read = 0` do `GraphRecursionError` xảy ra trước khi message history được giữ lại; trace dev rỗng nên không thể xác nhận usage từ dev trace. Trong official runs sau freeze, cả 6 run đều ghi nhận `skills_read = 3`. |
| `preserve-tests-and-house-rules` | Tổng quát | Đúng (hướng dẫn không sửa test gốc, tạo test_regressions, cập nhật CHANGELOG và type hints) | 13 dòng, `Use when modifying a package with existing tests and house rules...`. Ở dev run trước freeze, runner ghi `skills_read = 0` do `GraphRecursionError` xảy ra trước khi message history được giữ lại; trace dev rỗng nên không thể xác nhận usage từ dev trace. Trong official runs sau freeze, cả 6 run đều ghi nhận `skills_read = 3`. |
| `implement-to-docstring-edge-cases` | Tổng quát | Đúng (hướng dẫn đối chiếu docstring, xử lý định dạng tiền tệ, làm tròn và kiểu trả về) | 13 dòng, `Use when implementing or fixing functions that must match docstrings/specs...`. Ở dev run trước freeze, runner ghi `skills_read = 0` do `GraphRecursionError` xảy ra trước khi message history được giữ lại; trace dev rỗng nên không thể xác nhận usage từ dev trace. Trong official runs sau freeze, cả 6 run đều ghi nhận `skills_read = 3`. |

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

Giải thích chỉ số `skills_read = 1/6` của baseline:
- Trong bảng tổng hợp, điều kiện `baseline` ghi nhận `Runs that read a skill = 1/6`.
- Kiểm tra `results/baseline/logs-eval/trace.md` cho thấy tác tử đã thực hiện lệnh `read_file` nhắm vào đường dẫn tạm `/tmp/pytest-of-tavan/.../skills/check-data-quality/SKILL.md` sót lại từ các unit test trên host; lệnh đọc này trả về lỗi `File not found`.
- Tuy nhiên, logic đếm của runner phát hiện chuỗi con `skills/` trong tham số `file_path` và đã đếm đây là 1 lần đọc kỹ năng.
- Đây là hiện tượng **dương tính giả của chỉ số đo lường (metric false positive)**, hoàn toàn không phải do baseline thực sự truy cập hay sử dụng bộ kỹ năng tự sinh đã đóng băng trong `skills/auto/`.

## 8. Phân tích

1. **Hiệu quả trên tác vụ học vs đánh giá:**
   - So với `baseline` (0.00), điều kiện `skills-auto` cải thiện điểm số trên tác vụ **học**, đạt **0.33 điểm trung bình** (đặc biệt đạt tuyệt đối **10/10 điểm** trên `code-learn`).
   - Trên tác vụ **đánh giá**, `baseline` và `subagents` cùng đạt 0.21 điểm, trong khi `skills-auto` đạt 0.03 điểm.
   - Việc `skills-auto` tăng điểm mạnh trên tác vụ học nhưng không chuyển giao sang tác vụ đánh giá cung cấp bằng chứng phù hợp với hiện tượng **quá khớp tri thức thủ tục (procedural overfitting)**, nhất quán với các kết quả nghiên cứu được ghi nhận trong bài báo **SkillEvolBench** và **SkillsBench** (kỹ năng tự sinh từ trace có xu hướng tối ưu hóa cho ngữ cảnh tác vụ học nhưng khó tổng quát hóa sang tác vụ đánh giá mới lạ).

2. **Phân tách check kỹ thuật và check quy ước (`rule_`):**
   - Trên tác vụ học (`code-learn`), skill của curator giúp tác tử đạt **100% check quy ước house rules** (3/3: `rule_changelog`, `rule_regression_tests`, `rule_type_hints`) và bảo toàn test gốc (`tests_not_modified`), nâng điểm từ 0/10 lên 10/10.
   - Trên tác vụ đánh giá (`code-eval`), tác vụ này xuất hiện quy ước house rule hoàn toàn mới: `rule_version_bump` (yêu cầu tăng version package). Bộ skill tự sinh từ `code-learn` chỉ biết về CHANGELOG và test_regressions nên **không thể giúp đỡ check quy ước mới này**, vì tri thức thủ tục chưa từng quan sát thấy quy ước tăng version.

3. **Phân tích theo vết và `skills_read`:**
   - **Phân biệt bằng chứng phát triển và chính thức:** Ở các dev run trước freeze, `trace.md` rỗng do `GraphRecursionError` nên không thể xác nhận hành vi sử dụng skill từ dev trace. Tuy nhiên, ở các lần chạy chính thức sau freeze (`results/skills-auto/`), cả 6 run đều ghi nhận `skills_read = 3` và trace được lưu đầy đủ: cơ chế Progressive Disclosure hoạt động hiệu quả khi tác tử chủ động đọc cả 3 skill ngay các lượt đầu.
   - **Check skill giúp đạt:** `rule_changelog` và `rule_regression_tests` trên `code-learn` chính thức. Vết trace cho thấy tác tử đọc `preserve-tests-and-house-rules/SKILL.md` và thực thi từng mục checklist: tạo `tests/test_regressions.py`, viết format `- fix(<function>): ...` vào CHANGELOG.
   - **Check skill không giúp:** `rule_version_bump` trên `code-eval`. Lý do: bộ skill thiếu quy ước này. Ngoài ra, việc đọc và đối chiếu 3 skill làm tăng số bước suy luận trung gian, khiến tác tử chạm ngưỡng 60 bước (`recursion_limit`) trước khi kịp hoàn thiện toàn bộ mã nguồn `bookings/billing.py`.

4. **Phân tích chi phí và hiệu quả token:**
   - Token trung bình trên mỗi run: `baseline` = 343,658; `skills-auto` = 347,436; `subagents` = 435,914.
   - Hiệu quả token được tính theo công thức chuẩn hóa `efficiency = mean_score / (mean_tokens / 100000)`:
     * Trên tác vụ học (learn):
       - `baseline`: 0.00 / 3.86189 = **0.00 score / 100k tokens**
       - `subagents`: 0.30 / 4.08390 = **0.0735 score / 100k tokens**
       - `skills-auto`: 0.3333 / 3.04014 = **0.1096 score / 100k tokens** (hoặc 0.33 / 3.04 = **0.1085 score / 100k tokens**) -> `skills-auto` đạt hiệu quả token cao nhất trên tập học nhờ hoàn thành sớm `code-learn` với 199,745 tokens.
     * Trên tác vụ đánh giá (eval):
       - `baseline`: 0.2121 / 3.01128 = **0.0704 score / 100k tokens** (hoặc 0.21 / 3.01 = **0.0697 score / 100k tokens**) -> `baseline` đạt hiệu quả token tốt nhất trên tập đánh giá.
       - `subagents`: 0.2121 / 4.63438 = **0.0458 score / 100k tokens** (hoặc 0.21 / 4.63 = **0.0453 score / 100k tokens**)
       - `skills-auto`: 0.0303 / 3.90859 = **0.0078 score / 100k tokens** (hoặc 0.03 / 3.91 = **0.0077 score / 100k tokens**)
   - **Đa tác tử (`subagents`):** Tiêu tốn nhiều token nhất (trung bình 435,914 tokens/run) nhưng `subagent_calls = 0` và không mang lại cải thiện điểm số nào so với `baseline`. Sự chênh lệch token xuất phát từ prompt/schema overhead và phương sai ngẫu nhiên. Vì vậy, với mô hình DeepSeek-V4.1-Flash trong cấu hình này, việc trang bị subagents là **không đáng chi phí**.

5. **Rò rỉ dữ liệu và quá khớp:**
   - **Kiểm soát rò rỉ dữ liệu (Data Leakage):** Không tìm thấy bất kỳ dấu hiệu đánh giá nào (evaluation markers) trong các vết học trước freeze được lưu lại, và bộ kỹ năng tự sinh không chứa tên định danh tác vụ hay nội dung riêng của tập đánh giá. Bộ kỹ năng tự sinh có guardrail tốt: chỉ kiểm tra các tệp bên trong sandbox/workspace và không tìm kiếm các công cụ chấm điểm hay tệp ngoài. Tuy nhiên, do một số vết học trước freeze bị rỗng khi gặp GraphRecursionError, bản thân các vết được lưu không thể là bằng chứng tuyệt đối chứng minh sự cách ly hoàn toàn của hệ thống tệp trong toàn bộ quá trình chạy.
   - **Quá khớp (Overfitting):** Thể hiện ở việc tác tử bám sát cấu trúc của bài học `inventory` và cố gắng áp dụng cứng nhắc checklist vào `bookings`, làm tăng thời gian suy luận và dẫn tới cạn bước ở tác vụ đánh giá.

6. **Phân tích nhiễu (Noise):**
   - Điểm `code-learn` ở dev run trước freeze (`results/skills-auto-dev`) đạt **9/10** (0.90).
   - Điểm `code-learn` sau đóng băng (`results/skills-auto`) đạt **10/10** (1.00).
   - Chênh lệch 1 check (10%) là phù hợp với phương sai ngẫu nhiên giữa các lần chạy của mô hình ngôn ngữ lớn (run-to-run variance), nhưng một cặp quan sát đơn lẻ là chưa đủ để ước lượng phương sai một cách đáng tin cậy. Do đó, các khác biệt điểm nhỏ cần được xem xét thận trọng và không nên suy diễn thành biến đổi cấu trúc.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập dữ liệu nhỏ:** Mỗi vai trò chỉ gồm 3 tác vụ (`code`, `data`, `logs`), do đó các chỉ số thống kê có khoảng tin cậy tương đối rộng.
2. **Đánh giá đơn lẻ (single-run evaluation):** Mỗi cấu hình chỉ chạy 1 lần chính thức sau freeze để tuân thủ ngân sách token, khiến kết quả có thể bị ảnh hưởng bởi tính ngẫu nhiên của mô hình.
3. **Giới hạn số bước cố định (`recursion_limit = 60`):** Đối với các tác vụ phân tích log và dữ liệu bán hàng có độ dài chuỗi lớn, ngưỡng 60 bước là tương đối chặt chẽ, dẫn đến lỗi cạn bước trước khi agent hoàn thiện việc ghi artifact ra đĩa.
4. **Tính cách ly hệ thống tệp không tuyệt đối đối với thực thi shell (Filesystem isolation is not absolute for shell execution):** Mặc dù các công cụ file thao tác trong sandbox root, `LocalShellBackend` thực thi lệnh shell vẫn có thể duyệt các đường dẫn trên host như `/tmp` và `/mnt` dưới môi trường WSL. Vết trace chính thức cho thấy mô hình đã duyệt các đường dẫn này (ví dụ cố đọc file test tạm trong `/tmp`). Điều này có thể làm nhiễu phép đo nếu tồn tại các tệp artifact từ các lần chạy trước trên host, dù bản thân các skill đã đóng băng không chứa dấu hiệu đánh giá.

## 10. Kết luận

Thí nghiệm cung cấp bằng chứng cho thấy cơ chế tự sinh kỹ năng (self-evolving skills) giúp nâng cao hiệu quả tác vụ cụ thể: trên `code-learn`, `skills-auto` nâng điểm từ 0/10 lên 10/10 tuyệt đối, giúp điểm trung bình tập học tăng từ 0.00 lên 0.33. Tuy nhiên, sự cải thiện này không chuyển giao sang tập đánh giá (0.03 so với 0.21 của baseline), phù hợp với hiện tượng quá khớp tri thức thủ tục đã được ghi nhận trong nghiên cứu khoa học. Cấu hình đa tác tử không phát huy hiệu quả với mô hình DeepSeek-V4.1-Flash do mô hình tự giải quyết tác vụ mà không phân rã (`subagent_calls = 0`). Hiện tượng cạn bước (`recursion_limit = 60`) trên các tác vụ xử lý dữ liệu và log lớn cho thấy rào cản hạ tầng cần được phân biệt rõ với năng lực nhận thức của tác tử. Đề xuất cải tiến tiếp theo là bổ sung cơ chế truy xuất kỹ năng động (dynamic skill retrieval/pruning) nhằm giảm tải ngữ cảnh và tăng ngưỡng recursion limit cho các tác vụ khối lượng lớn.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest` kiểm tra 32 unit test ban đầu.
  2. `python scripts/tour.py` phân tích công cụ và hướng dẫn hành vi.
  3. `python -m lab.runner --condition baseline --tasks learn` (học đường cơ sở; không phát hiện evaluation marker trong artifacts được lưu; lưu ý một số trace rỗng).
  4. `python -m lab.runner --condition subagents --tasks learn` (học đa tác tử; không phát hiện evaluation marker trong artifacts được lưu; lưu ý một số trace rỗng).
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
