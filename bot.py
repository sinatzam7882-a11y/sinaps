# ==================== فایل اجرای اصلی بات سیناپس ====================
# این فایل نقطه شروع اجراست - فقط همین فایل را اجرا کنید: python bot.py
#
# ساختار فایل‌ها:
# ├── bot.py                       ← این فایل (نقطه اجرا)
# ├── config.py                    ← تنظیمات، اتصال Gemini، توابع JSON و State
# ├── menus.py                     ← فقط کیبوردهای منو
# ├── texts_profile.py             ← سوالات اطلاعات شخصی/کسب‌وکار/پرسشنامه/ارزیابی
# ├── texts_section_forms.py       ← سوالات تب کسب‌وکار، مسئولیت اجتماعی، مسیر رشد
# ├── texts_products_logistics.py  ← متن محصولات/خدمات سیناپس + فرم‌های لیدی لجستیک
# ├── handlers_core.py             ← عضویت کانال، start، callback، دریافت فیش
# ├── handlers_menu.py             ← پردازش پیام‌های متنی (منو و همه فرم‌ها)
# └── excel_and_admin.py           ← گزارش اکسل و دستورات ادمین

import traceback
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

# ایمپورت تنظیمات اصلی
from config import BOT_TOKEN, logger, CHANNEL_ID, ADMIN_ID

# ایمپورت هندلرها
from handlers_core import start, handle_callback, handle_photo
from handlers_menu import handle_menu

# ایمپورت دستورات ادمین
from excel_and_admin import (
    get_excel, get_data, show_summary, broadcast
)

# ==================== هندلر سراسری خطا ====================
async def error_handler(update, context):
    """مدیریت خطاهای پیش‌بینی نشده و اطلاع‌رسانی به کاربر"""
    logger.error(f"❌ خطای سراسری: {context.error}", exc_info=context.error)
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ خطایی رخ داد. لطفاً دوباره تلاش کنید یا /start را بزنید."
            )
        except Exception:
            pass

# ==================== ساخت و راه‌اندازی اپلیکیشن ====================
app = ApplicationBuilder().token(BOT_TOKEN).build()

# ثبت هندلر خطا
app.add_error_handler(error_handler)

# ثبت دستورات
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("getexcel", get_excel))
app.add_handler(CommandHandler("getdata", get_data))
app.add_handler(CommandHandler("summary", show_summary))
app.add_handler(CommandHandler("broadcast", broadcast))

# ثبت هندلر callback (دکمه‌های اینلاین)
app.add_handler(CallbackQueryHandler(handle_callback))

# ثبت هندلر تصویر (فیش پرداخت)
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# ثبت هندلر پیام متنی (منو و فرم‌ها)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

# ==================== اجرا ====================
print("🤖 بات سیناپس روشن شد...")
print(f"📢 کانال اجباری: {CHANNEL_ID}")
print(f"👑 ادمین: {ADMIN_ID}")
print("📁 اطلاعات در فایل‌های JSON ذخیره می‌شوند")
print("📊 دستور /getexcel برای دریافت فایل اکسل")
print("📤 دستور /broadcast [پیام] برای ارسال همگانی")
app.run_polling()