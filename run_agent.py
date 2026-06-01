import os
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Đảm bảo import được từ src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent.agent import ReActAgent

# --- Định nghĩa một số Tools mẫu (Dựa theo Instructor Guide) ---
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

def main():
    load_dotenv()
    
    provider_name = os.getenv("DEFAULT_PROVIDER", "openai").strip().lower()
    
    try:
        if provider_name == "openai":
            from src.core.openai_provider import OpenAIProvider
            api_key = os.getenv("OPENAI_API_KEY")
            print("Đang khởi tạo OpenAI Provider...")
            llm = OpenAIProvider(api_key=api_key)
        elif provider_name == "gemini":
            from src.core.gemini_provider import GeminiProvider
            api_key = os.getenv("GEMINI_API_KEY")
            print("Đang khởi tạo Gemini Provider...")
            llm = GeminiProvider(api_key=api_key)
        else:
            from src.core.local_provider import LocalProvider
            model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
            if not os.path.exists(model_path):
                print(f"❌ Lỗi: Không tìm thấy model tại {model_path}")
                print("Vui lòng đảm bảo bạn đã tải model vào thư mục models/ theo hướng dẫn.")
                return
            print(f"Đang tải model từ {model_path} (có thể mất vài giây)...")
            llm = LocalProvider(model_path=model_path)
    except Exception as e:
        print(f"❌ Lỗi khởi tạo Provider: {e}")
        return
    
    # Khởi tạo Agent
    agent = ReActAgent(llm=llm, tools=tools, max_steps=5)
    
    print("\n✅ Agent đã sẵn sàng! Gõ 'exit' hoặc 'quit' để thoát.")
    
    while True:
        try:
            user_input = input("\nBạn: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            print("\n--- Agent đang suy nghĩ ---")
            result = agent.run(user_input)
            
            print("\n--- Kết quả cuối cùng ---")
            print(result)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
