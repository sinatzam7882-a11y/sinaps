# ==================== هندلر پردازش پیام‌های متنی (منو و فرم‌ها) ====================
# این فایل قلب اصلی بات است: تشخیص می‌دهد کاربر کجای منو یا کدام فرم است
# و پاسخ مناسب را برمی‌گرداند. شامل: نمایش زیرمنوها، فرم‌های لیدی لجستیک،
# فرم‌های تب کسب‌وکار/مسئولیت اجتماعی/مسیر رشد (با سوالات ثابت)، اطلاعات
# شخصی/کسب‌وکار، پرسشنامه تخصصی، فرم ارزیابی بازار کار و مشاوره هوشمند Gemini.

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    client, SYSTEM_PROMPT, logger, ADMIN_ID,
    get_user_state, set_user_state, clear_user_state,
    get_user_info, is_user_registered, save_assessment,
    save_survey_answer, save_section_form,
)
from menus import (
    main_menu, market_menu, business_menu, social_menu,
    growth_menu, logistics_menu, back_menu, get_confirm_keyboard,
)
from texts_profile import (
    personal_info_questions, business_info_questions,
    survey_questions, assessment_questions, ASSESSMENT_END_MSG,
    SUPPORT_TEXT_TEMPLATE,
)
from texts_section_forms import (
    BUSINESS_QUESTIONS, SOCIAL_QUESTIONS, GROWTH_QUESTIONS,
    BUSINESS_END_MSG, SOCIAL_END_MSG, GROWTH_END_MSG,
)
from texts_products_logistics import SYNAPSE_PRODUCTS_MSG, LOGISTICS_FORMS
from handlers_core import is_member_of_channel, send_join_message, notify_admin, get_info_summary
from config import SUPPORT_INFO  # اطلاعات تماس پشتیبانی (شماره، آیدی تلگرام، ساعات کاری)

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

    # ===== محصولات و خدمات سیناپس =====
    if text == "🌱 محصولات و خدمات سیناپس":
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
            # فرم تکمیل شد - ذخیره در JSON (برای اکسل) و ارسال به ادمین
            user_info = get_user_info(user_id)
            first_name = user_info.get("first_name", "کاربر")
            sub = temp.get("sub", "")
            form_type = temp.get("form_type", "")
            end_msg = temp.get("end_msg", "")

            # 💾 ذخیره پاسخ‌ها در فایل JSON تا در گزارش اکسل هم بیایند
            save_section_form(user_id, form_type, sub, qs, answers)

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
            "🌱 محصولات و خدمات سیناپس — ابزارها و دوره‌های آموزشی\n\n"
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
            SUPPORT_TEXT_TEMPLATE.format(
                phone=SUPPORT_INFO['phone'],
                telegram=SUPPORT_INFO['telegram'],
                hours=SUPPORT_INFO['hours'],
            ),
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
                await update.message.reply_text(ASSESSMENT_END_MSG, reply_markup=main_menu)
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