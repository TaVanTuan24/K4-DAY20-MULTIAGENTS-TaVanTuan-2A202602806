# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Tạ Văn Tuấn | 2A202602806 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `wb/deepseek-ai/DeepSeek-V4.1-Flash`, `0`, `60`
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents 0.7.21`, Ubuntu 24.04 (WSL2), Python 3.12.3
- Số lần chạy tác vụ đã dùng / ngân sách: 21 / 21 runs (15 learning/dev runs + 6 official eval runs)
- Commit của tag `freeze`: (sẽ cập nhật sau khi tạo tag `freeze`)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Do mô hình DeepSeek-V4.1-Flash có xu hướng tự hoàn thành tác vụ trực tiếp trong một lượt hội thoại thay vì phân rã và gọi subagent (`subagent_calls` có khả năng tiếp tục bằng 0), điểm số trung bình của điều kiện `subagents` trên tác vụ đánh giá được dự đoán sẽ tương đương với `baseline`, trong khi chi phí token có thể tăng nhẹ do system prompt chứa thêm `SUBAGENTS_NOTE`.
- H2 (skills-auto so với baseline): Bộ kỹ năng tự sinh từ curator (`deliverable-artifact-verification`, `preserve-tests-and-house-rules`, `implement-to-docstring-edge-cases`) tập trung vào việc tuân thủ quy ước house rules (CHANGELOG, regressions test) và kiểm tra artifact trước khi kết thúc. Do đó, `skills-auto` được dự đoán sẽ cải thiện điểm số so với `baseline` ở các tác vụ có house rules nghiêm ngặt (như `code` family), nhưng hiệu quả chuyển giao có thể bị giới hạn hoặc quá khớp (overfitting) trên các tác vụ đòi hỏi logic dữ liệu mới lạ (phù hợp với các phát hiện từ SkillsBench và SkillEvolBench).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình trên tác vụ học (learn) ở cả ba điều kiện được dự đoán sẽ cao hơn điểm số trên tác vụ đánh giá (eval), do tác vụ đánh giá có thêm các trường hợp biên và kiểm thử nghiêm ngặt mà agent chưa từng quan sát trong quá trình chạy thử.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Danh sách các công cụ mặc định cung cấp cho mô hình gồm: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. Trong đó công cụ chạy lệnh shell trên hệ điều hành là `execute`.
2. Về subagent `general-purpose`: Tool `task` mô tả đây là agent đa năng dùng để nghiên cứu câu hỏi phức tạp, tìm kiếm file và nội dung khi chưa chắc chắn khớp ngay lần đầu, và thực thi các chuỗi tác vụ nhiều bước. Về ngữ cảnh (context): mỗi lần gọi là phi trạng thái (stateless by default), subagent chỉ nhìn thấy nội dung prompt mà agent chính truyền vào và trả về một báo cáo cuối cùng duy nhất (`the agent sees only the prompt you give it and returns a single final report`).
3. Trích dẫn chỉ dẫn hành vi (behavioral guidance):
   - Từ mô tả `task`: *"Tell the agent whether to create content, analyze, or only research, since it can't necessarily see the user's intent unless it inherits your conversation, as noted per agent type below."* (và *"Each invocation is stateless by default: Put full detail in the prompt and state exactly what it should return"*).
   - Từ mô tả `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| | | | |

Nhận xét: nhóm lỗi nào chiếm đa số? Skill có thể phòng ngừa nhóm đó không?

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc):
- Ảnh hưởng đến token và thời gian:

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do:

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| | | | |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
