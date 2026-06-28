# ==================== پنل پیشرفته‌ی ادمین ====================
# این فایل شامل: نمایش پنل دکمه‌ای ادمین (بعد از /start) و پردازش کلیک
# روی هرکدام از دکمه‌های آن (اکسل، آمار، سفارش‌های در انتظار، جستجوی
# کاربر، ارسال پیام همگانی). جستجو و پیام‌همگانی چون نیاز به یک پیام
# متنی بعدی دارند، با تنظیم user_state ادمین و گرفتن همان پیام بعدی در
# handlers_menu.py تکمیل می‌شوند.

from datetime import datetime
from config import ADMIN_ID, logger, set_user_state
from menus import get_admin_panel_keyboard

ADMIN_PANEL_INTRO = (
    "🛠 پنل مدیریت سیناپس\n\n"
    "از دکمه‌های زیر برای دسترسی سریع به امکانات مدیریتی استفاده کنید 👇"
)

# ==================== نمایش پنل ادمین (صدا زده می‌شود از start) ====================
async def show_admin_panel(update, context):
    """پنل دکمه‌ای ادمین را نمایش می‌دهد - فقط برای ADMIN_ID صدا زده شود"""
    await update.message.reply_text(ADMIN_PANEL_INTRO, reply_markup=get_admin_panel_keyboard())

# ==================== دیسپچر کلیک روی دکمه‌های پنل ====================
async def handle_admin_panel_callback(update, context, data):
    """پردازش کلیک روی هرکدام از دکمه‌های پنل مدیریت (callback_data با پیشوند admin_panel_)"""
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ دسترسی ندارید.", show_alert=True)
        return

    # وارد کردن تابع‌ها داخل این تابع برای جلوگیری از import حلقوی بین فایل‌ها
    from excel_and_admin import (
        generate_excel_report, build_summary_text, build_pending_text,
    )

    if data == "admin_panel_excel":
        await query.message.reply_text("📊 در حال تولید فایل اکسل... لطفاً صبر کنید...")
        try:
            excel_file = generate_excel_report()
            with open(excel_file, 'rb') as f:
                await context.bot.send_document(
                    chat_id=ADMIN_ID,
                    document=f,
                    filename=f'users_data_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
                    caption="📊 گزارش کامل کاربران"
                )
        except Exception as e:
            await query.message.reply_text(f"⚠️ خطا در تولید فایل: {str(e)}")
        return

    if data == "admin_panel_stats":
        await query.message.reply_text(build_summary_text(), parse_mode='Markdown')
        return

    if data == "admin_panel_pending":
        await query.message.reply_text(build_pending_text(), parse_mode='Markdown')
        return

    if data == "admin_panel_find":
        set_user_state(ADMIN_ID, "admin_find_waiting", 0, {})
        await query.message.reply_text(
            "🔍 نام، نام خانوادگی، نام کسب‌وکار یا شماره تماس کاربر مدنظر را تایپ کنید:"
        )
        return

    if data == "admin_panel_broadcast":
        set_user_state(ADMIN_ID, "admin_broadcast_waiting", 0, {})
        await query.message.reply_text(
            "📢 متن پیامی که می‌خواهید برای همه‌ی کاربران ارسال شود را تایپ کنید:"
        )
        return