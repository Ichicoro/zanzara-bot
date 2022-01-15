import datetime, json, sqlite3, functools, shutil
from io import BytesIO
from typing import Callable
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import Filters
from random import randint

from image import create_img

con = None
try:
    con = sqlite3.connect('zanzara.db')
    con.execute('CREATE TABLE IF NOT EXISTS clessy_points (user_id INT, points int, amount_created int)')
    con.commit()
    con.close()
except sqlite3.Error:
    print("Unable to connect to db...")
    exit(1)

config = None
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    shutil.copyfile("sample_config.json", "config.json")
    print("Populate config.json k nye")
    exit(2)
except Exception:
    print("Unable to read config...")
    exit(2)


def with_connection(func: Callable[[Update, CallbackContext, sqlite3.Connection], None]):
    @functools.wraps(func)
    def wrapper_with_conn(update: Update, callback: CallbackContext):
        con = None
        try:
            con = sqlite3.connect('zanzara.db')
        except sqlite3.Error:
            print("Unable to connect to db...")
            update.message.reply_text("C'è un problema col db, sono desolatə. @Ichicoro vieni a fixarmi pls")
            return
        func(update, callback, con)
        con.commit()
        con.close()
    return wrapper_with_conn


def reset_points(context: CallbackContext):
    con = None
    try:
        con = sqlite3.connect('zanzara.db')
    except sqlite3.Error:
        print("Unable to connect to db...")
        return
    
    con.execute("UPDATE clessy_points SET points = 10")

    con.commit()
    con.close()


def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')


@with_connection
def handle_clessy(update: Update, context: CallbackContext, con: sqlite3.Connection) -> None:
    if update.message.reply_to_message is None or update.message.reply_to_message.text == "":
        update.message.reply_text("Questo comando funziona solo se lo usi mentre rispondi a un messaggio 😅")
        return

    if update.message.from_user.id == 341049157:
        if randint(0,1) == 1:
            update.message.reply_text("Oggi non mi va di creare immagini per @Kendottanta :)")
            return

    replied = update.message.reply_to_message
    user_id = replied.from_user.id
    points_query = con.execute("SELECT points FROM clessy_points WHERE user_id=:userid LIMIT 1", { "userid": user_id })
    points = points_query.fetchone()
    print(points)
    
    # If the user has never used the "plugin", insert data into the table
    try:
        points = points[0]
    except TypeError:
        con.execute("""
            INSERT INTO clessy_points (user_id, points, amount_created)
            VALUES (:userid, 10, 0)
        """, { 'userid': user_id })
        points = 10
    
    if points == 0:
        update.message.reply_text(
            "Non hai abbastanza punti per usare /unsplash... Sono desolatə 😅")
        return

    con.execute("""
        UPDATE clessy_points
        SET
            points = points - 1,
            amount_created = amount_created + 1
        WHERE user_id = :userid
    """, {'userid': user_id})

    print(update.message.reply_to_message)

    user = update.message.reply_to_message.forward_sender_name if update.message.reply_to_message.forward_sender_name else update.message.reply_to_message.from_user

    user_text = ""
    if isinstance(user, str):
        user_text = user
    else:
        user_text = f"{user.full_name} ({user.username})" if user.username else f"{user.full_name}"

    photo = BytesIO()
    photo.name = "image.png"
    create_img(update.message.reply_to_message.text, user_text).save(photo, "PNG")
    photo.seek(0)
    update.message.reply_photo(photo=photo)


def handle_user_message(update: Update, context: CallbackContext) -> None:
    return
    if update.message.reply_to_message is None or not update.message.text.startswith(("+", "-")):
        return
    


updater = Updater(config["bot_token"])

updater.job_queue.run_daily(callback=reset_points, time=datetime.time(0, 0), name="resettapunti")

updater.dispatcher.add_handler(CommandHandler('unsplash', handle_clessy))
updater.dispatcher.add_handler(MessageHandler(callback=handle_user_message, filters=Filters.all))

updater.start_polling()
updater.idle()
