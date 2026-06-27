# ==================== فایل منوها (کیبوردها) بات سیناپس ====================
# این فایل فقط شامل کیبوردهای منو (ReplyKeyboard) و دکمه‌های اینلاین تایید است.
# متن سوالات و پیام‌ها در فایل‌های دیگر قرار دارند تا این فایل ساده و کوتاه بماند.

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# ==================== منوی اصلی ====================
main_menu = ReplyKeyboardMarkup([
    [KeyboardButton("🟢 بازار کار"), KeyboardButton("🔵 کسب‌وکار")],
    [KeyboardButton("🟣 مسئولیت اجتماعی"), KeyboardButton("🟠 مسیر رشد")],
    [KeyboardButton("🔴 لیدی لجستیک"), KeyboardButton("🌱 محصولات و خدمات سیناپس")],
    [KeyboardButton("📖 راهنمای انتخاب مسیر"), KeyboardButton("🆔 اطلاعات شخصی")],
    [KeyboardButton("🏢 اطلاعات کسب و کار"), KeyboardButton("📊 پرسشنامه تخصصی")],
    [KeyboardButton("💬 مشاوره هوشمند"), KeyboardButton("📞 ارتباط با پشتیبانی")],
    [KeyboardButton("💳 ارسال فیش پرداخت")]
], resize_keyboard=True)

# ==================== منوی بازار کار ====================
market_menu = ReplyKeyboardMarkup([
    [KeyboardButton("👤 کارجو"), KeyboardButton("💼 فریلنسر")],
    [KeyboardButton("🏢 کارفرما")],
    [KeyboardButton("🔙 بازگشت به منوی اصلی")]
], resize_keyboard=True)

# ==================== منوی کسب‌وکار (زیرتب‌های برند) ====================
business_menu = ReplyKeyboardMarkup([
    [KeyboardButton("🌟 برند شخصی"), KeyboardButton("🚀 برند محصولی")],
    [KeyboardButton("🏛️ برند سازمانی")],
    [KeyboardButton("🔙 بازگشت به منوی اصلی")]
], resize_keyboard=True)

# ==================== منوی مسئولیت اجتماعی ====================
social_menu = ReplyKeyboardMarkup([
    [KeyboardButton("❤️ نیک‌اندیش داخل ایران"), KeyboardButton("🌍 نیک‌اندیش خارج ایران")],
    [KeyboardButton("🤝 پروژه اجتماعی")],
    [KeyboardButton("🔙 بازگشت به منوی اصلی")]
], resize_keyboard=True)

# ==================== منوی مسیر رشد ====================
growth_menu = ReplyKeyboardMarkup([
    [KeyboardButton("🧠 توسعه فردی"), KeyboardButton("💼 توسعه شغلی")],
    [KeyboardButton("🤝 توسعه اثر اجتماعی")],
    [KeyboardButton("🔙 بازگشت به منوی اصلی")]
], resize_keyboard=True)

# ==================== منوی لیدی لجستیک ====================
logistics_menu = ReplyKeyboardMarkup([
    [KeyboardButton("💰 استعلام قیمت"), KeyboardButton("🌍 تأمین‌کننده خارجی")],
    [KeyboardButton("📦 حمل و اسناد"), KeyboardButton("📈 فروش و بازاریابی")],
    [KeyboardButton("🎓 آموزش واردات"), KeyboardButton("🧭 مشاوره تخصصی")],
    [KeyboardButton("🔙 بازگشت به منوی اصلی")]
], resize_keyboard=True)

# ==================== منوی بازگشت ====================
back_menu = ReplyKeyboardMarkup([
    [KeyboardButton("🔙 بازگشت به منوی اصلی")]
], resize_keyboard=True)

# ==================== کیبورد تایید اطلاعات ====================
def get_confirm_keyboard():
    """دکمه‌های تایید، ویرایش و انصراف برای فرم‌ها"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تایید و ثبت", callback_data="confirm")],
        [InlineKeyboardButton("✏️ ویرایش اطلاعات", callback_data="edit")],
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel")]
    ])