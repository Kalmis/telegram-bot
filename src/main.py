import os
import logging
import requests
from telegram.ext import Updater, CommandHandler
from google_photos import GooglePhotosAlbum, PhotoUrlsIsEmptyError
from desire_path import DesirePathApi, DesirePathError


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger('telegram-bot')
logger.setLevel(logging.INFO)

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
GOOGLE_PHOTOS_ALBUM_URL = os.getenv('GOOGLE_PHOTOS_ALBUM_URL')
DESIRE_PATH_URL = os.getenv('DESIRE_PATH_URL')
kusti_album = GooglePhotosAlbum(GOOGLE_PHOTOS_ALBUM_URL)
desire_path = DesirePathApi(DESIRE_PATH_URL)


def start(update, context):
    update.message.reply_text(text="I'm KalmisBot, nice to meet you!")


def random_photo_of_kusti(update, context):
    try:
        photo_url = kusti_album.random_photo_url()
        update.message.reply_photo(photo=photo_url,
                                   caption='Here you go!')
    except PhotoUrlsIsEmptyError:
        update.message.reply_text(text="Photos are currently unavailable :(")


def info_of_oikotie_listing(update, context):
    url = context.args[0]
    try:
        data = desire_path.listing_info_from_url(url)
        basic = data['Perustiedot']
        basic_info = f"{basic['Sijainti'].split(',')[1]}, {basic['Asuinpinta-ala']}, {basic['Huoneiston kokoonpano']}\n"
        price = data['Hinta']
        price_info = f"Myyntihinta: {price['Myyntihinta']} (Velaton: {price['Velaton hinta']})\n"
        lv_cost = data['Asuinkustannukset']
        lv_cost_info = f"Hoitovastike: {lv_cost['Hoitovastike']}, Rahoitusvastike: {lv_cost['Rahoitusvastike']}, Yhtiövastike: {lv_cost['Yhtiövastike']}\n"
        text = basic_info + price_info + lv_cost_info
        update.message.reply_text(text=text)
    except DesirePathError as e:
        update.message.reply_text(text="Fetching oikotie info failed")


def main():
    logger.info("Starting")
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    logger.info("Adding handlers")
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('kusti', random_photo_of_kusti))
    dispatcher.add_handler(CommandHandler('oikotie', info_of_oikotie_listing))

    logger.info("Starting polling")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
