import os
import logging
from telegram import Update, ReplyKeyboardMarkup # MODIFIED: ReplyKeyboardMarkup را اضافه کردیم
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

# مقادیر ثابت را از متغیرهای محیطی Railway بخوانید
BOT_TOKEN = os.environ.get("7881822944:AAGxT_kO7hu2upomyzoObVwDys-NNr0syUU")
ADMIN_CHAT_ID = os.environ.get("7390493561")

# تعریف مراحل مکالمه
GET_PHOTO, GET_DESCRIPTION = range(2)

# NEW: تعریف کیبورد اصلی برنامه
main_menu_keyboard = [
    ["➕ فروش جدید"],
]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ # MODIFIED: این تابع دیگر مکالمه را شروع نمی‌کند، فقط خوشامد می‌گوید و کیبورد را نمایش می‌دهد """
    user = update.message.from_user
    await update.message.reply_text(
        f"سلام {user.first_name}! به ربات فروش قطعات خوش آمدید.\n\n"
        "برای ثبت یک محصول جدید، روی دکمه '➕ فروش جدید' کلیک کنید.",
        reply_markup=main_menu_markup # NEW: نمایش کیبورد اصلی
    )

async def new_sale_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ # NEW: این تابع جدید، مکالمه برای فروش جدید را آغاز می‌کند """
    await update.message.reply_text(
        "لطفاً عکس قطعه مورد نظر خود را ارسال کنید.\n\n"
        "برای لغو فرآیند، می‌توانید /cancel را ارسال کنید."
    )
    return GET_PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره عکس و درخواست توضیحات."""
    photo_file = await update.message.photo[-1].get_file()
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

    caption = (
        f"یک محصول جدید از طرف کاربر:\n"
        f"نام: {user.full_name}\n"
        f"نام کاربری: @{user.username}\n"
        f"آیدی: {user.id}\n\n"
        f"مشخصات محصول:\n{description}"
    )
    await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_id, caption=caption)

    await update.message.reply_text(
        "✅ متشکرم! اطلاعات شما با موفقیت برای مدیر ارسال شد.",
        reply_markup=main_menu_markup # MODIFIED: نمایش مجدد کیبورد اصلی در پایان کار
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو مکالمه."""
    await update.message.reply_text(
        "فرآیند ارسال محصول لغو شد.",
        reply_markup=main_menu_markup # MODIFIED: نمایش مجدد کیبورد اصلی پس از لغو
    )
    context.user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """اجرای ربات."""
    application = Application.builder().token(BOT_TOKEN).build()

    # MODIFIED: کنترل‌کننده مکالمه اکنون با کلیک روی دکمه شروع می‌شود
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(["➕ فروش جدید"]), new_sale_start)], # MODIFIED
        states={
            GET_PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            GET_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # NEW: دستور /start اکنون به صورت جداگانه و خارج از مکالمه تعریف می‌شود
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    # شروع به کار ربات
    print("Bot is running...") # NEW: یک پیام برای لاگ‌ها جهت اطمینان از اجرا
    application.run_polling()


if __name__ == "__main__":
    main()
