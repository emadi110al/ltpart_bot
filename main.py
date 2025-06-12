import os
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InputMediaPhoto,
    InputMediaVideo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown

# فعال کردن لاگ برای دیدن خطاها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن متغیرهای محیطی از پلتفرم میزبان (Railway)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

# تعریف حالت‌های مختلف مکالمه برای پرسشنامه
(
    GET_PHOTO,
    GET_VIDEO,
    GET_FULL_NAME,
    GET_MOBILE_NUMBER,
    GET_BRAND_MODEL,
    GET_DXDIAG,
    GET_RAM_SSD,
    GET_BATTERY_HEALTH,
    GET_BREAKAGE,
    GET_SCREEN_STATUS,
    GET_MOTHERBOARD_STATUS,
    GET_CHARGER_STATUS,
) = range(12)

# تعریف کیبوردهای کمکی
main_menu_keyboard = [["➕ فروش جدید لپ‌تاپ"]]
main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

yes_no_keyboard = [["بله", "خیر"]]
yes_no_markup = ReplyKeyboardMarkup(yes_no_keyboard, resize_keyboard=True, one_time_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تابع خوشامدگویی اولیه و نمایش منوی اصلی."""
    user = update.message.from_user
    await update.message.reply_text(
        f"سلام {user.first_name}!\n"
        "به ربات ثبت و فروش لپ‌تاپ کارکرده خوش آمدید.\n\n"
        "برای شروع، روی دکمه زیر کلیک کنید.",
        reply_markup=main_menu_markup,
    )


async def new_sale_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع فرآیند فروش جدید و درخواست اولین اطلاعات (عکس)."""
    context.user_data.clear()  # پاک کردن اطلاعات فروش قبلی در صورت وجود
    await update.message.reply_text(
        "فرآیند ثبت لپ‌تاپ آغاز شد.\n\n"
        "۱. لطفاً یک عکس اصلی از لپ‌تاپ خود ارسال کنید.",
        reply_markup=ReplyKeyboardRemove(),  # حذف کیبورد اصلی در طول فرآیند
    )
    return GET_PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره عکس اصلی و درخواست ویدیو."""
    context.user_data["photo_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("۲. عالی! حالا یک ویدیوی کوتاه (حداکثر ۲۰ ثانیه) از زوایای مختلف دستگاه ارسال کنید.")
    return GET_VIDEO


async def get_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره ویدیو و درخواست نام کامل."""
    context.user_data["video_id"] = update.message.video.file_id
    await update.message.reply_text("۳. نام و نام خانوادگی کامل خود را وارد کنید.")
    return GET_FULL_NAME


async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره نام و درخواست شماره موبایل."""
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("۴. شماره موبایل خود را (ترجیحاً با فرمت 09xxxxxxxxx) وارد کنید.")
    return GET_MOBILE_NUMBER


async def get_mobile_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره شماره موبایل و درخواست برند و مدل."""
    context.user_data["mobile_number"] = update.message.text
    await update.message.reply_text("۵. برند و مدل دقیق دستگاه را وارد کنید (مثال: Lenovo ThinkPad T480).")
    return GET_BRAND_MODEL


async def get_brand_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره برند و مدل و درخواست اسکرین‌شات DxDiag."""
    context.user_data["brand_model"] = update.message.text
    await update.message.reply_text(
        "۶. لطفاً یک اسکرین‌شات از تب System در پنجره DxDiag ویندوز خود ارسال کنید.\n"
        "(برای باز کردن DxDiag، کلیدهای Win+R را فشار داده، dxdiag را تایپ و Enter کنید)."
    )
    return GET_DXDIAG


async def get_dxdiag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره اسکرین‌شات و درخواست مشخصات رم و SSD."""
    context.user_data["dxdiag_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("۷. مشخصات دقیق رم و حافظه SSD/HDD را وارد کنید (مثال: 16GB RAM, 512GB NVMe SSD).")
    return GET_RAM_SSD


async def get_ram_ssd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره مشخصات رم و درخواست سلامت باتری."""
    context.user_data["ram_ssd"] = update.message.text
    await update.message.reply_text("۸. درصد سلامت باتری چقدر است؟ (یک عدد وارد کنید).")
    return GET_BATTERY_HEALTH


async def get_battery_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره سلامت باتری و سوال در مورد شکستگی."""
    context.user_data["battery_health"] = update.message.text
    await update.message.reply_text("۹. آیا دستگاه شکستگی یا فرورفتگی دارد؟", reply_markup=yes_no_markup)
    return GET_BREAKAGE


async def get_breakage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره وضعیت شکستگی و سوال در مورد صفحه‌نمایش."""
    context.user_data["has_breakage"] = update.message.text
    await update.message.reply_text("۱۰. آیا صفحه‌نمایش کاملاً سالم است (بدون پیکسل سوخته، هاله یا خط)؟", reply_markup=yes_no_markup)
    return GET_SCREEN_STATUS


async def get_screen_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره وضعیت صفحه‌نمایش و سوال در مورد مادربرد."""
    context.user_data["screen_status"] = update.message.text
    await update.message.reply_text("۱۱. آیا مادربرد دستگاه تعمیر شده است؟", reply_markup=yes_no_markup)
    return GET_MOTHERBOARD_STATUS


async def get_motherboard_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره وضعیت مادربرد و سوال در مورد شارژر."""
    context.user_data["motherboard_status"] = update.message.text
    await update.message.reply_text("۱۲. آیا دستگاه آداپتور شارژر اصلی خود را دارد؟", reply_markup=yes_no_markup)
    return GET_CHARGER_STATUS


async def get_charger_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ذخیره وضعیت شارژر، ارسال گزارش کامل به مدیر و پایان مکالمه."""
    context.user_data["charger_status"] = update.message.text
    user_info = context.user_data
    user = update.message.from_user

    await update.message.reply_text(
        "✅ اطلاعات شما با موفقیت تکمیل شد. در حال ارسال برای مدیر...",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Escape کردن تمام ورودی‌های کاربر برای جلوگیری از خطای Markdown
    full_name = escape_markdown(user_info.get('full_name', 'وارد نشده'), version=2)
    mobile_number = escape_markdown(user_info.get('mobile_number', 'وارد نشده'), version=2)
    brand_model = escape_markdown(user_info.get('brand_model', 'وارد نشده'), version=2)
    ram_ssd = escape_markdown(user_info.get('ram_ssd', 'وارد نشده'), version=2)
    battery_health = escape_markdown(user_info.get('battery_health', 'وارد نشده'), version=2)
    
    # MODIFIED: تمام کاراکترهای "-" در لیست با "\-" جایگزین شدند
    report = (
        f"💻 *درخواست فروش لپ‌تاپ جدید* 💻\n\n"
        f"👤 *اطلاعات فروشنده:*\n"
        f"\- نام کامل: {full_name}\n"
        f"\- شماره تماس: {mobile_number}\n"
        f"\- یوزرنیم تلگرام: @{escape_markdown(user.username, version=2) if user.username else 'ندارد'}\n\n"
        f"📋 *مشخصات دستگاه:*\n"
        f"\- برند و مدل: {brand_model}\n"
        f"\- رم و حافظه: {ram_ssd}\n"
        f"\- سلامت باتری: {battery_health}%\n\n"
        f"📝 *وضعیت ظاهری و فنی:*\n"
        f"\- شکستگی یا فرورفتگی: {user_info.get('has_breakage', 'وارد نشده')}\n"
        f"\- وضعیت صفحه‌نمایش: {user_info.get('screen_status', 'وارد نشده')}\n"
        f"\- مادربرد تعمیر شده: {user_info.get('motherboard_status', 'وارد نشده')}\n"
        f"\- آداپتور اصلی: {user_info.get('charger_status', 'وارد نشده')}\n"
    )

    # ساخت لیست مدیا برای ارسال به صورت آلبوم
    media_group = [
        InputMediaPhoto(media=user_info["photo_id"], caption="عکس اصلی دستگاه"),
        InputMediaVideo(media=user_info["video_id"]),
        InputMediaPhoto(media=user_info["dxdiag_id"]),
    ]
    
    # ارسال گزارش به ادمین
    try:
        await context.bot.send_media_group(chat_id=ADMIN_CHAT_ID, media=media_group)
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=report, parse_mode='MarkdownV2')
    except Exception as e:
        logger.error(f"Failed to send report to admin: {e}")
        await update.message.reply_text("متاسفانه در ارسال اطلاعات به مدیر مشکلی پیش آمد. لطفاً بعداً دوباره تلاش کنید.")

    # پیام نهایی به کاربر
    await update.message.reply_text(
        "گزارش شما با موفقیت برای مدیریت ارسال شد. نتیجه به زودی به شما اطلاع داده خواهد شد.\n\n"
        "ممنون از شما!",
        reply_markup=main_menu_markup,
    )

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو کامل فرآیند و بازگشت به منوی اصلی."""
    context.user_data.clear()
    await update.message.reply_text(
        "فرآیند ثبت محصول لغو شد.", reply_markup=main_menu_markup
    )
    return ConversationHandler.END


def main() -> None:
    """راه‌اندازی و اجرای ربات."""
    application = Application.builder().token(BOT_TOKEN).build()

    # تعریف کنترل‌کننده مکالمه با تمام مراحل
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(["➕ فروش جدید لپ‌تاپ"]), new_sale_start)],
        states={
            GET_PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            GET_VIDEO: [MessageHandler(filters.VIDEO, get_video)],
            GET_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            GET_MOBILE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mobile_number)],
            GET_BRAND_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_brand_model)],
            GET_DXDIAG: [MessageHandler(filters.PHOTO, get_dxdiag)],
            GET_RAM_SSD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ram_ssd)],
            GET_BATTERY_HEALTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_battery_health)],
            GET_BREAKAGE: [MessageHandler(filters.Regex("^(بله|خیر)$"), get_breakage)],
            GET_SCREEN_STATUS: [MessageHandler(filters.Regex("^(بله|خیر)$"), get_screen_status)],
            GET_MOTHERBOARD_STATUS: [MessageHandler(filters.Regex("^(بله|خیر)$"), get_motherboard_status)],
            GET_CHARGER_STATUS: [MessageHandler(filters.Regex("^(بله|خیر)$"), get_charger_status)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    print("Laptop seller bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
