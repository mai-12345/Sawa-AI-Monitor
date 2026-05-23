
import google.generativeai as genai
import time
import json
import os
import re
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# =========================
# Setup & Config

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


model = genai.GenerativeModel("gemini-2.5-flash")

# =========================
# CACHE (In-Memory)

cache = {}

# =========================
# LOCAL FILTER (Regex Powered)


study_keywords = r"\b(مذاكرة|كود|برمجة|مشروع|امتحان|محاضرة|شرح|دراسة|حل|assignment|شيت)\b"
noise_keywords = r"\b(ماتش|فيلم|أكل|خروجة|نلعب|مسلسل|تيك توك|ريلز|جيم)\b"

def local_filter(text: str) -> str:
    text_lower = text.lower()

    if re.search(study_keywords, text_lower):
        return "STUDY"

    if re.search(noise_keywords, text_lower):
        return "OFF_TOPIC"

    return "UNCERTAIN"

# =========================
# CLEAN JSON SAFE PARSE

def safe_json(response_text: str) -> dict:
    try:
        return json.loads(response_text)
    except Exception:
        return {"status": "غير ملتزم", "confidence": 0.0, "error": "json_parse_failed"}

# =========================
# AI CALL

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
def ai_check(text: str) -> dict:
    prompt = f"""
أنت AI Monitor داخل تطبيق "سوا" للمذاكرة لطلاب مصريين.
حدد إذا الرسالة:
- ملتزم (لها علاقة بالدراسة، الكلية، المذاكرة، أو التنظيم)
- غير ملتزم (دردشة عامة، هزار، خروجات)

Return ONLY JSON:
{{"status":"ملتزم","confidence":0.95}}

Message:
{text}
"""
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return safe_json(response.text)

# =========================
# MAIN LOGIC

def check_context(text: str) -> dict:
    """
    تحلل الرسالة لمعرفة ما إذا كانت مرتبطة بالدراسة أم لا.
    تستخدم فلتر محلي أولاً لتوفير استهلاك الـ API، ثم تلجأ للـ AI إذا لزم الأمر.
    """
    # 1. CACHE CHECK
    if text in cache:
        result = cache[text].copy()
        result["source"] = "cache" # لتوضيح أنها جاءت من الكاش
        return result

    # 2. LOCAL FILTER (FREE)
    local_result = local_filter(text)

    if local_result == "STUDY":
        output = {"status": "ملتزم", "confidence": 1.0, "source": "local"}
        cache[text] = output
        return output

    if local_result == "OFF_TOPIC":
        output = {"status": "غير ملتزم", "confidence": 1.0, "source": "local"}
        cache[text] = output
        return output

    # 3. AI FALLBACK (EXPENSIVE)
    ai_result = ai_check(text)
    ai_result["source"] = "ai"
    cache[text] = ai_result

    return ai_result

# =========================
# TEST

if __name__ == "__main__":
    texts = [
        "اي رايك نذاكر اول محاضره من اليوتيوب", # Local (STUDY)
        "شوفت الماتش امبارح؟", # Local (OFF_TOPIC)
        "انا حاسس اني متلخبط ومش عارف ابدأ منين", # AI (UNCERTAIN)
        "اي رايك نذاكر اول محاضره من اليوتيوب"  # Cache test
    ]

    print("--- START ---")
    for t in texts:
        print("=" * 50)
        print(f"Text: {t}")
        print(f"Result: {check_context(t)}")
        time.sleep(1)
    print("--- END ---")
