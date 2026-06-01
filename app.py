import os
import sys
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.agent import ReActAgent

app = Flask(__name__, static_folder='static')
CORS(app)

# Khởi tạo Agent một lần duy nhất khi ứng dụng bắt đầu
agent = None

def init_agent():
    global agent
    if agent is not None:
        return agent

    load_dotenv()
    
    provider_name = os.getenv("DEFAULT_PROVIDER", "openai").strip().lower()
    
    # Định nghĩa tools (như trong run_agent.py)
    def check_stock(args):
        return "100"

    def get_discount(args):
        if "WINNER" in args:
            return "10%"
        return "0%"

    def calc_shipping(args):
        return "50000 VND"

    tools = [
        {
            "name": "check_stock",
            "description": "check_stock(item_name) -> Trả về số lượng hàng còn trong kho.",
            "func": check_stock
        },
        {
            "name": "get_discount",
            "description": "get_discount(coupon_code) -> Trả về phần trăm giảm giá của mã khuyến mãi.",
            "func": get_discount
        },
        {
            "name": "calc_shipping",
            "description": "calc_shipping(weight, destination) -> Tính phí ship dựa trên cân nặng và điểm đến.",
            "func": calc_shipping
        }
    ]

    try:
        if provider_name == "openai":
            from src.core.openai_provider import OpenAIProvider
            api_key = os.getenv("OPENAI_API_KEY")
            llm = OpenAIProvider(api_key=api_key)
        elif provider_name == "gemini":
            from src.core.gemini_provider import GeminiProvider
            api_key = os.getenv("GEMINI_API_KEY")
            llm = GeminiProvider(api_key=api_key)
        else:
            from src.core.local_provider import LocalProvider
            model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
            if not os.path.exists(model_path):
                raise Exception(f"Không tìm thấy model tại {model_path}")
            llm = LocalProvider(model_path=model_path)
            
        agent = ReActAgent(llm=llm, tools=tools, max_steps=5)
        print(f"✅ Agent đã sẵn sàng với provider: {provider_name}")
        return agent
    except Exception as e:
        print(f"❌ Lỗi khởi tạo Provider: {e}")
        return None

# API Endpoint để chat
@app.route('/api/chat', methods=['POST'])
def chat():
    global agent
    if agent is None:
        agent = init_agent()
    
    if agent is None:
        return jsonify({"error": "Failed to initialize agent"}), 500

    data = request.json
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Chúng ta sẽ thu thập log suy nghĩ của agent bằng cách redirect stdout (tùy chọn)
        # hoặc chỉ trả về kết quả cuối cùng.
        # Ở đây đơn giản trả về kết quả cuối cùng.
        result = agent.run(user_input)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route cho file static
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    init_agent()
    app.run(debug=True, host='0.0.0.0', port=5000)
