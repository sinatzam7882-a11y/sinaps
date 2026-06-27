# ==================== فایل تنظیمات اصلی بات سیناپس ====================
# این فایل شامل: متغیرهای محیطی، اتصال Gemini، توابع JSON و ذخیره‌سازی است
# نکته: این فایل تغییر ساختاری نسبت به قبل نداشته و فقط برای پشتیبانی از
# فرم‌های جدید (برند شخصی/محصولی/سازمانی، مسئولیت اجتماعی، مسیر رشد)
# یک فایل JSON و یک تابع ذخیره‌سازی جدید به آن اضافه شده است.

import os
import json
import logging
from datetime import datetime
from google import genai

# ==================== تنظیمات لاگینگ ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== متغیرهای محیطی ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8065571732"))
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@synapse_os")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN در متغیرهای محیطی تنظیم نشده است!")

logger.info(f"✅ ربات با موفقیت راه‌اندازی شد!")
logger.info(f"📢 کانال: {CHANNEL_ID}")
logger.info(f"👑 ادمین: {ADMIN_ID}")

# ==================== پرامپت سیستم برای هوش مصنوعی ====================
SYSTEM_PROMPT = (
    "تو یک مشاور کسب و کار حرفه‌ای هستی به نام مریم شهبازی. "
    "با لحنی گرم، دوستانه و حرفه‌ای پاسخ بده. "
    "همیشه به فارسی روان پاسخ بده. "
    "پاسخ‌هایت را کوتاه و مفید نگه دار."
)

# ==================== اتصال به Gemini ====================
try:
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("✅ Gemini متصل شد.")
    else:
        client = None
        logger.warning("⚠️ GEMINI_API_KEY تنظیم نشده.")
except Exception as e:
    logger.error(f"خطا در راه‌اندازی Gemini: {e}")
    client = None

# ==================== مسیر فایل‌های ذخیره‌سازی ====================
USERS_FILE = "users.json"
SURVEY_FILE = "survey.json"
ASSESSMENT_FILE = "assessment.json"
# فایل جدید: ذخیره پاسخ‌های فرم‌های برند شخصی/محصولی/سازمانی،
# مسئولیت اجتماعی و مسیر رشد (همه این فرم‌ها در اینجا ذخیره می‌شوند)
SECTION_FORMS_FILE = "section_forms.json"
EXCEL_FILE = "users_data.xlsx"

# ==================== اطلاعات پشتیبانی ====================
SUPPORT_INFO = {
    "phone": "09134525212",
    "email": "Shahbazimary1995@gmail.com",
    "telegram": "@malam_shahbazi",
    "hours": "تمام وقت",
    "response_time": "حداکثر تا 24 ساعت"
}

# ==================== توابع خواندن و نوشتن JSON ====================
def read_json(file_path, default={}):
    """خواندن فایل JSON - اگر فایل وجود نداشت مقدار پیش‌فرض برگرداند"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    return default

def write_json(file_path, data):
    """نوشتن داده در فایل JSON"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== توابع ذخیره و بازیابی اطلاعات ====================
def save_user_info(user_id, info):
    """ذخیره اطلاعات کاربر در فایل JSON"""
    users = read_json(USERS_FILE, {})
    if str(user_id) not in users:
        users[str(user_id)] = {}
    users[str(user_id)].update(info)
    users[str(user_id)]["telegram_id"] = str(user_id)
    users[str(user_id)]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_json(USERS_FILE, users)
    logger.info(f"✅ اطلاعات کاربر {user_id} ذخیره شد")
    return True

def save_assessment(user_id, answers):
    """ذخیره پاسخ‌های فرم ارزیابی در فایل JSON"""
    assessments = read_json(ASSESSMENT_FILE, {})
    if str(user_id) not in assessments:
        assessments[str(user_id)] = {}
    assessments[str(user_id)].update(answers)
    assessments[str(user_id)]["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_json(ASSESSMENT_FILE, assessments)
    logger.info(f"✅ فرم ارزیابی کاربر {user_id} ذخیره شد")
    return True

def save_survey_answer(user_id, section, answer):
    """ذخیره پاسخ پرسشنامه تخصصی در فایل JSON"""
    surveys = read_json(SURVEY_FILE, {})
    if str(user_id) not in surveys:
        surveys[str(user_id)] = {}
    surveys[str(user_id)][section] = answer
    surveys[str(user_id)]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    write_json(SURVEY_FILE, surveys)

def save_section_form(user_id, form_type, sub_title, qs, answers):
    """
    ذخیره پاسخ‌های فرم‌های بخش‌های مختلف (کسب‌وکار، مسئولیت اجتماعی، مسیر رشد) در JSON.
    هر بار که کاربر یکی از این فرم‌ها را کامل می‌کند، یک رکورد جدید
    به لیست فرم‌های همان کاربر اضافه می‌شود (چون ممکن است کاربر چند زیربخش
    مختلف را پر کند، مثلاً هم برند شخصی و هم توسعه شغلی).

    form_type: یکی از "business" / "social" / "growth"
    sub_title: عنوان زیربخش، مثلاً "🌟 برند شخصی"
    qs: لیست متن سوالات همان فرم
    answers: لیست پاسخ‌های کاربر (به همان ترتیب سوالات)
    """
    data = read_json(SECTION_FORMS_FILE, {})
    if str(user_id) not in data:
        data[str(user_id)] = []

    record = {
        "form_type": form_type,
        "sub_title": sub_title,
        "qa": [{"question": q, "answer": a} for q, a in zip(qs, answers)],
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data[str(user_id)].append(record)
    write_json(SECTION_FORMS_FILE, data)
    logger.info(f"✅ فرم «{sub_title}» کاربر {user_id} ذخیره شد")
    return True

def get_user_info(user_id):
    """دریافت اطلاعات یک کاربر خاص"""
    users = read_json(USERS_FILE, {})
    return users.get(str(user_id), {})

def is_user_registered(user_id):
    """بررسی اینکه آیا کاربر اطلاعات شخصی ثبت کرده یا نه"""
    users = read_json(USERS_FILE, {})
    user_data = users.get(str(user_id), {})
    return user_data.get("first_name") is not None and user_data.get("first_name") != ""

def is_business_registered(user_id):
    """بررسی اینکه آیا کاربر اطلاعات کسب‌وکار ثبت کرده یا نه"""
    users = read_json(USERS_FILE, {})
    user_data = users.get(str(user_id), {})
    return user_data.get("business_name") is not None and user_data.get("business_name") != ""

def has_completed_assessment(user_id):
    """بررسی اینکه آیا کاربر فرم ارزیابی را کامل پر کرده یا نه"""
    assessments = read_json(ASSESSMENT_FILE, {})
    return str(user_id) in assessments and len(assessments[str(user_id)]) > 5

# ==================== مدیریت وضعیت (State) کاربران ====================
user_states = {}

def get_user_state(user_id):
    """دریافت وضعیت فعلی کاربر (در کدام مرحله از فرم است)"""
    return user_states.get(user_id, {"section": None, "step": 0, "temp": {}})

def set_user_state(user_id, section, step=0, temp=None):
    """تنظیم وضعیت کاربر برای ردیابی مرحله فرم"""
    user_states[user_id] = {
        "section": section,
        "step": step,
        "temp": temp if temp else {}
    }

def clear_user_state(user_id):
    """پاک کردن وضعیت کاربر (وقتی فرم تمام یا لغو شد)"""
    if user_id in user_states:
        del user_states[user_id]