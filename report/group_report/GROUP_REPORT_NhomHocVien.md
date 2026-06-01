# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Nhóm Học Viên AI
- **Team Members**: Học viên 1
- **Deployment Date**: 2026-06-01

---

## 1. Executive Summary

*Dự án đã nâng cấp thành công từ một Chatbot thông thường lên hệ thống ReAct Agent, có khả năng tư duy đa bước và gọi công cụ linh hoạt.*

- **Success Rate**: 100% trên các kịch bản test đa bước cơ bản.
- **Key Outcome**: Agent đã có thể xử lý hoàn hảo các câu hỏi phức tạp (VD: "Kiểm tra kho hàng iPhone và tính phí ship về Hà Nội") bằng cách tự động gọi lần lượt các Tool `check_stock` và `calc_shipping` một cách hoàn toàn tự động, thay vì trả lời bừa như Chatbot thông thường.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
Chúng tôi đã cài đặt vòng lặp **Thought-Action-Observation** bên trong `src/agent/agent.py`.
- **Thought**: Agent phân tích xem cần phải làm gì tiếp theo.
- **Action**: Dùng Regex trích xuất tên hàm và tham số.
- **Observation**: Gọi hàm bằng cơ chế gọi động (dynamic function calling) thông qua `eval()` hoặc string-passing, sau đó gắn kết quả trả về vào ngữ cảnh cho bước suy luận tiếp theo.

### 2.2 Tool Definitions (Inventory)
| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `check_stock` | `string` | Kiểm tra số lượng tồn kho của một sản phẩm. |
| `calc_shipping` | `tuple/string` | Tính phí giao hàng dựa vào khối lượng và điểm đến. |
| `get_discount` | `string` | Kiểm tra mã giảm giá và trả về phần trăm giảm. |

### 2.3 LLM Providers Used
- **Primary**: GPT-4o (OpenAIProvider)
- **Secondary (Backup)**: Phi-3 GGUF (LocalProvider - gặp sự cố môi trường Windows nên chuyển sang OpenAI).

---

## 3. Telemetry & Performance Dashboard

- **Average Latency (P50)**: ~2500ms (Do phải gọi LLM nhiều lần trong vòng lặp)
- **Max Latency (P99)**: ~5000ms
- **Average Tokens per Task**: ~400 tokens (Prompt ngày càng dài ra sau mỗi lần append Observation)
- **Total Cost of Test Suite**: ~$0.01 (GPT-4o)

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Lỗi vòng lặp vô hạn do LLM chat nhảm
- **Input**: "ẽit" (Gõ nhầm chữ exit)
- **Observation**: LLM phản hồi "Xin lỗi, có vẻ như bạn đã gặp lỗi đánh máy..." mà không dùng format `Final Answer: ...`. Hệ thống báo lỗi Parse và ép LLM trả lời lại. LLM tiếp tục chat nhảm, dẫn đến việc cạn kiệt 5 steps (`max_steps_reached`).
- **Root Cause**: LLM không nhận diện được đây là một task cần dùng tool, nên chuyển sang chế độ Chat giao tiếp thông thường, vi phạm nghiêm trọng quy tắc Format của ReAct Prompt.
- **Fix/Guardrail**: Thêm logic tự động thoát nếu LLM không trả về đúng chuẩn quá 3 lần, hoặc sửa System prompt để ép LLM xuất `Final Answer:` ngay cả khi chỉ đang nói chuyện phiếm.

---

## 5. Ablation Studies & Experiments

### Experiment 1 (Bonus): Chatbot vs Agent
| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q (Chào hỏi) | Trả lời tự nhiên, nhanh | Cứng nhắc, đôi khi bị ép dùng Final Answer | **Chatbot** |
| Multi-step (Mua hàng + Mã giảm giá) | Tự bịa (Hallucinated) phí ship và tồn kho | Gọi đúng 2 tool, đưa số liệu chính xác 100% | **Agent** |

---

## 6. Production Readiness Review

- **Security**: Đang dùng `eval()` để parse arguments từ LLM. Trên môi trường thực tế (Production), cần chuyển sang chuẩn JSON parsing (hoặc OpenAI Function Calling / Structured Outputs) để tránh lỗi Injection.
- **Guardrails**: Đã set giới hạn `max_steps = 5` để tránh việc Agent bị lặp vô hạn và đốt sạch tiền API.
- **Bugs Fixed**: Đã xử lý triệt để lỗi UnicodeEncodeError trên Windows Terminal để đảm bảo hiển thị đúng dấu Tiếng Việt.
