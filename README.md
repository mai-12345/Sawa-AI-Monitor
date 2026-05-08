
# AI Monitor Service - Sawa App 

## Overview 
هذه الخدمة مسؤولة عن تحليل رسائل الطلاب داخل تطبيق "سوا" لتحديد ما إذا كانت الرسالة مرتبطة بالمذاكرة (ملتزم) أو مجرد دردشة عامة (غير ملتزم). 

تم تصميم الكود بهندسة (3-Layer Architecture) لتقليل التكلفة وزيادة السرعة:
1. **Cache Layer:** لعدم تكرار الطلبات لنفس الرسالة.
2. **Local Regex Filter (Free):** لاصطياد الكلمات الواضحة جداً (مثل: مذاكرة، ماتش، فيلم) بدون استهلاك API.
3. **AI Fallback (Gemini API):** للتدخل في الرسائل المعقدة التي تحتاج لفهم سياق العامية المصرية.

---

## Setup & Installation 

1. **تثبيت المكتبات المطلوبة:**
   ```bash
   pip install -r requirements.txt
   
إعداد الـ API Key:
قم بإنشاء ملف .env في نفس المسار وضع فيه مفتاح Gemini الخاص بك:

Code snippet
GEMINI_API_KEY=your_actual_api_key_here


---

## How to Use 

يمكنك استدعاء الدالة الأساسية `check_context` في أي مكان داخل الكود الخاص بك:

```python
from ai_service import check_context

# Example 1: رسالة مذاكرة واضحة (ستمر من الفلتر المحلي ولن تستهلك API)
result1 = check_context("اي رايك نذاكر اول محاضره من اليوتيوب")
print(result1)

# Example 2: رسالة معقدة (ستذهب للـ AI)
result2 = check_context("انا حاسس اني متلخبط ومش عارف ابدأ منين")
print(result2)
Output Format (شكل الرد المرجوع)
الدالة تقوم دائماً بإرجاع Python Dictionary (JSON) يحتوي على 3 عناصر:

status: حالة الرسالة ("ملتزم" أو "غير ملتزم").

confidence: نسبة التأكد من النتيجة (من 0.0 إلى 1.0).

source: مصدر القرار لمعرفة هل استهلك API أم لا ("local" / "ai" / "cache").

مثال للرد:

JSON
{
  "status": "ملتزم",
  "confidence": 1.0,
  "source": "local"
}
Note to Developer :
قمت باستخدام Python Dictionary للـ In-Memory Caching لتسريع الردود المؤقتة. يُفضل في بيئة الإنتاج (Production) ربط هذا الجزء بـ Redis Cache لضمان الاحتفاظ بالبيانات حتى بعد عمل Restart للسيرفر.