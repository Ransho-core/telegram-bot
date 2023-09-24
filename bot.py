import json
import telebot
import os
import datetime
import threading
import schedule
import time
import pytz
from telebot import types
from decouple import config


# import wikipediaapi
# import subprocess

TOKEN = config('BOT_TOKEN')

# Dictionary mapping country names to their respective timezones
country_timezones = {
    "USA": "America/New_York",
    "UK": "Europe/London",
    "India": "Asia/Kolkata",
    "Saudi Arabia": "Asia/Riyadh",
    "United Arab Emirates": "Asia/Dubai",
    "Egypt": "Africa/Cairo",
    "Iraq": "Asia/Baghdad",
    "Kuwait": "Asia/Kuwait",
    "Qatar": "Asia/Qatar",
    "Bahrain": "Asia/Bahrain",
    "Oman": "Asia/Muscat",
    "Jordan": "Asia/Amman",
    "Lebanon": "Asia/Beirut",
    "Syria": "Asia/Damascus",
    "Yemen": "Asia/Aden",
    "Sudan": "Africa/Khartoum",
    "Tunisia": "Africa/Tunis",
    "Libya": "Africa/Tripoli",
    "Morocco": "Africa/Casablanca",
    "Algeria": "Africa/Algiers",
    "Mauritania": "Africa/Nouakchott",
    "Somalia": "Africa/Mogadishu",
    "Djibouti": "Africa/Djibouti",
    "Comoros": "Indian/Comoro",
    "France": "Europe/Paris",
    "Germany": "Europe/Berlin",
    "Spain": "Europe/Madrid",
    "Italy": "Europe/Rome",
    "Netherlands": "Europe/Amsterdam",
    "Belgium": "Europe/Brussels",
    "Switzerland": "Europe/Zurich",
    "Austria": "Europe/Vienna",
    "Greece": "Europe/Athens",
    "Sweden": "Europe/Stockholm",
    "Norway": "Europe/Oslo",
    "Denmark": "Europe/Copenhagen",
    "Finland": "Europe/Helsinki",
    "Portugal": "Europe/Lisbon",
    "Ireland": "Europe/Dublin",
    "Poland": "Europe/Warsaw",
    "Hungary": "Europe/Budapest",
    "Czech Republic": "Europe/Prague",
    "Slovakia": "Europe/Bratislava",
    "Romania": "Europe/Bucharest",
    "Bulgaria": "Europe/Sofia",
    "Croatia": "Europe/Zagreb",
    "Slovenia": "Europe/Ljubljana",
    "Estonia": "Europe/Tallinn",
    "Latvia": "Europe/Riga",
    "Lithuania": "Europe/Vilnius",
    "Cyprus": "Asia/Nicosia",
    "Iceland": "Atlantic/Reykjavik",
    "Luxembourg": "Europe/Luxembourg",
    "Malta": "Europe/Malta",
    "Monaco": "Europe/Monaco",
    "Montenegro": "Europe/Podgorica",
    "North Macedonia": "Europe/Skopje",
    "Serbia": "Europe/Belgrade",
    "Slovakia": "Europe/Bratislava",
    "Slovenia": "Europe/Ljubljana",
    "Estonia": "Europe/Tallinn",
    "Latvia": "Europe/Riga",
    "Lithuania": "Europe/Vilnius",
    "Cyprus": "Asia/Nicosia",
    "Iceland": "Atlantic/Reykjavik",
    "Luxembourg": "Europe/Luxembourg",
    "Malta": "Europe/Malta",
    "Monaco": "Europe/Monaco",
    "Montenegro": "Europe/Podgorica",
    "North Macedonia": "Europe/Skopje",
    "Serbia": "Europe/Belgrade",
    "Bosnia and Herzegovina": "Europe/Sarajevo",
    "Croatia": "Europe/Zagreb",
    "Slovenia": "Europe/Ljubljana",
    "Kosovo": "Europe/Pristina",
    "Albania": "Europe/Tirane",
    "Bulgaria": "Europe/Sofia",
    "Romania": "Europe/Bucharest",
    "Moldova": "Europe/Chisinau",
    "Ukraine": "Europe/Kiev",
    "Belarus": "Europe/Minsk",
    "Estonia": "Europe/Tallinn",
    "Latvia": "Europe/Riga",
    "Lithuania": "Europe/Vilnius",
    "Cyprus": "Asia/Nicosia",
    "Iceland": "Atlantic/Reykjavik",
    "Luxembourg": "Europe/Luxembourg",
    "Malta": "Europe/Malta",
    "Monaco": "Europe/Monaco",
    "Montenegro": "Europe/Podgorica",
    "North Macedonia": "Europe/Skopje",
    "Serbia": "Europe/Belgrade",
    "Bosnia and Herzegovina": "Europe/Sarajevo",
    "Croatia": "Europe/Zagreb",
    "Slovenia": "Europe/Ljubljana",
    "Kosovo": "Europe/Pristina",
    "Albania": "Europe/Tirane",
    "Bulgaria": "Europe/Sofia",
    "Romania": "Europe/Bucharest",
    "Moldova": "Europe/Chisinau",
    "Ukraine": "Europe/Kiev",
    "Belarus": "Europe/Minsk",
    "Poland": "Europe/Warsaw",
    "Hungary": "Europe/Budapest",
    "Czech Republic": "Europe/Prague",
    "Slovakia": "Europe/Bratislava",
    "Greece": "Europe/Athens",
}

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Define the file to store messages
db_file = 'messages.json'
db_ids = 'ids.json'
# Create a dictionary to store messages with labels
message_dict = {}

# Define a dictionary to store user-specific labels
user_labels = {}

# Define a dictionary to store user-specific ides
user_ids = {}

user_alarms = {}  # Dictionary to store user alarms

# Load messages from the database file (if it exists)
if os.path.exists(db_file):
    with open(db_file, 'r') as file:
        message_dict = json.load(file)

if os.path.exists(db_ids):
    with open(db_ids, 'r') as file_ids:
        user_ids = json.load(file_ids)


def label_exists(label):
    return label in message_dict


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, (message.from_user.username+", how are you doing?"))
    # Save the original text message with the label
    user_ids[message.from_user.id] = message.from_user.username

    with open(db_ids, 'w') as file_ids:
        json.dump(user_ids, file_ids, indent=4)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = """
    Available commands:
    
    /start or /hello - Greet the bot.
    /sendaf - Send a reply message or file using "/sendaf" command.
    /edit - Edit a label.
    /sendall - Send a message to all users.
    /send - Send a message to a specific user by ID or username.
    /save or // - Save a message or file with a label.
    /savel - Save a message or file with a label for later use.
    /get or / - Retrieve a saved message or file by label.
    /remove - Remove a saved label and associated message/file.
    /sendallt - Send a message with a label to all users.
    /gettime - Get the time of a country.
    /alarm - Set an alarm.
    
    To use these commands, simply type them in the chat.
    """

    # List of commands that users can choose from
    command_list = [
        "/start",
        "/sendaf",
        "/edit",
        "/sendall",
        "/send",
        "/save or //",
        "/savel",
        "/get or /",
        "/remove",
        "/sendallt",
        "/gettime",
        "/alarm"
    ]

    # Create an inline keyboard to display the commands
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    # Add each command as a button within the keyboard
    for command in command_list:
        markup.add(types.KeyboardButton(command))

    bot.reply_to(message, help_text, reply_markup=markup)


@bot.message_handler(commands=['gettime'])
def get_current_time(message):
    try:
        # Check if the user specified a country
        if len(message.text.split()) < 2:
            bot.reply_to(
                message, "Please specify a country. For example, /gettime USA")
            return

        # Extract the country name from the message
        country = message.text.split(' ', 1)[1].strip()

        # Check if the specified country is in the dictionary
        if country in country_timezones:
            # Get the timezone for the specified country
            timezone = country_timezones[country]

            # Get the current time in the specified timezone
            current_time = datetime.datetime.now(timezone).strftime("%H:%M:%S")

            # Send the current time as a message
            bot.reply_to(message, f"Current Time in {country}: {current_time}")
        else:
            bot.reply_to(
                message, f"Timezone information for {country} is not available.")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


@bot.message_handler(commands=['alarm'])
def set_alarm(message):
    try:
        # Split the command text to get day, month, and time
        command_parts = message.text.split(' ', 1)
        if len(command_parts) < 2:
            bot.reply_to(
                message, "Please use the format /alarm day.month hour:min")
            return

        _, alarm_data = command_parts
        alarm_data = alarm_data.split()

        if len(alarm_data) != 3:
            bot.reply_to(
                message, "Invalid format. Please use /alarm day month hour:min 24 format")
            return

        day, month, time = alarm_data
        hour, minute = map(int, time.split(':'))

        # Create a datetime object for the alarm
        now = datetime.datetime.now()
        alarm_datetime = datetime.datetime(year=now.year, month=int(
            month), day=int(day), hour=hour, minute=minute)
        # Calculate the time until the alarm
        time_difference = alarm_datetime - now
        seconds_until_alarm = time_difference.total_seconds()
        if seconds_until_alarm <= 0:
            bot.reply_to(message, "Please choose a future time for the alarm.")
            return

        # Store the alarm for the user
        user_id = message.from_user.id
        user_alarms[user_id] = alarm_datetime

        bot.reply_to(
            message, f"Alarm set for {alarm_datetime.strftime('%A, %d %B %Y, %H:%M:%S')}")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


def check_alarms():
    now = datetime.datetime.now()
    for user_id, alarm_time in user_alarms.copy().items():
        if now >= alarm_time:
            bot.send_message(user_id, "Time to answer your call!")
            del user_alarms[user_id]

# Define a function to run the bot


def run_bot():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Bot polling error: {str(e)}")
            time.sleep(5)

# Define a function to schedule alarm checks


def schedule_alarms():
    schedule.every(1).minutes.do(check_alarms)
    while True:
        schedule.run_pending()
        time.sleep(1)


# Create threads for running the bot and scheduling alarms
bot_thread = threading.Thread(target=run_bot)
schedule_thread = threading.Thread(target=schedule_alarms)


# # Function to download a YouTube video
# def download_youtube_video(url, quality):
#     try:
#         download_command = f"youtube-dl -f {quality} -o '%(title)s.%(ext)s' {url}"
#         process = subprocess.Popen(
#             download_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#         # Wait for the download to finish
#         stdout, stderr = process.communicate()

#         if process.returncode == 0:
#             # Video downloaded successfully
#             return f"{stdout.strip().decode()}"
#         else:
#             # An error occurred during the download
#             return f"Error: {stderr.strip().decode()}"

#     except Exception as e:
#         return str(e)


# @bot.message_handler(commands=['y'])
# def handle_youtube_download(message):
#     try:
#         # Get the YouTube link and quality from the message
#         command_parts = message.text.split(' ', 2)
#         if len(command_parts) < 3:
#             bot.reply_to(message, "Usage: /y [YouTube link] [quality]")
#             return

#         url = command_parts[1].strip()
#         quality = command_parts[2].strip()

#         # Download the video with the specified quality
#         download_result = download_youtube_video(url, quality)

#         # Check if the result is a filename (successful download) or an error message
#         if download_result.endswith(".mp4"):
#             # Send the downloaded video file to the user
#             with open(download_result, 'rb') as video_file:
#                 bot.send_video(message.chat.id, video_file)

#             # Remove the downloaded file from the server
#             subprocess.run(["rm", download_result])
#         else:
#             # Send the error message to the user
#             bot.reply_to(message, download_result)

#     except Exception as e:
#         bot.reply_to(message, f"Error: {str(e)}")


# @bot.message_handler(commands=['wiki'])
# def search_wikipedia(message):
#     try:
#         # Initialize the Wikipedia API with a proper user agent
#         wiki_wiki = wikipediaapi.Wikipedia(
#             language='en',
#             extract_format=wikipediaapi.ExtractFormat.WIKI
#         )

#         # Extract the article name from the message text
#         article_name = message.text.replace('/wiki', '').strip()

#         # Use the Wikipedia API to fetch the article
#         page = wiki_wiki.page(article_name)

#         if page.exists():
#             # Send the entire article as a message
#             bot.send_message(message.chat.id, page.text)
#         else:
#             bot.send_message(message.chat.id, "Article not found.")

#     except Exception as e:
#         bot.send_message(message.chat.id, f"An error occurred: {str(e)}")


@bot.message_handler(commands=['sendaf'])
def send_file_or_message_in_response(message):
    if message.reply_to_message:
        replied_message = message.reply_to_message
        for id in user_ids.keys():
            if id == str(message.from_user.id):
                continue
            else:
                if replied_message.document:
                    # If the replied message is a document, send the document
                    file_info = replied_message.document
                    file_id = file_info.file_id
                    bot.send_document(id, file_id)
                elif replied_message.photo:
                    # If the replied message is a photo, send the photo
                    # Get the highest quality photo
                    file_id = replied_message.photo[-1].file_id
                    bot.send_photo(id, file_id)
                elif replied_message.video:
                    # If the replied message is a video, send the video
                    file_info = replied_message.video
                    file_id = file_info.file_id
                    bot.send_video(id, file_id)
                elif replied_message.voice:
                    # If the replied message is a video, send the video
                    file_info = replied_message.voice
                    file_id = file_info.file_id
                    bot.send_voice(id, file_id)
                elif replied_message.text:
                    # If the replied message is text, send the text as a message
                    text_to_send = replied_message.text
                    bot.send_message(id, text_to_send)
                else:
                    # If the replied message is none of the above, inform the user
                    bot.reply_to(
                        message, "Please reply with a document, photo, video, or text to use /sendaf.")
    else:
        # If there is no replied message, inform the user
        bot.reply_to(
            message, "Please reply with a document, photo, video, or text to use /sendaf.")


@bot.message_handler(commands=['edit'])
def edit_lable(message):
    try:
        _, old_lable, new_lable = [text.strip()
                                   for text in message.text.split(' ', 2)]

        if old_lable in message_dict:
            user_id = message.from_user.id
            if user_id in user_labels and old_lable in user_labels[user_id]:
                user_labels[user_id][new_lable] = user_labels[user_id][old_lable]
                message_dict[new_lable] = message_dict[old_lable]
            else:
                message_dict[new_lable] = message_dict[old_lable]

            message.text = '/remove ' + old_lable
            remove_label(message, 1)
            with open(db_file, 'w') as file:
                json.dump(message_dict, file, indent=4)
            bot.reply_to(message, "Edit done.")
        else:
            bot.reply_to(message, "Lable not found.")
    except ValueError:
        bot.reply_to(message, "You have to write something.")

# send a message to id


@bot.message_handler(commands=['sendat'])
def send_message_all(message, s=0):
    try:
        _, msg = [text.strip() for text in message.text.split(' ', 1)]
        for id in user_ids.keys():
            if id == str(message.from_user.id):
                continue
            else:
                bot.send_message(id, msg)
        if s == 0:
            bot.reply_to(message, "Message had sent to all.")
    except ValueError:
        bot.reply_to(message, "You have to write something.")


@bot.message_handler(commands=['sendal'])
def send_message_tag(message, s=0):
    try:
        label = message.text.split(' ', 1)[1].strip()
        if label in message_dict:
            message_text = message_dict[label]
            if message_text.startswith('file_id:'):
                # It's a saved file, send the file by its ID
                file_id = message_text.replace('file_id:', '')

                for id in user_ids.keys():
                    if id == str(message.from_user.id):
                        continue
                    else:
                        bot.send_document(id, file_id)
                if s == 0:
                    bot.reply_to(message, "Message had sent to all.")
            elif message_text.startswith('photo_id:'):
                # It's a saved file, send the file by its ID
                photo_id = message_text.replace('photo_id:', '')

                for id in user_ids.keys():
                    if id == str(message.from_user.id):
                        continue
                    else:
                        bot.send_photo(id, photo_id)
                if s == 0:
                    bot.reply_to(message, "Message had sent to all.")
            else:

                for id in user_ids.keys():
                    if id == str(message.from_user.id):
                        continue
                    else:
                        bot.send_message(id, message_text)
                if s == 0:
                    bot.reply_to(message, "Message had sent to all.")

    except IndexError:
        bot.reply_to(message, "You have to write something.")


@bot.message_handler(commands=['send'])
def send_message(message, s=0):
    try:
        if message.reply_to_message:
            _, id = [text.strip() for text in message.text.split(' ', 1)]
            msg = message.reply_to_message.text
            if id in user_ids.keys():
                bot.send_message(id, msg)
            elif id in user_ids.values():
                for key, value in user_ids.items():
                    if value == id:
                        bot.send_message(key, msg)
                        if s == 0:
                            bot.reply_to(message, "Done.")
            else:
                bot.reply_to(message, "Wrong ID")
        else:
            _, id, msg = [text.strip() for text in message.text.split(' ', 2)]
            if id in user_ids.keys():
                bot.send_message(id, msg)
            elif id in user_ids.values():
                for key, value in user_ids.items():
                    if value == id:
                        bot.send_message(key, msg)
                        if s == 0:
                            bot.reply_to(message, "Done.")
            else:
                bot.reply_to(message, "Wrong ID")

    except ValueError:
        bot.reply_to(
            message, "You have to write something or message selected.")


# Handle the /save command for text messages and files


@bot.message_handler(commands=['save', '//'])
def save_messageG(message, s=0):
    if message.reply_to_message:
        if message.reply_to_message.text:
            original_message = message.reply_to_message.text
            label = message.text.split(' ', 1)[1].strip()
            if label_exists(label):
                bot.reply_to(message, "This lable is used by someone.")
                return
            else:
                pass
            # Save the original text message with the label
            message_dict[label] = original_message

            with open(db_file, 'w') as file:
                json.dump(message_dict, file, indent=4)
            if s == 0:
                bot.reply_to(
                    message, f'Text message with label "{label}" saved successfully!')
        elif message.reply_to_message.document:
            file_info = message.reply_to_message.document
            label = message.text.split(' ', 1)[1].strip()
            file_id = file_info.file_id

            # Save the file ID with the label
            message_dict[label] = f'file_id:{file_id}'

            with open(db_file, 'w') as file:
                json.dump(message_dict, file, indent=4)
            if s == 0:
                bot.reply_to(
                    message, f'File with label "{label}" saved successfully!')
        elif message.reply_to_message.photo:
            # Get the last (highest resolution) photo
            file_info = message.reply_to_message.photo[-1]
            label = message.text.split(' ', 1)[1].strip()
            file_id = file_info.file_id

            # Save the file ID with the label
            message_dict[label] = f'photo_id:{file_id}'

            with open(db_file, 'w') as file:
                json.dump(message_dict, file, indent=4)
            if s == 0:
                bot.reply_to(
                    message, f'Photo with label "{label}" saved successfully!')
        elif message.reply_to_message.video:
            video = message.reply_to_message.video
            label = message.text.split(' ', 1)[1].strip()
            file_id = video.file_id

            # Save the file ID with the label
            message_dict[label] = f'video_id:{file_id}'

            with open(db_file, 'w') as file:
                json.dump(message_dict, file, indent=4)
            if s == 0:
                bot.reply_to(
                    message, f'Video with label "{label}" saved successfully!')
        elif message.reply_to_message.voice:
            voice = message.reply_to_message.voice
            label = message.text.split(' ', 1)[1].strip()
            file_id = voice.file_id

            # Save the file ID with the label
            message_dict[label] = f'voice_id:{file_id}'

            with open(db_file, 'w') as file:
                json.dump(message_dict, file, indent=4)
            if s == 0:
                bot.reply_to(
                    message, f'voice with label "{label}" saved successfully!')
        else:
            bot.reply_to(
                message, "To save a message or file, reply to it with the desired label.")
    else:
        bot.reply_to(
            message, "To save a message or file, reply to it with the desired label.")
    save_messageL(message, 1)


@bot.message_handler(commands=['savel'])
def save_messageL(message, s=0):
    if message.reply_to_message:
        original_message = message.reply_to_message
        label = message.text.split(' ', 1)[1].strip()
        user_id = message.from_user.id

        # Check if the user has used this label before
        if user_id not in user_labels:
            user_labels[user_id] = {}

        # Save the message ID with the label for the user
        user_labels[user_id][label] = original_message.message_id

        # Save the message text or file ID with the label
        if original_message.text:
            message_dict[original_message.message_id] = original_message.text
        elif original_message.document:
            file_info = original_message.document
            file_id = file_info.file_id
            message_dict[original_message.message_id] = f'file_id:{file_id}'
        elif original_message.photo:
            # Get the last (highest resolution) photo
            file_info = original_message.photo[-1]
            file_id = file_info.file_id
            label = message.text.split(' ', 1)[1].strip()
            message_dict[original_message.message_id] = f'photo_id:{file_id}'
        elif original_message.video:
            # Get the last (highest resolution) video
            video = original_message.video
            file_id = video.file_id
            label = message.text.split(' ', 1)[1].strip()

            message_dict[original_message.message_id] = f'video_id:{file_id}'
        # Save the user labels and messages to the database file
        elif original_message.voice:
            # Get the last (highest resolution) video
            voice = original_message.voice
            file_id = voice.file_id
            label = message.text.split(' ', 1)[1].strip()

            message_dict[original_message.message_id] = f'voice_id:{file_id}'
        # Save the user labels and messages to the database file
        with open(db_file, 'w') as file:
            json.dump(message_dict, file, indent=4)
        if s == 0:
            bot.reply_to(
                message, f'Message with label "{label}" saved successfully!')

    else:
        bot.reply_to(
            message, "To save a message or file, reply to it with the desired label.")


# Handle the command to retrieve a saved message by label

@bot.message_handler(commands=['get', '/'])
def retrieve_messageG(message):
    try:
        label = message.text.split(' ', 1)[1].strip()
        if label in message_dict:
            message_text = message_dict[label]
            if message_text.startswith('file_id:'):
                # It's a saved file, send the file by its ID
                file_id = message_text.replace('file_id:', '')
                bot.send_document(message.chat.id, file_id)
            elif message_text.startswith('photo_id:'):
                # It's a saved file, send the file by its ID
                photo_id = message_text.replace('photo_id:', '')
                bot.send_photo(message.chat.id, photo_id)
            elif message_text.startswith('video_id:'):
                # It's a saved file, send the file by its ID
                video_id = message_text.replace('video_id:', '')
                bot.send_video(message.chat.id, video_id)
            elif message_text.startswith('voice_id:'):
                # It's a saved file, send the file by its ID
                voice_id = message_text.replace('voice_id:', '')
                bot.send_voice(message.chat.id, voice_id)
            else:
                bot.reply_to(
                    message, f'\n{message_text}')
        else:
            retrieve_messageL(message)
    except IndexError:
        bot.reply_to(message, "Write a lable to get.")


@bot.message_handler(commands=['getl'])
def retrieve_messageL(message):
    try:
        label = message.text.split(' ', 1)[1].strip()
        user_id = message.from_user.id

        # Check if the user has used this label
        if user_id in user_labels and label in user_labels[user_id]:
            message_id = user_labels[user_id][label]
            if message_id in message_dict:
                message_text = message_dict[message_id]
                if message_text.startswith('file_id:'):
                    file_id = message_text.replace('file_id:', '')
                    bot.send_document(message.chat.id, file_id)
                elif message_text.startswith('photo_id:'):
                    photo_id = message_text.replace('photo_id:', '')
                    bot.send_photo(message.chat.id, photo_id)
                elif message_text.startswith('video_id:'):
                    video_id = message_text.replace('video_id:', '')
                    bot.send_video(message.chat.id, video_id)
                elif message_text.startswith('voice_id:'):
                    voice_id = message_text.replace('voice_id:', '')
                    bot.send_voice(message.chat.id, voice_id)
                else:
                    bot.reply_to(message, f'\n{message_text}')
            else:
                bot.reply_to(message, f'Label "{label}" not found.')
        else:
            bot.reply_to(message, f'You have not used label "{label}".')
    except IndexError:
        bot.reply_to(message, "Write a lable to get.")


@bot.message_handler(commands=['remove'])
def remove_label(message, s=0):
    try:
        label = message.text.split(' ', 1)[1].strip()
        user_id = message.from_user.id
        # Check if the user has used this label before
        if user_id in user_labels and label in user_labels[user_id]:

            message_id = message_dict[label]
            del message_dict[label]
            if message_id in message_dict:
                del message_dict[message_id]

                # Save the user labels and messages to the database file
                with open(db_file, 'w') as file:
                    json.dump(message_dict, file, indent=4)

            message_id = user_labels[user_id][label]

            # Remove the label from the user's labels
            del user_labels[user_id][label]

            # Check if the message is still associated with any other labels
            if message_id not in [v for labels in user_labels.values() for v in labels.values()]:
                # If not, remove the message from the main message_dict
                if message_id in message_dict:
                    del message_dict[message_id]

                # Save the user labels and messages to the database file
                with open(db_file, 'w') as file:
                    json.dump(message_dict, file, indent=4)
                if s == 0:
                    bot.reply_to(
                        message, f'Label "{label}" removed successfully!')

        else:
            bot.reply_to(
                message, f'Label "{label}" not created by you.')
            return
    except IndexError:
        bot.reply_to(message, "Write a lable to remove.")


# Start the bot
bot.infinity_polling()
# schedule_thread.start()
