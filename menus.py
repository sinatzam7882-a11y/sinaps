# ==================== فایل منوها (کیبوردها) بات سیناپس ====================
# این فایل فقط شامل کیبوردهای منو (ReplyKeyboard) و دکمه‌های اینلاین تایید است.
# متن سوالات و پیام‌ها در فایل‌های دیگر قرار دارند تا این فایل ساده و کوتاه بماند.

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# ==================== منوی اصلی ====================
# توجه: طبق درخواست، فقط دکمه‌ی «محصولات و خدمات سیناپس» تک و تمام‌عرض
# (یعنی بزرگ‌تر از بقیه) است. تمام دکمه‌های دیگر دوتا-دوتا در یک ردیف
# قرار گرفته‌اند تا نسبت به آن کوچک‌تر و معمولی دیده شوند.
main_menu = ReplyKeyboardMarkup([
    [KeyboardButton("🌱 محصولات و خدمات سیناپس 🌱")],
    [KeyboardButton("💎 خرید اشتراک"), KeyboardButton("🔴 لیدی لجستیک")],
    [KeyboardButton("🟢 بازار کار"), KeyboardButton("🔵 کسب‌وکار")],
    [KeyboardButton("🟣 مسئولیت اجتماعی"), KeyboardButton("🟠 مسیر رشد")],
    [KeyboardButton("💬 مشاوره هوشمند"), KeyboardButton("📁 درخواست پروژه")],
    [KeyboardButton("🎨 طراحی بنر"), KeyboardButton("📖 راهنمای انتخاب مسیر")],
    [KeyboardButton("🆔 اطلاعات شخصی"), KeyboardButton("🏢 اطلاعات کسب و کار")],
    [KeyboardButton("📊 پرسشنامه تخصصی"), KeyboardButton("📞 ارتباط با پشتیبانی")],
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

# ==================== کیبورد انتخاب سطح اشتراک ====================
def get_subscription_tiers_keyboard(active_tiers):
    """
    یک دکمه‌ی اینلاین برای هر سطح اشتراک فعال می‌سازد (الان فقط برنزی).
    callback_data به شکل 'sub_select_bronze' است.
    """
    rows = []
    for tier in active_tiers.values():
        rows.append([InlineKeyboardButton(
            f"{tier['label']} — {tier['price']}",
            callback_data=f"sub_select_{tier['key']}"
        )])
    return InlineKeyboardMarkup(rows)

# ==================== کیبورد تایید/رد اشتراک برای ادمین ====================
def get_admin_subscription_keyboard(user_id):
    """دکمه‌های تایید/رد که زیر فیش پرداخت اشتراک برای ادمین ارسال می‌شود"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ تایید اشتراک", callback_data=f"sub_approve_{user_id}"),
            InlineKeyboardButton("❌ رد درخواست", callback_data=f"sub_reject_{user_id}"),
        ]
    ])

# ==================== کیبورد درخواست خودکار شماره تماس ====================
def get_phone_request_keyboard():
    """
    دکمه‌ی اشتراک‌گذاری خودکار شماره تماس تلگرام (Request Contact).
    کاربر می‌تواند به‌جای تایپ، با یک لمس شماره‌ی ثبت‌شده در تلگرامش را بفرستد.
    دکمه‌ی بازگشت هم کنارش هست تا اگر خواست تایپ دستی کند، راه برگشت داشته باشد.
    """
    return ReplyKeyboardMarkup([
        [KeyboardButton("📱 ارسال خودکار شماره تماس", request_contact=True)],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ], resize_keyboard=True)

# ==================== پنل پیشرفته‌ی ادمین (فقط برای ADMIN_ID نمایش داده می‌شود) ====================
def get_admin_panel_keyboard():
    """
    دکمه‌های شیشه‌ای پنل مدیریت: دریافت اکسل، آمار، سفارش‌های در انتظار،
    جستجوی کاربر و ارسال پیام همگانی - بدون نیاز به حفظ کردن دستورهای متنی.
    """
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 دریافت اکسل", callback_data="admin_panel_excel"),
            InlineKeyboardButton("📈 آمار کلی", callback_data="admin_panel_stats"),
        ],
        [
            InlineKeyboardButton("⏳ سفارش‌های در انتظار", callback_data="admin_panel_pending"),
            InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="admin_panel_find"),
        ],
        [
            InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="admin_panel_broadcast"),
        ],
    ])