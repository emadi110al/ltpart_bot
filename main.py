import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# فعال کردن لاگ برای دیدن خطاها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# تعریف مراحل مکالمه
GET_PHOTO, GET_DESCRIPTION = range(2)

# مقادیر ثابت
# !!! توکن ربات خود و آیدی عددی مدیر را در اینجا جایگزین کنید !!!
BOT_TOKEN = "7881822944:AAGxT_kO7hu2upomyzoObVwDys-NNr0syUU"  # توکن ربات که از BotFather گرفتید
ADMIN_CHAT_ID = "7390493561"  # آیدی عددی اکانت مدیر

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع مکالمه و درخواست عکس محصول."""
    user = update.message.from_user
    await update.message.reply_text(
        f"سلام {user.first_name}!\n"
        "لطفاً عکس قطعه مورد نظر خود را ارسال کنید.\n\n"
        "برای لغو فرآیند، می‌توانید /cancel را ارسال کنید."
    )
    return GET_PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره عکس و درخواست توضیحات."""
    # دریافت بهترین کیفیت عکس ارسال شده
    photo_file = await update.message.photo[-1].get_file()
    
    # ذخیره آیدی فایل عکس در حافظه موقت ربات برای این کاربر
    context.user_data['photo_id'] = photo_file.file_id
    
    await update.message.reply_text(
        "عالی! حالا لطفاً مشخصات کامل محصول (مانند نام، مدل، وضعیت و قیمت پیشنهادی) را در یک پیام متنی ارسال کنید."
    )
    return GET_DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """دریافت توضیحات، فوروارد به مدیر و پایان مکالمه."""
    user = update.message.from_user
    photo_id = context.user_data['photo_id']
    description = update.message.text

    # ساخت متن پیام برای مدیر
    caption = (
        f"یک محصول جدید از طرف کاربر:\n"
        f"نام: {user.full_name}\n"
        f"نام کاربری: @{user.username}\n"
        f"آیدی: {user.id}\n\n"
        f"مشخصات محصول:\n{description}"
    )

    # ارسال عکس به همراه توضیحات برای مدیر
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_id, caption=caption)

    # پیام تشکر برای کاربر
    await update.message.reply_text(
        "✅ متشکرم! اطلاعات شما با موفقیت برای مدیر ارسال شد. به زودی با شما تماس گرفته خواهد شد."
    )
    
    # پاک کردن حافظه موقت و پایان مکالمه
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو مکالمه."""
    await update.message.reply_text("فرآیند ارسال محصول لغو شد.")
    context.user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """اجرای ربات."""
    application = Application.builder().token(BOT_TOKEN).build()

    # تعریف کنترل‌کننده مکالمه
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # شروع به کار ربات
    application.run_polling()


if __name__ == "__main__":
    main()
