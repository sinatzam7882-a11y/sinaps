# استفاده از Python 3.10 به عنوان پایه
FROM python:3.10-slim

# تنظیم متغیرهای محیطی برای Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Tehran

# تنظیم timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# ایجاد دایرکتوری کاری
WORKDIR /app

# کپی کردن فایل requirements.txt اول (برای استفاده از کش Docker)
COPY requirements.txt .

# نصب وابستگی‌ها
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن تمام فایل‌های پروژه
COPY . .

# ایجاد دایرکتوری برای ذخیره فایل‌های JSON و Excel
RUN mkdir -p /app/data && \
    mkdir -p /app/images

# ایجاد کاربر غیر ریشه برای امنیت بیشتر
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# سوئیچ به کاربر غیر ریشه
USER botuser

# پورت پیش‌فرض (اگر نیاز باشد)
EXPOSE 8080

# دستور اجرای بات
CMD ["python", "bot.py"]