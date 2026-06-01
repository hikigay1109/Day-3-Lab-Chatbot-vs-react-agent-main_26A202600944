import os
import sys
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

# Đảm bảo import được từ src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    load_dotenv()
    
    provider_name = os.getenv("DEFAULT_PROVIDER", "openai").strip().lower()
    
    try:
        if provider_name == "openai":
            from src.core.openai_provider import OpenAIProvider
            api_key = os.getenv("OPENAI_API_KEY")
            print("Đang khởi tạo OpenAI Provider (Baseline)...")
            llm = OpenAIProvider(api_key=api_key)
        elif provider_name == "gemini":
            from src.core.gemini_provider import GeminiProvider
            api_key = os.getenv("GEMINI_API_KEY")
            print("Đang khởi tạo Gemini Provider (Baseline)...")
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
    
    print("\n✅ Baseline LLM đã sẵn sàng! Gõ 'exit' hoặc 'quit' để thoát.")
    print("Mẹo: Hãy hỏi số lượng hàng hóa (check_stock) hoặc giá vận chuyển (calc_shipping) để xem nó ảo giác ra sao.")
    
    while True:
        try:
            user_input = input("\nBạn: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            print("\n--- Baseline LLM đang trả lời (Không có tools) ---")
            # Gọi LLM trực tiếp, không qua ReAct Agent
            result = llm.generate(prompt=user_input)
            
            print("\n--- Kết quả cuối cùng ---")
            print(result["content"])
            
            # (Tuỳ chọn) In ra số token và độ trễ nếu có
            if "latency_ms" in result:
                print(f"\n[Thời gian phản hồi: {result['latency_ms']:.2f}ms]")
                
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
