# ==================== هندلرهای اصلی (start / عضویت / callback / فیش) ====================
# این فایل شامل: بررسی عضویت در کانال، هندلر /start، هندلر دکمه‌های اینلاین
# (تایید/ویرایش/انصراف فرم‌ها و بررسی عضویت) و هندلر دریافت تصویر فیش پرداخت است.
# هندلر پیام‌های متنی منو/فرم‌ها در فایل handlers_menu.py قرار دارد.

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, BadRequest, Forbidden

from config import (
    CHANNEL_ID, ADMIN_ID, logger,
    get_user_state, set_user_state, clear_user_state,
    get_user_info, is_user_registered, save_user_info,
    save_telegram_identity,
)
from menus import main_menu, back_menu, get_confirm_keyboard
from texts_profile import personal_info_questions, business_info_questions

# ==================== بررسی عضویت کاربر در کانال ====================
async def is_member_of_channel(user_id, context):
    """بررسی اینکه کاربر در کانال اجباری عضو است یا نه"""
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )
        valid_statuses = ['member', 'administrator', 'creator']
        is_member = chat_member.status in valid_statuses
        logger.info(f"{'✅' if is_member else '❌'} کاربر {user_id} - وضعیت کانال: {chat_member.status}")
        return is_member

    except Forbidden as e:
        # بات ادمین کانال نیست - فرض می‌کنیم عضو است تا ربات کار کند
        logger.warning(f"⛔ بات به کانال دسترسی ندارد (کاربر {user_id}): {e}")
        return True

    except BadRequest as e:
        error_msg = str(e).lower()
        logger.error(f"❌ درخواست نامعتبر (کاربر {user_id}): {e}")
        if "user not found" in error_msg:
            return False
        if "chat not found" in error_msg:
            logger.error(f"⚠️ کانال {CHANNEL_ID} پیدا نشد! آیدی کانال را بررسی کنید.")
            return True
        return False

    except TelegramError as e:
        logger.error(f"⚠️ خطای تلگرام (کاربر {user_id}): {e}")
        return False

    except Exception as e:
        logger.error(f"⚠️ خطای ناشناخته در بررسی عضویت (کاربر {user_id}): {e}")
        return False

# ==================== ارسال پیام الزام به عضویت ====================
async def send_join_message(update: Update, context=None):
    """ارسال پیام درخواست عضویت در کانال با دکمه‌های اینلاین"""
    channel_url = f"https://t.me/{CHANNEL_ID.lstrip('@')}"
    join_button = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 عضویت در کانال", url=channel_url)],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_membership")]
    ])

    message = (
        "⚠️ برای استفاده از ربات، ابتدا باید در کانال ما عضو شوید!\n\n"
        "📢 لطفاً روی دکمه زیر کلیک کرده و در کانال عضو شوید.\n\n"
        f"🆔 آیدی کانال: {CHANNEL_ID}\n\n"
        "✅ بعد از عضویت، روی دکمه «بررسی عضویت» کلیک کنید.\n\n"
        "💡 نکته: اگر قبلاً عضو شده‌اید، روی دکمه بررسی عضویت کلیک کنید تا دوباره چک شود."
    )

    if update.message:
        await update.message.reply_text(message, reply_markup=join_button, disable_web_page_preview=True)
    elif update.callback_query:
        await update.callback_query.message.reply_text(message, reply_markup=join_button, disable_web_page_preview=True)

# ==================== متن خوش‌آمدگویی منوی اصلی ====================
def get_welcome_text(user_id, returning):
    """ساخت متن خوش‌آمدگویی - یک متن ثابت برای همه کاربران"""
    return (
        "سلام سلام شهبازی هستم، مریم 😍🌱\n\n"
        "به سیناپس خوش اومدی. 🌱😍\n"
        "هر آدمی در یکی از این مسیرها به دنبال رشد و توسعه برای ساختن یک ورژن بهتر از خودشه. "
        "تو از کجا میخوای شروع کنی؟\n\n"
        "🟢 بازار کار\n🔵 کسب‌وکار\n🟣 مسئولیت اجتماعی\n🟠 مسیر رشد\n"
        "🔴 لیدی لجستیک\n🌱 محصولات و خدمات سیناپس\n\n"
        "لطفاً مسیر موردنظرت را انتخاب کن. 👇"
    )

# ==================== نوتیفیکیشن به ادمین ====================
async def notify_admin(context, user_id, info, section_type="personal"):
    """ارسال اطلاعات ثبت‌شده کاربر به ادمین"""
    try:
        if section_type == "personal":
            message = f"🆕 **کاربر جدید ثبت‌نام کرد!**\n\n"
            message += f"🆔 آیدی تلگرام: `{user_id}`\n"
            message += f"👤 نام: {info.get('first_name', '')} {info.get('last_name', '')}\n"
            message += f"🏙️ شهر: {info.get('city', '')}\n"
            message += f"📞 شماره: {info.get('phone', '')}"
        elif section_type == "assessment":
            message = f"📋 **فرم ارزیابی جدید!**\n\n"
            message += f"🆔 آیدی تلگرام: `{user_id}`\n"
            message += f"👤 نام: {info.get('full_name', '')}\n"
            message += f"📞 شماره: {info.get('phone', '')}\n"
            message += f"🎂 سن: {info.get('age', '')}\n"
            message += f"📍 مکان: {info.get('location', '')}\n"
            message += f"💼 نقش: {info.get('role', '')}\n"
            message += f"📊 حوزه: {info.get('field', '')}"
        else:
            message = f"🏢 اطلاعات کسب و کار جدید!\n\n"
            message += f"🆔 آیدی تلگرام: {user_id}\n"
            message += f"👤 نام: {info.get('full_name', '')}\n"
            message += f"🏢 نام کسب و کار: {info.get('business_name', '')}\n"
            message += f"💼 حیطه فعالیت: {info.get('field', '')}\n"
            message += f"📞 شماره تماس: {info.get('phone', '')}\n"
            message += f"📱 شبکه اجتماعی: {info.get('social', '')}"

        await context.bot.send_message(chat_id=ADMIN_ID, text=message, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"خطا در ارسال نوتیفیکیشن: {e}")

# ==================== تابع نمایش خلاصه اطلاعات ====================
def get_info_summary(info, section_type):
    """نمایش خلاصه اطلاعات وارد شده قبل از تایید نهایی"""
    if section_type == "personal":
        return f"""📝 **خلاصه اطلاعات شخصی شما:**

👤 نام: {info.get('first_name', '❌')}
👨‍👩‍👧 نام خانوادگی: {info.get('last_name', '❌')}
📅 تاریخ تولد: {info.get('birth_date', '❌')}
📞 شماره تماس: {info.get('phone', '❌')}
🏙️ شهر: {info.get('city', '❌')}

آیا اطلاعات صحیح است؟"""

    elif section_type == "business":
        return (
            f"🏢 خلاصه اطلاعات کسب و کار شما:\n\n"
            f"👤 نام: {info.get('full_name', '❌')}\n"
            f"🏢 نام کسب و کار: {info.get('business_name', '❌')}\n"
            f"💼 حیطه فعالیت: {info.get('field', '❌')}\n"
            f"📞 شماره تماس: {info.get('phone', '❌')}\n"
            f"📱 شبکه اجتماعی: {info.get('social', '❌')}\n\n"
            f"آیا اطلاعات صحیح است؟"
        )

    return ""

# ==================== هندلر دستور /start ====================
async def start(update: Update, context):
    """هندلر اصلی شروع بات - بررسی عضویت و نمایش خوش‌آمدگویی"""
    user_id = update.effective_user.id
    logger.info(f"📩 دستور /start از کاربر {user_id}")

    # 💾 ذخیره‌ی فوری آیدی/یوزرنیم تلگرام کاربر، حتی اگر هنوز ثبت‌نام نکرده باشد
    save_telegram_identity(
        user_id,
        username=update.effective_user.username,
        telegram_first_name=update.effective_user.first_name,
    )

    try:
        is_member = await is_member_of_channel(user_id, context)
        if not is_member:
            await send_join_message(update, context)
            return

        logger.info(f"✅ کاربر {user_id} وارد شد - عضو کانال")
        welcome_msg = get_welcome_text(user_id, returning=is_user_registered(user_id))

        try:
            with open('images/welcome.jpg', 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption=welcome_msg, reply_markup=main_menu)
        except Exception:
            await update.message.reply_text(welcome_msg, reply_markup=main_menu)

    except Exception as e:
        logger.error(f"❌ خطا در هندلر start برای کاربر {user_id}: {e}", exc_info=True)
        try:
            await update.message.reply_text("⚠️ خطایی رخ داد. لطفاً دوباره /start را بزنید.", reply_markup=main_menu)
        except Exception:
            pass

# ==================== هندلر دکمه‌های اینلاین (callback) ====================
async def handle_callback(update, context):
    """پردازش دکمه‌های اینلاین: بررسی عضویت، ویرایش، تایید، انصراف، اشتراک"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # ===== انتخاب سطح اشتراک (sub_select_bronze / sub_select_silver / ...) =====
    if data.startswith("sub_select_"):
        from handlers_subscription import handle_subscription_tier_selection
        tier_key = data.replace("sub_select_", "")
        await handle_subscription_tier_selection(update, context, tier_key)
        return

    # ===== دکمه‌ی «خرید/تمدید اشتراک» که زیر پیام انقضا نشان داده می‌شود =====
    if data == "open_subscription_menu":
        from handlers_subscription import show_subscription_plans_from_callback
        await show_subscription_plans_from_callback(update, context)
        return

    # ===== تایید اشتراک توسط ادمین (sub_approve_<user_id>) =====
    if data.startswith("sub_approve_"):
        from handlers_subscription import handle_admin_approve_subscription
        target_user_id = data.replace("sub_approve_", "")
        await handle_admin_approve_subscription(update, context, target_user_id)
        return

    # ===== رد اشتراک توسط ادمین (sub_reject_<user_id>) =====
    if data.startswith("sub_reject_"):
        from handlers_subscription import handle_admin_reject_subscription
        target_user_id = data.replace("sub_reject_", "")
        await handle_admin_reject_subscription(update, context, target_user_id)
        return

    # ===== بررسی عضویت پس از کلیک روی دکمه =====
    if data == "check_membership":
        is_member = await is_member_of_channel(user_id, context)

        if is_member:
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except Exception:
                pass

            welcome_msg = get_welcome_text(user_id, returning=is_user_registered(user_id))

            try:
                with open('images/welcome.jpg', 'rb') as photo:
                    await query.message.reply_photo(photo=photo, caption=welcome_msg, reply_markup=main_menu)
            except Exception:
                await query.message.reply_text(welcome_msg, reply_markup=main_menu)

        else:
            channel_url = f"https://t.me/{CHANNEL_ID.lstrip('@')}"
            join_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 عضویت در کانال", url=channel_url)],
                [InlineKeyboardButton("🔄 بررسی مجدد", callback_data="check_membership")]
            ])
            try:
                await query.edit_message_text(
                    f"❌ هنوز عضو کانال نشده‌اید!\n\n"
                    f"📢 لطفاً ابتدا در کانال {CHANNEL_ID} عضو شوید.\n"
                    f"✅ سپس روی دکمه «بررسی مجدد» کلیک کنید.",
                    reply_markup=join_button
                )
            except Exception:
                await query.message.reply_text(
                    f"❌ هنوز عضو کانال نشده‌اید!\n\n"
                    f"📢 لطفاً ابتدا در کانال {CHANNEL_ID} عضو شوید.\n"
                    f"✅ سپس روی دکمه «بررسی مجدد» کلیک کنید.",
                    reply_markup=join_button
                )
        return

    # ===== ویرایش اطلاعات شخصی =====
    if data == "edit_personal":
        clear_user_state(user_id)
        set_user_state(user_id, "personal", 0, {})
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await query.message.reply_text(
            f"✏️ ویرایش اطلاعات شخصی\n\n{personal_info_questions[0][1]}",
            reply_markup=back_menu
        )
        return

    # ===== پردازش تایید / ویرایش / انصراف فرم‌ها =====
    state = get_user_state(user_id)
    temp = state.get("temp", {})
    section = state.get("section", "")

    logger.info(f"کاربر {user_id} روی دکمه {data} کلیک کرد - بخش: {section}")

    if data == "confirm":
        try:
            if section == "personal_confirm":
                # ذخیره اطلاعات شخصی
                save_user_info(user_id, temp)
                await notify_admin(context, user_id, temp, "personal")
                first_name = temp.get('first_name', '')
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text(
                    f"✅ {first_name} عزیز، ثبت‌نام شما با موفقیت انجام شد! 🎉\n\n"
                    f"👤 نام: {first_name} {temp.get('last_name', '')}\n"
                    f"🏙️ شهر: {temp.get('city', '')}\n"
                    f"📞 شماره تماس: {temp.get('phone', '')}\n\n"
                    f"به سیناپس خوش اومدی! 🌱😍\n"
                    f"از منوی زیر مسیر موردنظرت را انتخاب کن 👇",
                    reply_markup=main_menu
                )
                clear_user_state(user_id)
                return

            elif section == "business_confirm":
                # ذخیره اطلاعات کسب و کار
                user_info = get_user_info(user_id)
                temp.update(user_info)
                save_user_info(user_id, temp)
                await notify_admin(context, user_id, temp, "business")
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text(
                    f"✅ **اطلاعات کسب و کار شما ثبت شد!** 🏢\n\n"
                    f"🏢 نام کسب و کار: {temp.get('business_name', '')}\n"
                    f"💼 حیطه فعالیت: {temp.get('field', '')}\n"
                    f"📞 شماره تماس: {temp.get('phone', '')}\n"
                    f"📱 شبکه اجتماعی: {temp.get('social', '')}\n\n"
                    f"📌 حالا می‌توانید:\n"
                    f"• پرسشنامه تخصصی را پر کنید\n"
                    f"• از مشاوره هوشمند استفاده کنید\n\n"
                    f"به منوی اصلی بازگشتید 👇",
                    reply_markup=main_menu,
                    parse_mode='Markdown'
                )
                clear_user_state(user_id)
                return

            else:
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text("⚠️ خطا در ثبت اطلاعات. لطفاً دوباره تلاش کنید.", reply_markup=main_menu)
                clear_user_state(user_id)
                return

        except Exception as e:
            logger.error(f"خطا در تایید: {e}")
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text(
                f"⚠️ خطا در ثبت اطلاعات: {str(e)}\n\nلطفاً دوباره تلاش کنید.",
                reply_markup=main_menu
            )
            clear_user_state(user_id)

    elif data == "edit":
        # بازگشت به شروع فرم برای ویرایش
        if section == "personal_confirm":
            new_section = "personal"
            questions = personal_info_questions
            title = "✏️ ویرایش اطلاعات شخصی"
        elif section == "business_confirm":
            new_section = "business"
            questions = business_info_questions
            title = "✏️ ویرایش اطلاعات کسب و کار"
        else:
            await query.edit_message_text("⚠️ خطا در ویرایش. لطفاً دوباره تلاش کنید.", reply_markup=main_menu)
            clear_user_state(user_id)
            return

        await query.edit_message_reply_markup(reply_markup=None)
        set_user_state(user_id, new_section, 0, {})
        await query.message.reply_text(f"{title}\n\n{questions[0][1]}", reply_markup=back_menu, parse_mode='Markdown')

    elif data == "cancel":
        # لغو فرم
        clear_user_state(user_id)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "❌ **ثبت‌نامه لغو شد.**\n\n"
            "اطلاعات شما ذخیره نشد.\n"
            "در صورت تمایل می‌توانید دوباره ثبت‌نام کنید.\n\n"
            "به منوی اصلی بازگشتید 👇",
            reply_markup=main_menu,
            parse_mode='Markdown'
        )

# ==================== هندلر دریافت تصویر فیش پرداخت ====================
async def handle_photo(update: Update, context):
    """
    دریافت تصویر فیش پرداخت از کاربر.
    دو حالت ممکن است:
      1) waiting_receipt              → فیش هزینه‌ی گزارش (۲۵۰هزارتومانی فرم‌ها) - مثل قبل
      2) waiting_subscription_receipt → فیش خرید/تمدید اشتراک - به ادمین با دکمه‌ی تایید/رد می‌رود
    """
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    section = state.get("section")

    if section == "waiting_subscription_receipt":
        from handlers_subscription import process_subscription_receipt
        tier_key = state.get("temp", {}).get("tier", "bronze")
        await process_subscription_receipt(update, context, user_id, tier_key)
        return

    if section == "waiting_receipt":
        user_info = get_user_info(user_id)
        first_name = user_info.get('first_name', 'کاربر')
        caption = (
            f"💳 فیش پرداخت جدید\n"
            f"👤 {first_name} {user_info.get('last_name', '')}\n"
            f"🆔 {user_id}\n"
            f"📱 {user_info.get('phone', 'ثبت نشده')}\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        try:
            photo = update.message.photo[-1]
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id, caption=caption)
            clear_user_state(user_id)
            await update.message.reply_text(
                f"✅ {first_name} عزیز، فیش پرداخت شما دریافت شد.\n\n"
                "🔍 بررسی شروع می‌شود و گزارش شناخت حداکثر ظرف ۲۴ ساعت ارسال خواهد شد. 🌱",
                reply_markup=main_menu
            )
        except Exception as e:
            logger.error(f"خطا در ارسال فیش: {e}")
            await update.message.reply_text("⚠️ خطا در دریافت تصویر. لطفاً دوباره ارسال کنید.", reply_markup=back_menu)
    else:
        await update.message.reply_text(
            "📸 برای ارسال فیش پرداخت از دکمه «💳 ارسال فیش پرداخت» در منوی اصلی استفاده کنید.",
            reply_markup=main_menu
        )

# ==================== هندلر دریافت شماره تماس خودکار (دکمه Request Contact) ====================
async def handle_contact(update: Update, context):
    """
    وقتی کاربر با دکمه‌ی «📱 ارسال خودکار شماره تماس» شماره‌اش را می‌فرستد،
    تلگرام یک پیام از نوع contact ارسال می‌کند (نه متن معمولی).
    این هندلر شماره را می‌گیرد و دقیقاً مثل اینکه کاربر آن را تایپ کرده باشد
    وارد همان مرحله‌ی فعلی فرم (هرکدام که باشد: شخصی/کسب‌وکار/ارزیابی/پروژه) می‌کند.
    """
    from handlers_menu import handle_menu_text_value
    user_id = update.effective_user.id
    contact = update.message.contact

    if not contact:
        return

    phone_number = contact.phone_number
    if not phone_number.startswith("+") and not phone_number.startswith("0"):
        phone_number = f"+{phone_number}"

    # اگر شماره مال خود کاربر بود (نه یک شخص دیگری که فوروارد کرده)، آیدی تلگرامش را هم ثبت کن
    if contact.user_id and contact.user_id == user_id:
        save_telegram_identity(user_id)

    await handle_menu_text_value(update, context, phone_number)