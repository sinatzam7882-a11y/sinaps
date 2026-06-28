# ==================== هندلرهای سیستم اشتراک ====================
# این فایل شامل: نمایش پلن‌های اشتراک، انتخاب پلن، دریافت فیش پرداخت اشتراک،
# و تایید/رد درخواست توسط ادمین (با دکمه‌های اینلاین) است.

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton

from config import (
    logger, ADMIN_ID, SUBSCRIPTION_TIERS, get_active_subscription_tiers,
    get_user_state, set_user_state, clear_user_state,
    get_user_info, get_subscription, create_pending_subscription,
    approve_subscription, reject_subscription,
)
from menus import (
    main_menu, back_menu, get_subscription_tiers_keyboard,
    get_admin_subscription_keyboard,
)
from texts_subscription import (
    build_subscription_intro, build_subscription_payment_instructions,
    SUBSCRIPTION_PENDING_MSG, build_subscription_approved_msg,
    SUBSCRIPTION_REJECTED_MSG, build_admin_subscription_notice,
)

# ==================== دکمه «💎 خرید اشتراک» در منوی اصلی ====================
async def show_subscription_plans(update: Update, context):
    """نمایش لیست سطوح اشتراک فعال (الان فقط برنزی) با دکمه‌ی انتخاب - از پیام متنی"""
    active_tiers = get_active_subscription_tiers()
    if not active_tiers:
        await update.message.reply_text(
            "⚠️ در حال حاضر هیچ پلن اشتراکی فعال نیست. لطفاً بعداً تلاش کنید.",
            reply_markup=main_menu
        )
        return

    text = build_subscription_intro(active_tiers)
    await update.message.reply_text(text, reply_markup=get_subscription_tiers_keyboard(active_tiers))

# ==================== همان نمایش پلن‌ها، اما وقتی از یک دکمه‌ی اینلاین صدا زده شده ====================
async def show_subscription_plans_from_callback(update, context):
    """نسخه‌ی callback-safe تابع بالا (وقتی از طریق دکمه‌ی شیشه‌ای 'خرید/تمدید اشتراک' صدا زده می‌شود)"""
    query = update.callback_query
    active_tiers = get_active_subscription_tiers()
    if not active_tiers:
        await query.message.reply_text(
            "⚠️ در حال حاضر هیچ پلن اشتراکی فعال نیست. لطفاً بعداً تلاش کنید.",
            reply_markup=main_menu
        )
        return

    text = build_subscription_intro(active_tiers)
    await query.message.reply_text(text, reply_markup=get_subscription_tiers_keyboard(active_tiers))

# ==================== انتخاب یک سطح اشتراک (callback از دکمه‌ی اینلاین) ====================
async def handle_subscription_tier_selection(update, context, tier_key):
    """
    کاربر روی یکی از دکمه‌های سطح اشتراک کلیک کرده (مثلاً 'sub_select_bronze').
    راهنمای پرداخت + هدایت به تب ارسال فیش نشان داده می‌شود.
    """
    query = update.callback_query
    user_id = query.from_user.id

    tier = SUBSCRIPTION_TIERS.get(tier_key)
    if not tier or not tier.get("active"):
        await query.message.reply_text("⚠️ این سطح اشتراک در حال حاضر فعال نیست.", reply_markup=main_menu)
        return

    # وضعیت کاربر را روی «در انتظار ارسال فیش اشتراک» می‌گذاریم تا وقتی
    # عکس فرستاد، handle_photo بداند این فیش برای «اشتراک» است نه برای
    # فی ۲۵۰هزارتومانی فرم‌های دیگر.
    set_user_state(user_id, "waiting_subscription_receipt", 0, {"tier": tier_key})

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    text = build_subscription_payment_instructions(tier)
    await query.message.reply_text(text, reply_markup=back_menu)

# ==================== دریافت فیش پرداخت اشتراک (از داخل handle_photo صدا زده می‌شود) ====================
async def process_subscription_receipt(update, context, user_id, tier_key):
    """
    وقتی کاربری که state او 'waiting_subscription_receipt' است عکس می‌فرستد،
    این تابع از handlers_core.handle_photo صدا زده می‌شود.
    """
    user_info = get_user_info(user_id)
    first_name = user_info.get("first_name", "کاربر")
    last_name = user_info.get("last_name", "")
    tier = SUBSCRIPTION_TIERS.get(tier_key, SUBSCRIPTION_TIERS["bronze"])

    # 💾 وضعیت را 'pending' (در انتظار تایید ادمین) می‌کنیم
    create_pending_subscription(user_id, tier_key)

    # ارسال فیش + اطلاعات کاربر به ادمین همراه با دکمه‌ی تایید/رد
    try:
        notice = build_admin_subscription_notice(user_id, first_name, last_name, tier)
        await context.bot.send_message(chat_id=ADMIN_ID, text=notice)
        photo = update.message.photo[-1]
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo.file_id,
            reply_markup=get_admin_subscription_keyboard(user_id)
        )
    except Exception as e:
        logger.error(f"خطا در ارسال فیش اشتراک به ادمین: {e}")

    clear_user_state(user_id)
    await update.message.reply_text(SUBSCRIPTION_PENDING_MSG, reply_markup=main_menu)

# ==================== تایید اشتراک توسط ادمین (callback 'sub_approve_<id>') ====================
async def handle_admin_approve_subscription(update, context, target_user_id):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ فقط ادمین می‌تواند این کار را انجام دهد.", show_alert=True)
        return

    record = approve_subscription(target_user_id)
    tier = SUBSCRIPTION_TIERS.get(record.get("tier", "bronze"), SUBSCRIPTION_TIERS["bronze"])

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await query.message.reply_text(f"✅ اشتراک کاربر {target_user_id} تایید و فعال شد.")

    # اطلاع به خود کاربر
    try:
        msg = build_subscription_approved_msg(tier, record["expires_at"])
        await context.bot.send_message(chat_id=int(target_user_id), text=msg, reply_markup=main_menu)
    except Exception as e:
        logger.error(f"خطا در اطلاع‌رسانی تایید اشتراک به کاربر {target_user_id}: {e}")

# ==================== رد اشتراک توسط ادمین (callback 'sub_reject_<id>') ====================
async def handle_admin_reject_subscription(update, context, target_user_id):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ فقط ادمین می‌تواند این کار را انجام دهد.", show_alert=True)
        return

    reject_subscription(target_user_id)

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass
    await query.message.reply_text(f"❌ درخواست اشتراک کاربر {target_user_id} رد شد.")

    try:
        await context.bot.send_message(chat_id=int(target_user_id), text=SUBSCRIPTION_REJECTED_MSG, reply_markup=main_menu)
    except Exception as e:
        logger.error(f"خطا در اطلاع‌رسانی رد اشتراک به کاربر {target_user_id}: {e}")