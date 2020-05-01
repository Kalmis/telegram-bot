import os
import logging
import glob
import random
from telegram.ext import Updater, CommandHandler


IMAGES_PATH = '/docs/images/'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger('telegram-bot.' + __name__)
logger.setLevel(logging.INFO)

API_TOKEN = os.getenv('TELEGRAM_TOKEN')

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def random_photo(update, context):

    photos = []
    for extension in ['*.JPG', '*.JPEG']:
        photos += glob.glob(IMAGES_PATH + extension)
    photo = random.choice(photos)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(photo, 'rb'))


if __name__ == "__main__":
    logger.info("Starting")
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    kusti_handler = CommandHandler('kusti', random_photo)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(kusti_handler)
    logger.info("Starting polling")
    updater.start_polling()
