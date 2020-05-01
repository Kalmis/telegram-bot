import os
import logging
from telegram.ext import Updater, CommandHandler
from google_photos import GooglePhotosAlbum, PhotoUrlsIsEmptyError


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger('telegram-bot')
logger.setLevel(logging.INFO)

API_TOKEN = os.getenv('TELEGRAM_TOKEN')
GOOGLE_PHOTOS_ALBUM_URL = os.getenv('GOOGLE_PHOTOS_ALBUM_URL')
kusti_album = GooglePhotosAlbum(GOOGLE_PHOTOS_ALBUM_URL)


def start(update, context):
    update.message.reply_text(text="I'm KalmisBot, nice to meet you!")


def random_photo_of_kusti(update, context):
    try:
        photo_url = kusti_album.random_photo_url()
        update.message.reply_photo(photo=photo_url,
                                   caption='Here you go!')
    except PhotoUrlsIsEmptyError:
        update.message.reply_text(text="Photos are currently unavailable :(")


def main():
    logger.info("Starting")
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    logger.info("Adding handlers")
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('kusti', random_photo_of_kusti))

    logger.info("Starting polling")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
