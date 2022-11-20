import logging
import os

from desire_path import DesirePathApi, DesirePathError
from google_photos import GooglePhotosAlbum, PhotoUrlsIsEmptyError
from telegram.ext import CommandHandler, Updater


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger("telegram-bot")
logger.setLevel(logging.INFO)

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_PHOTOS_ALBUM_URL_KUSTI = os.getenv("GOOGLE_PHOTOS_ALBUM_URL_KUSTI")
GOOGLE_PHOTOS_ALBUM_URL_BIZ = os.getenv("GOOGLE_PHOTOS_ALBUM_URL_BIZ")
DESIRE_PATH_API_URL = os.getenv("DESIRE_PATH_API_URL")
DESIRE_PATH_URL = os.getenv("DESIRE_PATH_URL")
kusti_album = GooglePhotosAlbum(GOOGLE_PHOTOS_ALBUM_URL_KUSTI)
biz_album = GooglePhotosAlbum(GOOGLE_PHOTOS_ALBUM_URL_BIZ)
desire_path = DesirePathApi(DESIRE_PATH_API_URL)


def start(update, context):
    update.message.reply_text(text="I'm KalmisBot, nice to meet you!")


def random_photo_of_kusti(update, context):
    try:
        photo_url = kusti_album.random_photo_url()
        update.message.reply_photo(photo=photo_url, caption="Here you go!")
    except PhotoUrlsIsEmptyError:
        update.message.reply_text(text="Photos are currently unavailable :(")


def random_photo_of_biz(update, context):
    try:
        photo_url = biz_album.random_photo_url()
        update.message.reply_photo(photo=photo_url, caption="han se on!")
    except PhotoUrlsIsEmptyError:
        update.message.reply_text(text="Photos are currently unavailable :(")


def _return_value_from_path_or_none(data, path):
    element_value = data
    try:
        for element_name in path:
            element_value = element_value[element_name]
        return element_value
    except KeyError:
        print(f"Path not found {path}")
        return None


def _return_price_as_text(data, path, decimals=True):
    price = _return_value_from_path_or_none(data, path + ["value"])
    currency = _return_value_from_path_or_none(data, path + ["currency"])
    period = _return_value_from_path_or_none(data, path + ["period"])
    currency = "€" if currency == "EUR" else currency

    if decimals:
        if period is not None:
            return f"{price:.2f} {currency}/{period}"
        else:
            return f"{price:.2f} {currency}"
    else:
        if period is not None:
            return f"{price:.0f} {currency}/{period}"
        else:
            return f"{price:.0f} {currency}"


def info_of_oikotie_listing(update, context):
    url = context.args[0]
    try:
        data = desire_path.listing_info_from_url(url)
        address = _return_value_from_path_or_none(data, ["location", "fullAddress"])
        address = address.split(",")[0] if address is not None else address
        size = _return_value_from_path_or_none(data, ["basicData", "size", "total", "value"])
        room_configuration = _return_value_from_path_or_none(
            data, ["basicData", "roomConfiguration"]
        )
        price = _return_price_as_text(data, ["price", "sales"], decimals=False)
        free_of_debt_price = _return_price_as_text(data, ["price", "freeOfDebt"], decimals=False)
        price_per_sqm = _return_price_as_text(data, ["price", "perSquareMeter"])
        condominium_charge = _return_price_as_text(data, ["charges", "condominium"])
        financing_charge = _return_price_as_text(data, ["charges", "financialCosts"])

        basic_info = f"{address}, {size} m2 ({room_configuration})\n"
        price_info = f"Myyntihinta: {price} ({free_of_debt_price}), {price_per_sqm}/m2\n"
        lv_cost_info = f"Hoitovastike: {condominium_charge}, Rahoitusvastike: {financing_charge}\n"
        desire_path_analytics_url = f"{DESIRE_PATH_URL}/{url}\n"
        text = basic_info + price_info + lv_cost_info + desire_path_analytics_url
        update.message.reply_text(text=text)
    except DesirePathError:
        update.message.reply_text(text="Fetching oikotie info failed")


def main():
    logger.info("Starting")
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    logger.info("Adding handlers")
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("kusti", random_photo_of_kusti))
    dispatcher.add_handler(CommandHandler("meno", random_photo_of_biz))
    dispatcher.add_handler(CommandHandler("oikotie", info_of_oikotie_listing))

    logger.info("Starting polling")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
