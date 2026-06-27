# ==================== فایل هندلرهای اصلی بات سیناپس ====================
# این فایل شامل: بررسی عضویت، هندلر start، پردازش منو، callback و هندلر فیش است

from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, BadRequest, Forbidden

from config import (
    CHANNEL_ID, ADMIN_ID, SYSTEM_PROMPT, client,
    logger, get_user_state, set_user_state, clear_user_state,
    get_user_info, is_user_registered, save_user_info,
    save_assessment, save_survey_answer, read_json,
    USERS_FILE, ASSESSMENT_FILE
)
from menus_and_questions import (
    main_menu, market_menu, business_menu, social_menu,
    growth_menu, logistics_menu, back_menu, get_confirm_keyboard,
    personal_info_questions, business_info_questions,
    survey_questions, assessment_questions,
    BUSINESS_QUESTIONS, SOCIAL_QUESTIONS, GROWTH_QUESTIONS,
    SOCIAL_END_MSG, GROWTH_END_MSG, BUSINESS_END_MSG,
    SYNAPSE_PRODUCTS_MSG, LOGISTICS_FORMS
)
from config import SUPPORT_INFO

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

    try:
        is_member = await is_member_of_channel(user_id, context)
        if not is_member:
            await send_join_message(update, context)
            return

        user_info = get_user_info(user_id)
        logger.info(f"✅ کاربر {user_id} وارد شد - عضو کانال")

        if is_user_registered(user_id):
            welcome_msg = (
                f"✨ خوش برگشتی {user_info.get('first_name', '')} عزیز!\n\n"
                "به سیناپس خوش اومدی. 🌱😍\n"
                "هر آدمی در یکی از این مسیرها به دنبال رشد و توسعه برای ساختن یک ورژن بهتر از خودشه. "
                "تو از کجا میخوای شروع کنی؟\n\n"
                "🟢 بازار کار\n🔵 کسب‌وکار\n🟣 مسئولیت اجتماعی\n🟠 مسیر رشد\n"
                "🔴 لیدی لجستیک\n🌱 محصولات سیناپس\n\n"
                "لطفاً مسیر موردنظرت را انتخاب کن. 👇"
            )
        else:
            welcome_msg = (
                "سلام سلام\n"
                "شهبازی هستم، مریم 😍🌱\n"
                "اینجا قراره هویت کسب و کار و برند خودتون رو بسازید و روز به روز فروش بیشتری رو تجربه کنین.\n"
                "با من همراه باش\n\n"
                "به سیناپس خوش اومدی. 🌱😍\n"
                "هر آدمی در یکی از این مسیرها به دنبال رشد و توسعه برای ساختن یک ورژن بهتر از خودشه. "
                "تو از کجا میخوای شروع کنی؟\n\n"
                "🟢 بازار کار\n🔵 کسب‌وکار\n🟣 مسئولیت اجتماعی\n🟠 مسیر رشد\n"
                "🔴 لیدی لجستیک\n🌱 محصولات سیناپس\n\n"
                "لطفاً مسیر موردنظرت را انتخاب کن. 👇"
            )

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

# ==================== هندلر اصلی پردازش پیام‌های متنی ====================
async def handle_menu(update: Update, context):
    """پردازش تمام پیام‌های متنی کاربر - منو، فرم‌ها و مشاوره هوشمند"""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # بررسی عضویت قبل از هر اقدامی
    if not await is_member_of_channel(user_id, context):
        await send_join_message(update, context)
        return

    state = get_user_state(user_id)
    section = state.get("section")
    step = state.get("step", 0)
    temp = state.get("temp", {})

    # ===== بازگشت به منوی اصلی =====
    if text == "🔙 بازگشت به منوی اصلی":
        clear_user_state(user_id)
        await update.message.reply_text("🔹 به منوی اصلی بازگشتید 👇", reply_markup=main_menu)
        return

    # ===== منوهای اصلی - نمایش زیرمنو =====
    menus = {
        "🟢 بازار کار": market_menu,
        "🔵 کسب‌وکار": business_menu,
        "🟣 مسئولیت اجتماعی": social_menu,
        "🟠 مسیر رشد": growth_menu,
        "🔴 لیدی لجستیک": logistics_menu,
    }
    if text in menus:
        await update.message.reply_text(f"{text}\n\nلطفاً یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=menus[text])
        return

    # ===== فرم‌های لیدی لجستیک =====
    if text in LOGISTICS_FORMS:
        set_user_state(user_id, "logistics_waiting", 0, {"service": text})
        await update.message.reply_text(LOGISTICS_FORMS[text], reply_markup=back_menu)
        await update.message.reply_text("📝 لطفاً اطلاعات خواسته شده را در یک پیام ارسال کنید:", reply_markup=back_menu)
        return

    # ===== دریافت پاسخ فرم لجستیک و ارسال به ادمین =====
    if section == "logistics_waiting":
        service = temp.get("service", "درخواست")
        user_info = get_user_info(user_id)
        first_name = user_info.get("first_name", "کاربر")
        admin_msg = (
            f"📋 درخواست جدید - {service}\n"
            f"👤 {first_name} {user_info.get('last_name', '')}\n"
            f"🆔 {user_id}\n"
            f"📱 {user_info.get('phone', '')}\n\n"
            f"💬 اطلاعات:\n{text}"
        )
        try:
            await context.bot.send_message(ADMIN_ID, admin_msg)
        except Exception:
            pass
        clear_user_state(user_id)
        await update.message.reply_text(
            "🌱 درخواست شما با موفقیت ثبت شد.\n\n"
            "اطلاعات ارسال‌شده توسط کارشناسان لیدی لجستیک بررسی می‌شود و در اولین فرصت "
            "برای هماهنگی و ارائه راهکار با شما تماس خواهیم گرفت.\n\n"
            "⏰ زمان پاسخگویی: حداکثر ۲ ساعت کاری.",
            reply_markup=main_menu
        )
        return

    # ===== محصولات / خدمات سیناپس =====
    if text == "🌱 محصولات سیناپس":
        await update.message.reply_text(SYNAPSE_PRODUCTS_MSG, reply_markup=main_menu)
        return

    # ===== شروع فرم کسب‌وکار (برند شخصی/محصولی/سازمانی) =====
    if text in BUSINESS_QUESTIONS:
        data = BUSINESS_QUESTIONS[text]
        set_user_state(user_id, "section_form", 0, {
            "form_type": "business",
            "sub": text,
            "intro": data["intro"],
            "qs": data["qs"],
            "end_msg": BUSINESS_END_MSG,
        })
        await update.message.reply_text(f"{data['intro']}\n\n{data['qs'][0]}", reply_markup=back_menu)
        return

    # ===== شروع فرم مسئولیت اجتماعی =====
    if text in SOCIAL_QUESTIONS:
        data = SOCIAL_QUESTIONS[text]
        set_user_state(user_id, "section_form", 0, {
            "form_type": "social",
            "sub": text,
            "intro": data["intro"],
            "qs": data["qs"],
            "end_msg": SOCIAL_END_MSG,
        })
        await update.message.reply_text(f"{data['intro']}\n\n{data['qs'][0]}", reply_markup=back_menu)
        return

    # ===== شروع فرم مسیر رشد =====
    if text in GROWTH_QUESTIONS:
        data = GROWTH_QUESTIONS[text]
        set_user_state(user_id, "section_form", 0, {
            "form_type": "growth",
            "sub": text,
            "intro": data["intro"],
            "qs": data["qs"],
            "end_msg": GROWTH_END_MSG,
        })
        await update.message.reply_text(f"{data['intro']}\n\n{data['qs'][0]}", reply_markup=back_menu)
        return

    # ===== پردازش پاسخ‌های فرم‌های section_form (کسب‌وکار، مسئولیت، مسیر رشد) =====
    if section == "section_form":
        qs = temp.get("qs", [])
        answers = temp.get("answers", [])
        answers.append(text)
        temp["answers"] = answers

        if step + 1 < len(qs):
            # سوال بعدی را نمایش بده
            set_user_state(user_id, "section_form", step + 1, temp)
            await update.message.reply_text(qs[step + 1], reply_markup=back_menu)
        else:
            # فرم تکمیل شد - ذخیره و ارسال به ادمین
            user_info = get_user_info(user_id)
            first_name = user_info.get("first_name", "کاربر")
            sub = temp.get("sub", "")
            end_msg = temp.get("end_msg", "")
            admin_msg = (
                f"📋 فرم جدید — {sub}\n"
                f"👤 {first_name} {user_info.get('last_name', '')}\n"
                f"🆔 {user_id} | 📱 {user_info.get('phone', '')}\n\n"
            )
            for i, (q, a) in enumerate(zip(qs, answers), 1):
                admin_msg += f"❓ {q[:60]}\n💬 {a}\n\n"
            try:
                await context.bot.send_message(ADMIN_ID, admin_msg[:4000])
            except Exception:
                pass
            clear_user_state(user_id)
            await update.message.reply_text(end_msg, reply_markup=main_menu)
        return

    # ===== راهنمای انتخاب مسیر =====
    if text == "📖 راهنمای انتخاب مسیر":
        await update.message.reply_text(
            "📖 راهنمای انتخاب مسیر\n\n"
            "🟢 بازار کار — دنبال شغل، پروژه یا جذب نیرو هستی\n"
            "🔵 کسب‌وکار — می‌خواهی کسب‌وکارت را رشد بدهی\n"
            "🟣 مسئولیت اجتماعی — اثر مثبت اجتماعی می‌خواهی\n"
            "🟠 مسیر رشد — به دنبال خودشناسی و مسیر زندگی هستی\n"
            "🔴 لیدی لجستیک — خدمات واردات و صادرات\n"
            "🌱 محصولات سیناپس — ابزارها و دوره‌های آموزشی\n\n"
            "مسیر موردنظرت را انتخاب کن 👇",
            reply_markup=main_menu
        )
        return

    # ===== اطلاعات شخصی =====
    if text == "🆔 اطلاعات شخصی":
        if is_user_registered(user_id):
            user_info = get_user_info(user_id)
            first_name = user_info.get("first_name", "")
            edit_kb = InlineKeyboardMarkup([[InlineKeyboardButton("✏️ ویرایش اطلاعات", callback_data="edit_personal")]])
            await update.message.reply_text(
                f"سلام {first_name} عزیز! 👋\n\n"
                f"✅ اطلاعات شما قبلاً ثبت شده:\n"
                f"👤 {first_name} {user_info.get('last_name', '')}\n"
                f"🏙️ {user_info.get('city', '')}\n"
                f"📞 {user_info.get('phone', '')}\n\n"
                f"برای ویرایش روی دکمه کلیک کنید 👇",
                reply_markup=edit_kb
            )
            return
        clear_user_state(user_id)
        set_user_state(user_id, "personal", 0, {})
        await update.message.reply_text(f"📝 ثبت اطلاعات شخصی\n\n{personal_info_questions[0][1]}", reply_markup=back_menu)
        return

    # ===== اطلاعات کسب و کار =====
    if text == "🏢 اطلاعات کسب و کار":
        if not is_user_registered(user_id):
            await update.message.reply_text("⚠️ ابتدا اطلاعات شخصی را ثبت کنید.", reply_markup=main_menu)
            return
        clear_user_state(user_id)
        set_user_state(user_id, "business", 0, {})
        await update.message.reply_text(f"🏢 ثبت اطلاعات کسب و کار\n\n{business_info_questions[0][1]}", reply_markup=back_menu)
        return

    # ===== پرسشنامه تخصصی =====
    if text == "📊 پرسشنامه تخصصی":
        if not is_user_registered(user_id):
            await update.message.reply_text("⚠️ ابتدا اطلاعات شخصی را ثبت کنید.", reply_markup=main_menu)
            return
        clear_user_state(user_id)
        set_user_state(user_id, "survey", 0, {})
        await update.message.reply_text(f"📋 پرسشنامه تخصصی\n\n{survey_questions[0][1]}", reply_markup=back_menu)
        return

    # ===== مشاوره هوشمند =====
    if text == "💬 مشاوره هوشمند":
        if not is_user_registered(user_id):
            await update.message.reply_text("⚠️ ابتدا اطلاعات شخصی را ثبت کنید.", reply_markup=main_menu)
            return
        await update.message.reply_text(
            "💬 مشاوره هوشمند\n\nهر سوالی درباره برندسازی، بازاریابی، فروش و... داری بپرس 👇",
            reply_markup=back_menu
        )
        return

    # ===== ارسال فیش پرداخت =====
    if text == "💳 ارسال فیش پرداخت":
        clear_user_state(user_id)
        set_user_state(user_id, "waiting_receipt", 0, {})
        await update.message.reply_text(
            "💳 پنل ارسال فیش پرداخت\n\n"
            "📸 تصویر فیش واریزی خود را ارسال کنید.\n\n"
            "• تصویر باید واضح و خوانا باشد\n"
            "• مبلغ و تاریخ باید مشخص باشد\n"
            "• بعد از ارسال حداکثر ۲۴ ساعت بررسی می‌شود",
            reply_markup=back_menu
        )
        return

    # ===== ارتباط با پشتیبانی =====
    if text == "📞 ارتباط با پشتیبانی":
        await update.message.reply_text(
            f"📞 ارتباط با پشتیبانی\n\n"
            f"📱 شماره تماس: {SUPPORT_INFO['phone']}\n"
            f"🆔 آیدی تلگرام: {SUPPORT_INFO['telegram']}\n"
            f"⏰ ساعات پاسخگویی: {SUPPORT_INFO['hours']}",
            reply_markup=back_menu
        )
        return

    # ===== پردازش فرم ارزیابی بازار کار =====
    if section == "assessment":
        if step < len(assessment_questions):
            field_name, _ = assessment_questions[step]
            temp[field_name] = text
            if step + 1 < len(assessment_questions):
                set_user_state(user_id, "assessment", step + 1, temp)
                await update.message.reply_text(assessment_questions[step + 1][1], reply_markup=back_menu)
            else:
                save_assessment(user_id, temp)
                await notify_admin(context, user_id, temp, "assessment")
                clear_user_state(user_id)
                await update.message.reply_text(
                    "🌱 ممنون که با حوصله پاسخ دادی.\n\n"
                    "📊 گزارش شناخت سیناپس شامل:\n"
                    "✨ آنچه امروز از تو می‌بینیم\n"
                    "✨ نقاط قوت و ظرفیت‌ها\n"
                    "✨ گره‌ها و موانع مسیر\n"
                    "✨ فرصت‌های رشد\n"
                    "✨ پیشنهاد گام بعدی\n\n"
                    "⏰ زمان تحویل: حداکثر ۲۴ ساعت\n"
                    "💳 هزینه گزارش شناخت: ۲۵۰ هزار تومان\n\n"
                    "پس از پرداخت، فیش را از طریق «💳 ارسال فیش پرداخت» ارسال کنید.",
                    reply_markup=main_menu
                )
        return

    # ===== پردازش فرم اطلاعات شخصی =====
    if section == "personal":
        if step < len(personal_info_questions):
            field_name, _ = personal_info_questions[step]
            temp[field_name] = text
            if step + 1 < len(personal_info_questions):
                set_user_state(user_id, "personal", step + 1, temp)
                await update.message.reply_text(personal_info_questions[step + 1][1], reply_markup=back_menu)
            else:
                summary = get_info_summary(temp, "personal")
                set_user_state(user_id, "personal_confirm", 0, temp)
                await update.message.reply_text(summary, reply_markup=get_confirm_keyboard(), parse_mode="Markdown")
        return

    # ===== پردازش فرم اطلاعات کسب و کار =====
    if section == "business":
        if step < len(business_info_questions):
            field_name, _ = business_info_questions[step]
            temp[field_name] = text
            if step + 1 < len(business_info_questions):
                set_user_state(user_id, "business", step + 1, temp)
                await update.message.reply_text(business_info_questions[step + 1][1], reply_markup=back_menu)
            else:
                summary = get_info_summary(temp, "business")
                set_user_state(user_id, "business_confirm", 0, temp)
                await update.message.reply_text(summary, reply_markup=get_confirm_keyboard(), parse_mode="Markdown")
        return

    # ===== پردازش پرسشنامه تخصصی =====
    if section == "survey":
        if step < len(survey_questions):
            field_name, _ = survey_questions[step]
            temp[field_name] = text
            if step + 1 < len(survey_questions):
                set_user_state(user_id, "survey", step + 1, temp)
                await update.message.reply_text(survey_questions[step + 1][1], reply_markup=back_menu)
            else:
                for key, value in temp.items():
                    save_survey_answer(user_id, key, value)
                clear_user_state(user_id)
                await update.message.reply_text(
                    "🌹 ممنون! پرسشنامه با موفقیت ثبت شد.\n\n"
                    "✅ ظرف ۴۸ ساعت کارشناسان با شما تماس می‌گیرند.",
                    reply_markup=main_menu
                )
        return

    # ===== انتظار برای تصویر فیش =====
    if section == "waiting_receipt":
        await update.message.reply_text("📸 لطفاً تصویر فیش را ارسال کنید.", reply_markup=back_menu)
        return

    # ===== مشاوره هوشمند Gemini (پردازش سوال آزاد) =====
    if not is_user_registered(user_id):
        await update.message.reply_text("⚠️ ابتدا اطلاعات شخصی را ثبت کنید.", reply_markup=main_menu)
        return

    if client is None:
        await update.message.reply_text("⚠️ سرویس هوشمند موقتاً در دسترس نیست.", reply_markup=back_menu)
        return

    user_info = get_user_info(user_id)
    first_name = user_info.get("first_name", "کاربر")
    await update.message.reply_text("⏳ در حال پردازش...")
    try:
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"اطلاعات کاربر:\n"
            f"نام: {first_name} {user_info.get('last_name', '')}\n"
            f"کسب‌وکار: {user_info.get('business_name', 'ثبت نشده')}\n"
            f"شهر: {user_info.get('city', 'ثبت نشده')}\n\n"
            f"سوال کاربر: {text}"
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        await update.message.reply_text(f"{first_name} عزیز،\n\n{response.text}", reply_markup=back_menu)
    except Exception as e:
        logger.error(f"Gemini Error: {e}", exc_info=True)
        await update.message.reply_text(
            f"⚠️ {first_name} عزیز، سرویس هوشمند موقتاً با مشکل مواجه شد.\n"
            f"خطا: {str(e)[:100]}\n\nلطفاً دوباره امتحان کنید.",
            reply_markup=back_menu
        )

# ==================== هندلر دکمه‌های اینلاین (callback) ====================
async def handle_callback(update, context):
    """پردازش دکمه‌های اینلاین: بررسی عضویت، ویرایش، تایید، انصراف"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # ===== بررسی عضویت پس از کلیک روی دکمه =====
    if data == "check_membership":
        is_member = await is_member_of_channel(user_id, context)

        if is_member:
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except Exception:
                pass

            user_info = get_user_info(user_id)

            if is_user_registered(user_id):
                welcome_msg = (
                    f"✨ خوش برگشتی {user_info.get('first_name', '')} عزیز!\n\n"
                    "به سیناپس خوش اومدی. 🌱😍\n"
                    "هر آدمی در یکی از این مسیرها به دنبال رشد و توسعه برای ساختن یک ورژن بهتر از خودشه. "
                    "تو از کجا میخوای شروع کنی؟\n\n"
                    "🟢 بازار کار\n🔵 کسب‌وکار\n🟣 مسئولیت اجتماعی\n🟠 مسیر رشد\n"
                    "🔴 لیدی لجستیک\n🌱 محصولات سیناپس\n\n"
                    "لطفاً مسیر موردنظرت را انتخاب کن. 👇"
                )
            else:
                welcome_msg = (
                    "سلام سلام\n"
                    "شهبازی هستم، مریم 😍🌱\n"
                    "به سیناپس خوش اومدی. 🌱😍\n"
                    "هر آدمی در یکی از این مسیرها به دنبال رشد و توسعه برای ساختن یک ورژن بهتر از خودشه. "
                    "تو از کجا میخوای شروع کنی؟\n\n"
                    "🟢 بازار کار\n🔵 کسب‌وکار\n🟣 مسئولیت اجتماعی\n🟠 مسیر رشد\n"
                    "🔴 لیدی لجستیک\n🌱 محصولات سیناپس\n\n"
                    "لطفاً مسیر موردنظرت را انتخاب کن. 👇"
                )

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
    """دریافت تصویر فیش پرداخت از کاربر و فوروارد به ادمین"""
    user_id = update.effective_user.id
    state = get_user_state(user_id)

    if state["section"] == "waiting_receipt":
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