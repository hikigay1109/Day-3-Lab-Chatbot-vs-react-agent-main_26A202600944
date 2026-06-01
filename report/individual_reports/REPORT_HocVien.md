# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Quang Minh
- **Student ID**: 26A202600994
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

Tôi đã đóng góp trực tiếp vào việc xây dựng bộ não cốt lõi của Agent và xử lý lỗi hệ thống:

- **Modules Implementated**: Xây dựng thành công vòng lặp ReAct trong `src/agent/agent.py` và luồng chạy động trong `run_agent.py`.
- **Code Highlights**:
  Đã viết logic parse (phân tách) định dạng Thought-Action bằng Regex:
  ```python
  action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", result)
  if action_match:
      tool_name = action_match.group(1)
      tool_args = action_match.group(2)
      observation = self._execute_tool(tool_name, tool_args)
  ```
- **Xử lý sự cố môi trường**: Sửa lỗi `UnicodeEncodeError: cp1252` trên Windows bằng cách reconfigure lại chuẩn mã hóa của `sys.stdout` sang `utf-8`.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: Khi nhập thử một chữ rác ("ẽit"), Agent bị kẹt trong vòng lặp vô hạn và báo lỗi `I could not find the answer within the maximum number of steps`.
- **Log Source**: `logs/...` (Ghi nhận sự kiện `AGENT_STEP` lặp 5 lần với phản hồi "Xin chào, làm thế nào tôi có thể giúp...").
- **Diagnosis**: Agent (GPT-4o) nhận thấy input là một câu giao tiếp thông thường, nên nó phản hồi tự nhiên thay vì tuân thủ format `Action:` hoặc `Final Answer:`. Do code chỉ tìm đúng 2 pattern này, nó coi phản hồi của LLM là lỗi (Error) và ép LLM trả lời lại. Cứ thế lặp đến khi max steps.
- **Solution**: Đã hiểu được bản chất "khắt khe" của ReAct. Giải pháp tối ưu là nới lỏng Regex (nếu không thấy Action thì mặc định gán toàn bộ câu nói đó vào Final Answer) hoặc quy định trong System Prompt: "Nếu người dùng chỉ muốn giao tiếp thông thường, HÃY GHI LÀ Final Answer: [Câu trả lời của bạn]".

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1.  **Reasoning**: Nhờ có khối `Thought`, Agent được chia nhỏ suy nghĩ, giúp nó phân tích logic theo từng bước (A -> B -> C) thay vì bị ngợp và phải đoán mò (hallucination) như Chatbot.
2.  **Reliability**: Ở những tác vụ giao tiếp (small-talk) thông thường, Agent lại thể hiện **tệ hơn** Chatbot vì nó bị gò bó bởi format và tốn thời gian (latency) để xử lý các khối văn bản vô nghĩa (Thought).
3.  **Observation**: Kết quả trả về (Observation) từ thế giới thực đóng vai trò như một mỏ neo, giúp Agent nhận thức được trạng thái hiện tại (VD: kho có 100 cái) để quyết định làm gì tiếp theo, từ đó hoàn toàn chấm dứt tình trạng "ảo giác dữ liệu" của LLM.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Chuyển từ cơ chế Regex-parsing thô sơ sang sử dụng tính năng **Structured Outputs** (JSON Schema) hoặc **Function Calling** native của OpenAI để đảm bảo 100% LLM trả về đúng tên hàm và đúng kiểu dữ liệu.
- **Performance**: Khi số lượng công cụ lên tới hàng chục, việc nhét tất cả `tool_descriptions` vào System Prompt sẽ rất tốn Tokens. Có thể cải tiến bằng cách dùng **Vector DB** để truy xuất (Retrieve) chỉ những Tool liên quan nhất đến câu hỏi của User rồi mới đưa vào Prompt.
