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

# ════════════════════════════════════════════════════════════════
# 💳 تنظیمات قیمت اشتراک — فقط همین خط‌ها را برای تغییر قیمت ویرایش کنید
# ════════════════════════════════════════════════════════════════
# نکته: عمداً عدد دقیق تومان اینجا گذاشته نشده. هر وقت قیمت نهایی را
# مشخص کردید، فقط مقدار رشته‌ی زیر را عوض کنید (مثلاً "350,000 تومان")
# و بات بدون هیچ تغییر دیگری از مقدار جدید استفاده می‌کند.
BRONZE_SUBSCRIPTION_PRICE = "قیمت متعاقباً اعلام می‌شود"   # 👈 اینجا قیمت برنزی را بنویسید
SILVER_SUBSCRIPTION_PRICE = "قیمت متعاقباً اعلام می‌شود"   # (سطح نقره‌ای - فعلاً غیرفعال)
GOLD_SUBSCRIPTION_PRICE = "قیمت متعاقباً اعلام می‌شود"     # (سطح طلایی - فعلاً غیرفعال)

# ==================== سطوح اشتراک ====================
# فقط سطح «برنزی» در حال حاضر فعال است (active=True). دو سطح دیگر
# به‌صورت کامل نوشته شده‌اند اما غیرفعال‌اند (active=False) تا هر وقت
# خواستید، فقط همین مقدار را True کنید و در منوها هم نمایش داده شوند.
# (در فایل menus_subscription.py به‌صورت خودکار فقط سطح‌های active نشان داده می‌شوند)
SUBSCRIPTION_TIERS = {
    "bronze": {
        "key": "bronze",
        "label": "🥉 اشتراک برنزی",
        "price": BRONZE_SUBSCRIPTION_PRICE,
        "duration_days": 30,
        "active": True,
        "perks": [
            "💬 دسترسی کامل به مشاوره هوشمند (هوش مصنوعی)",
            "📁 امکان ثبت درخواست پروژه",
            "🎨 دسترسی به طراحی بنر اختصاصی",
        ],
    },
    "silver": {
        "key": "silver",
        "label": "🥈 اشتراک نقره‌ای",
        "price": SILVER_SUBSCRIPTION_PRICE,
        "duration_days": 30,
        "active": False,  # 👈 بعداً برای فعال‌سازی این سطح، True کنید
        "perks": [
            "✨ همه‌ی امکانات سطح برنزی",
            "⚡ اولویت پاسخ‌گویی کارشناسان",
            # TODO: مزایای اختصاصی سطح نقره‌ای را اینجا اضافه کنید
        ],
    },
    "gold": {
        "key": "gold",
        "label": "🥇 اشتراک طلایی",
        "price": GOLD_SUBSCRIPTION_PRICE,
        "duration_days": 30,
        "active": False,  # 👈 بعداً برای فعال‌سازی این سطح، True کنید
        "perks": [
            "✨ همه‌ی امکانات سطح نقره‌ای",
            "👑 جلسه مشاوره اختصاصی ماهانه",
            # TODO: مزایای اختصاصی سطح طلایی را اینجا اضافه کنید
        ],
    },
}

def get_active_subscription_tiers():
    """فقط سطوح اشتراکی که active=True هستند را برمی‌گرداند (الان فقط برنزی)"""
    return {k: v for k, v in SUBSCRIPTION_TIERS.items() if v.get("active")}

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
# فایل جدید: وضعیت اشتراک هر کاربر (فعال/منقضی/در انتظار تایید)
SUBSCRIPTIONS_FILE = "subscriptions.json"
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

def save_telegram_identity(user_id, username=None, telegram_first_name=None):
    """
    ذخیره‌ی فوری آیدی تلگرام کاربر، به محض اولین تماس (مثلاً همان لحظه /start)،
    حتی اگر هنوز فرم اطلاعات شخصی را پر نکرده باشد. این تابع چیزی را
    اگر کاربر بعداً پر کند (مثل first_name واقعی) override نمی‌کند؛
    فقط مطمئن می‌شود رکورد پایه‌ی کاربر از همان ابتدا وجود دارد.
    """
    users = read_json(USERS_FILE, {})
    uid = str(user_id)
    if uid not in users:
        users[uid] = {}
    users[uid]["telegram_id"] = uid
    if username:
        users[uid]["telegram_username"] = f"@{username}"
    if telegram_first_name and not users[uid].get("first_name"):
        # فقط اگر هنوز نام واقعی ثبت نشده، نام نمایشی تلگرام را به‌عنوان مرجع اولیه نگه می‌داریم
        users[uid].setdefault("telegram_display_name", telegram_first_name)
    users[uid].setdefault("first_seen", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    write_json(USERS_FILE, users)
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

# ════════════════════════════════════════════════════════════════
# 💳 توابع مدیریت اشتراک (سیستم قفل امکانات هوش مصنوعی/پروژه/بنر)
# ════════════════════════════════════════════════════════════════
# ساختار هر رکورد در subscriptions.json:
# {
#   "status": "none" | "pending" | "active" | "expired" | "rejected",
#   "tier": "bronze" | "silver" | "gold" | None,
#   "requested_at": "...",      # زمانی که کاربر فیش را فرستاد
#   "approved_at": "...",       # زمانی که ادمین تایید کرد
#   "expires_at": "...",        # تاریخ انقضا (approved_at + duration_days)
#   "history": [ ... ]          # تاریخچه‌ی درخواست‌های قبلی
# }

def get_subscription(user_id):
    """دریافت وضعیت اشتراک یک کاربر (در صورت نبود، حالت پیش‌فرض 'none')"""
    subs = read_json(SUBSCRIPTIONS_FILE, {})
    return subs.get(str(user_id), {
        "status": "none", "tier": None,
        "requested_at": None, "approved_at": None, "expires_at": None,
        "history": []
    })

def _save_subscription(user_id, record):
    subs = read_json(SUBSCRIPTIONS_FILE, {})
    subs[str(user_id)] = record
    write_json(SUBSCRIPTIONS_FILE, subs)

def has_active_subscription(user_id):
    """
    بررسی می‌کند که آیا اشتراک کاربر فعال و معتبر است یا نه.
    اگر تاریخ انقضا گذشته باشد، خودکار وضعیت را 'expired' می‌کند.
    """
    record = get_subscription(user_id)
    if record["status"] != "active" or not record.get("expires_at"):
        return False

    expires_at = datetime.strptime(record["expires_at"], "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expires_at:
        # اشتراک منقضی شده - وضعیت را آپدیت کن
        record["status"] = "expired"
        _save_subscription(user_id, record)
        return False
    return True

def create_pending_subscription(user_id, tier_key):
    """
    وقتی کاربر فیش پرداخت اشتراک را ارسال می‌کند، این تابع وضعیت او را
    'pending' (در انتظار تایید ادمین) می‌کند.
    """
    record = get_subscription(user_id)
    record["status"] = "pending"
    record["tier"] = tier_key
    record["requested_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _save_subscription(user_id, record)
    logger.info(f"💳 درخواست اشتراک {tier_key} کاربر {user_id} در انتظار تایید ثبت شد")
    return record

def approve_subscription(user_id):
    """
    ادمین درخواست اشتراک کاربر را تایید می‌کند:
    تاریخ شروع = الان، تاریخ انقضا = الان + مدت سطح اشتراک (مثلاً ۳۰ روز).
    """
    from datetime import timedelta
    record = get_subscription(user_id)
    tier_key = record.get("tier") or "bronze"
    tier_info = SUBSCRIPTION_TIERS.get(tier_key, SUBSCRIPTION_TIERS["bronze"])
    duration = tier_info.get("duration_days", 30)

    now = datetime.now()
    expires = now + timedelta(days=duration)

    record["status"] = "active"
    record["approved_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
    record["expires_at"] = expires.strftime("%Y-%m-%d %H:%M:%S")
    record.setdefault("history", []).append({
        "tier": tier_key,
        "approved_at": record["approved_at"],
        "expires_at": record["expires_at"],
    })
    _save_subscription(user_id, record)
    logger.info(f"✅ اشتراک {tier_key} کاربر {user_id} تایید شد - معتبر تا {record['expires_at']}")
    return record

def reject_subscription(user_id):
    """ادمین درخواست اشتراک کاربر را رد می‌کند"""
    record = get_subscription(user_id)
    record["status"] = "rejected"
    _save_subscription(user_id, record)
    logger.info(f"❌ درخواست اشتراک کاربر {user_id} رد شد")
    return record

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