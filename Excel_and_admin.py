# ==================== فایل گزارش اکسل و دستورات ادمین ====================
# این فایل شامل: تولید فایل اکسل، دستورات ادمین (/getexcel, /getdata, /summary, /broadcast) است

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime
from telegram import Update
from config import (
    read_json, USERS_FILE, SURVEY_FILE, ASSESSMENT_FILE,
    EXCEL_FILE, ADMIN_ID, logger
)

# ==================== تولید فایل اکسل ====================
def generate_excel_report():
    """ساخت فایل اکسل با اطلاعات کاربران، فرم‌های ارزیابی، پرسشنامه و آمار"""
    users = read_json(USERS_FILE, {})
    surveys = read_json(SURVEY_FILE, {})
    assessments = read_json(ASSESSMENT_FILE, {})

    wb = openpyxl.Workbook()

    # استایل مشترک ستون‌های هدر
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border = Border(left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='thin'), bottom=Side(style='thin'))

    # ===== شیت ۱: اطلاعات کاربران =====
    ws1 = wb.active
    ws1.title = "اطلاعات کاربران"

    headers = ["ردیف", "آیدی تلگرام", "نام", "نام خانوادگی", "تاریخ تولد",
               "شماره تماس", "شهر", "نام کسب و کار", "آدرس", "راه معرفی", "تاریخ ثبت"]

    for col, header in enumerate(headers, 1):
        cell = ws1.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    for row, (user_id, info) in enumerate(users.items(), 2):
        ws1.cell(row=row, column=1, value=row - 1)
        ws1.cell(row=row, column=2, value=info.get('telegram_id', user_id))
        ws1.cell(row=row, column=3, value=info.get('first_name', ''))
        ws1.cell(row=row, column=4, value=info.get('last_name', ''))
        ws1.cell(row=row, column=5, value=info.get('birth_date', ''))
        ws1.cell(row=row, column=6, value=info.get('phone', ''))
        ws1.cell(row=row, column=7, value=info.get('city', ''))
        ws1.cell(row=row, column=8, value=info.get('business_name', ''))
        ws1.cell(row=row, column=9, value=info.get('address', ''))
        ws1.cell(row=row, column=10, value=info.get('referral_source', ''))
        ws1.cell(row=row, column=11, value=info.get('last_update', ''))

    for col in range(1, len(headers) + 1):
        ws1.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20

    # ===== شیت ۲: فرم ارزیابی =====
    ws2 = wb.create_sheet("فرم_ارزیابی")

    assessment_headers = ["ردیف", "آیدی تلگرام", "نام و نام خانوادگی", "شماره تماس", "سن",
                          "استان و شهر", "نقش فعلی", "حوزه تخصصی", "سه توانمندی",
                          "دغدغه شغلی", "درآمد ماهیانه", "هدف یک ساله", "موانع اصلی",
                          "مسئله حل شدنی", "نیاز اصلی", "نکته تکمیلی", "تاریخ ثبت"]

    for col, header in enumerate(assessment_headers, 1):
        cell = ws2.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    for row, (user_id, answers) in enumerate(assessments.items(), 2):
        user_info = users.get(user_id, {})
        ws2.cell(row=row, column=1, value=row - 1)
        ws2.cell(row=row, column=2, value=user_info.get('telegram_id', user_id))
        ws2.cell(row=row, column=3, value=answers.get('full_name', ''))
        ws2.cell(row=row, column=4, value=answers.get('phone', ''))
        ws2.cell(row=row, column=5, value=answers.get('age', ''))
        ws2.cell(row=row, column=6, value=answers.get('location', ''))
        ws2.cell(row=row, column=7, value=answers.get('role', ''))
        ws2.cell(row=row, column=8, value=answers.get('field', ''))
        ws2.cell(row=row, column=9, value=answers.get('strengths', ''))
        ws2.cell(row=row, column=10, value=answers.get('challenge', ''))
        ws2.cell(row=row, column=11, value=answers.get('income', ''))
        ws2.cell(row=row, column=12, value=answers.get('goal', ''))
        ws2.cell(row=row, column=13, value=answers.get('obstacles', ''))
        ws2.cell(row=row, column=14, value=answers.get('solve_problem', ''))
        ws2.cell(row=row, column=15, value=answers.get('need', ''))
        ws2.cell(row=row, column=16, value=answers.get('note', ''))
        ws2.cell(row=row, column=17, value=answers.get('submitted_at', ''))

    for col in range(1, len(assessment_headers) + 1):
        ws2.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 25

    # ===== شیت ۳: پرسشنامه تخصصی =====
    ws3 = wb.create_sheet("پرسشنامه")

    survey_headers = ["ردیف", "آیدی تلگرام", "نام", "نام خانوادگی", "نام کسب و کار",
                      "درباره کسب و کار", "محصولات و مزیت", "زیرساخت مجازی",
                      "تیم", "فروش ماهیانه", "چالش اصلی", "نیاز مشاوره"]

    for col, header in enumerate(survey_headers, 1):
        cell = ws3.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border

    for row, (user_id, answers) in enumerate(surveys.items(), 2):
        user_info = users.get(user_id, {})
        ws3.cell(row=row, column=1, value=row - 1)
        ws3.cell(row=row, column=2, value=user_info.get('telegram_id', user_id))
        ws3.cell(row=row, column=3, value=user_info.get('first_name', ''))
        ws3.cell(row=row, column=4, value=user_info.get('last_name', ''))
        ws3.cell(row=row, column=5, value=user_info.get('business_name', ''))
        ws3.cell(row=row, column=6, value=answers.get('about_business', ''))
        ws3.cell(row=row, column=7, value=answers.get('products', ''))
        ws3.cell(row=row, column=8, value=answers.get('infrastructure', ''))
        ws3.cell(row=row, column=9, value=answers.get('team', ''))
        ws3.cell(row=row, column=10, value=answers.get('sales', ''))
        ws3.cell(row=row, column=11, value=answers.get('problem', ''))
        ws3.cell(row=row, column=12, value=answers.get('consulting', ''))

    for col in range(1, len(survey_headers) + 1):
        ws3.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20

    # ===== شیت ۴: خلاصه آمار =====
    ws4 = wb.create_sheet("خلاصه آمار")

    stats_data = [
        ["آمار کلی", ""],
        ["تعداد کل کاربران", len(users)],
        ["تعداد فرم‌های ارزیابی تکمیل شده", len(assessments)],
        ["تعداد پرسشنامه‌های تکمیل شده", sum(1 for u in surveys if len(surveys[u]) > 2)],
        ["تاریخ تولید گزارش", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["", ""],
        ["آخرین ۵ کاربر", ""],
    ]

    for i, (user_id, info) in enumerate(list(users.items())[-5:], 1):
        name = f"{info.get('first_name', '')} {info.get('last_name', '')}"
        stats_data.append([f"{i}. {name}", info.get('business_name', '')])

    for row, (key, value) in enumerate(stats_data, 1):
        ws4.cell(row=row, column=1, value=key)
        ws4.cell(row=row, column=2, value=value)

    ws4.column_dimensions['A'].width = 30
    ws4.column_dimensions['B'].width = 30

    wb.save(EXCEL_FILE)
    return EXCEL_FILE

# ==================== دستور /getexcel - دریافت فایل اکسل ====================
async def get_excel(update: Update, context):
    """ادمین می‌تواند با این دستور فایل اکسل کامل کاربران را دریافت کند"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی ندارید!")
        return

    await update.message.reply_text("📊 در حال تولید فایل اکسل... لطفاً صبر کنید...")

    try:
        excel_file = generate_excel_report()
        with open(excel_file, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f'users_data_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
                caption="📊 **گزارش کامل کاربران**\n\n"
                        f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                        "📋 شامل: اطلاعات کاربران + فرم ارزیابی + پرسشنامه + آمار"
            )
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا در تولید فایل: {str(e)}")

# ==================== دستور /getdata - دریافت فایل‌های JSON خام ====================
async def get_data(update: Update, context):
    """ادمین می‌تواند فایل‌های JSON خام را دریافت کند"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی ندارید!")
        return

    import os
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'rb') as f:
            await update.message.reply_document(f, filename=f'users_{datetime.now().strftime("%Y%m%d")}.json')

    if os.path.exists(SURVEY_FILE):
        with open(SURVEY_FILE, 'rb') as f:
            await update.message.reply_document(f, filename=f'survey_{datetime.now().strftime("%Y%m%d")}.json')

    if os.path.exists(ASSESSMENT_FILE):
        with open(ASSESSMENT_FILE, 'rb') as f:
            await update.message.reply_document(f, filename=f'assessment_{datetime.now().strftime("%Y%m%d")}.json')

# ==================== دستور /summary - آمار خلاصه ====================
async def show_summary(update: Update, context):
    """نمایش آمار کلی کاربران برای ادمین"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی ندارید!")
        return

    users = read_json(USERS_FILE, {})
    surveys = read_json(SURVEY_FILE, {})
    assessments = read_json(ASSESSMENT_FILE, {})

    completed_surveys = sum(1 for u in surveys if len(surveys[u]) > 2)
    today = datetime.now().strftime("%Y-%m-%d")
    today_users = sum(1 for u in users.values() if u.get("last_update", "").startswith(today))

    summary = f"📊 **آمار کلی:**\n\n"
    summary += f"👥 کل کاربران: {len(users)}\n"
    summary += f"📋 فرم‌های ارزیابی تکمیل شده: {len(assessments)}\n"
    summary += f"📊 پرسشنامه‌های تکمیل شده: {completed_surveys}\n"
    summary += f"🆕 کاربران امروز: {today_users}\n\n"
    summary += "**آخرین ۵ کاربر:**\n"

    for i, (uid, info) in enumerate(list(users.items())[-5:], 1):
        name = f"{info.get('first_name', '')} {info.get('last_name', '')}"
        business = info.get('business_name', 'نامشخص')
        summary += f"{i}. {name} - {business}\n"

    await update.message.reply_text(summary, parse_mode='Markdown')

# ==================== دستور /broadcast - ارسال پیام همگانی ====================
async def broadcast(update: Update, context):
    """ارسال پیام به تمام کاربران ثبت‌شده (فقط ادمین)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی ندارید!")
        return

    users = read_json(USERS_FILE, {})
    if not users:
        await update.message.reply_text("📭 هیچ کاربری ثبت نشده!")
        return

    message_text = " ".join(context.args)
    if not message_text:
        await update.message.reply_text("⚠️ لطفاً پیام خود را وارد کنید.\nمثال: /broadcast سلام به همه!")
        return

    await update.message.reply_text(f"📤 ارسال پیام به {len(users)} کاربر...")

    success = 0
    for user_id in users.keys():
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"📢 **پیام از طرف مدیریت:**\n\n{message_text}"
            )
            success += 1
        except:
            pass

    await update.message.reply_text(f"✅ پیام به {success} کاربر ارسال شد.")