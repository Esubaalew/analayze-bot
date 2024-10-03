import os
import time
import schedule
import logging
from datetime import datetime, timedelta
from os import getenv
from telegram.constants import ChatAction
from telegram import Update, ChatMember, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# Adjust imports from your 'bott' package (assuming this is your package)
from bott.analyzer.tools import (
    load_json,
    chat_info,
    get_oldest_message,
    get_latest_message,
    get_senders,
    get_forwarders,
    count_forwarded_messages,
    get_forward_sources,
    count_replies,
    get_repliers,
    get_editors,
    count_edited_messages,
    get_most_common_words,
    get_most_active_hours,
    get_most_active_weekdays,
    get_most_active_months,
    get_most_active_year,
    get_most_active_months_all_time,
    get_most_active_months_by_year
)

# Visualization imports
from bott.analyzer.visuals.active_senders import (
    visualize_bar_chart,
    visualize_pie_chart,
    visualize_area_chart,
    visualize_line__chart,
    visualize_vertical_chart
)

from bott.analyzer.visuals.active_weekdays import (
    visualize_most_active_weekdays_bar,
    visualize_most_active_weekdays_pie
)

from bott.analyzer.visuals.forwarders import (
    visualize_forwarders_vertical_bar_chart,
    visualize_forwarders_bar_chart,
    visualize_forwarders_line_chart,
    visualize_forwarders_pie_chart,
    visualize_forwarders_area_chart
)

from bott.analyzer.visuals.repliers import (
    visualize_bar_chart_repliers,
    visualize_vertical_bar_chart_repliers,
    visualize_pie_chart_repliers,
    visualize_area_chart_repliers,
    visualize_line_chart_repliers
)

from bott.analyzer.visuals.editors import (
    visualize_pie_chart_editors,
    visualize_vertical_bar_chart_editors,
    visualize_bar_chart_editors,
    visualize_area_chart_editors,
    visualize_line_chart_editors
)

# Other visuals imports
from bott.analyzer.visuals.forward_sources import *
from bott.analyzer.visuals.common_words import visualize_most_common_words
from bott.analyzer.visuals.active_hours import *
from bott.analyzer.visuals.active_months import *
from bott.analyzer.visuals.active_years import *


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

CHANNEL_USERNAME = "@esubalewbots"

def delete_json_files():
    directory = "."
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            os.remove(os.path.join(directory, filename))
            print(f"Deleted file: {filename}")
async def send_join_channel_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    button = InlineKeyboardButton("Join Channel", url="https://t.me/esubalewbots")
    keyboard = [[button]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text="To use this bot, please join our channel:",
        reply_markup=reply_markup
    )
async def check_user_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        user_status = chat_member.status

        return user_status

    except BadRequest as e:
        print(f"Error: {e}")
        return "error"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_first_name = update.effective_user.first_name

    tools_list = [
        "1. Chat Info",
        "2. Oldest Message",
        "3. Latest Message",
        "4. Rank Senders",
        "5. Rank Forwarders",
        "6. Forward Sources",
        "7. Rank Repliers",
        "8. Rank Editors",
        "9. Common Words",
        "10. Active Hours",
        "11. Active Weekdays",
        "12. Active Months",
        "13. Active Years",
        "14. Months All Time",
        "15. Months By Year"
    ]

    tools_message = "\n".join(tools_list)

    await update.message.reply_text(
        f'Hello {user_first_name}, I am Liyu Bot, a Telegram chat analytics bot.\n'
        f'You can use the following tools to analyze and visualize the Telegram groups:\n'
        f'{tools_message}\n' + 'Start by sending a JSON file.'
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "Go to any of your **Telegram groups** or *personal chats* on your desktop, and export the chat history "
        "as a JSON file\\. "
        "Then, send the JSON file to the bot and choose the functionality you want to perform\\."
    )
    await update.message.reply_text(message, parse_mode='MarkdownV2')

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Sorry, I didn't understand that command.")

async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Sorry, I didn't understand that text.")


async def filter_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I guess this pic is good. Please send a JSON file instead.")


async def filter_videos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("What is this video? Please send a JSON file instead.")


async def filter_audios(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Audio, yeah? Please send a JSON file instead.")


async def filter_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("This might be your voice ah? Please send a JSON file instead.")


async def filter_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Please send a JSON file instead; I guess this is your location.")


async def filter_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("OH!! Is this your contact? Please send a JSON file instead.")


async def filter_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("What is this sticker? Please send a JSON file instead.")


async def visualize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Please send a JSON file to visualize the data. You can export the chat history as a "
        "JSON file from your Telegram desktop."
    )


async def filter_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("A poll? Please send a JSON file instead.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    user_status = await check_user_status(update, context)  # Ensure this function is also async
    if user_status == "error":
        await update.message.reply_text("An error occurred. Please try again later.")
        return
    if user_status not in [
        ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR
    ]:
        await update.message.reply_text(
            f"Your current status: {user_status}\nPlease join {CHANNEL_USERNAME} before using the bot."
        )
        await send_join_channel_button(update.message.chat_id, context)  # Make sure this is also async
        return
    
    document = update.message.document
    if document.file_size > 20971520:  # 20 MB, Telegram's file size limit
        await update.message.reply_text("The file size exceeds the limit. Please upload a file smaller than 20 MB.")
        return

    if document.mime_type == 'application/json':
        file_id = document.file_id
        file = await context.bot.get_file(file_id)  # Await the get_file call
        file_path = await file.download()  # Await the download call
        data = load_json(file_path)
        
        if data:
            buttons = [
                InlineKeyboardButton("ChatInfo", callback_data='chat_info'),
                InlineKeyboardButton("OldestMessage", callback_data='oldest_message'),
                InlineKeyboardButton("LatestMessage", callback_data='latest_message'),
                InlineKeyboardButton("RankSenders", callback_data='rank_senders'),
                InlineKeyboardButton("RankForwarders", callback_data='rank_forwarders'),
                InlineKeyboardButton("ForwardSources", callback_data='forward_sources'),
                InlineKeyboardButton("RankRepliers", callback_data='rank_repliers'),
                InlineKeyboardButton("RankEditors", callback_data='rank_editors'),
                InlineKeyboardButton("CommonWords", callback_data='most_common_words'),
                InlineKeyboardButton("ActiveHours", callback_data='most_active_hours'),
                InlineKeyboardButton("ActiveWeekdays", callback_data='most_active_weekdays'),
                InlineKeyboardButton("ActiveMonths", callback_data='most_active_months'),
                InlineKeyboardButton("ActiveYears", callback_data='most_active_year'),
                InlineKeyboardButton("MonthsAllTime", callback_data='most_active_months_all_time'),
                InlineKeyboardButton("MonthsByYear", callback_data='most_active_months_by_year')
            ]

            keyboard = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('Please select a functionality:', reply_markup=reply_markup)
            context.user_data['file_path'] = file_path
        else:
            await update.message.reply_text("Failed to process the JSON file.")
    else:
        await update.message.reply_text("Only JSON files are supported. Please send a JSON file.")

async def button_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_status = await check_user_status(update, context)
    if user_status == "error":
        await update.message.reply_text("An error occurred. Please try again later.")
        return
    if user_status not in [
      ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.CREATOR
  ]:
      await update.message.reply_text(
      f"Your current status: {user_status}\nPlease join {CHANNEL_USERNAME} before using the bot."
    )
      await send_join_channel_button(update.message.chat_id, context)
      return
    query = await update.callback_query
    query.answer()
    file_names = []
    if query.data == 'chat_info':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                chat_info_dict = chat_info(data)
                chat_info_text = (
                    f"Chat Name: {chat_info_dict['name']}\n"
                    f"Chat Type: {chat_info_dict['type']}\n"
                    f"Chat ID: {chat_info_dict['id']}\n"
                    f"Messages Count: {chat_info_dict['messages_count']}"
                )
                await query.message.reply_text(chat_info_text)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'oldest_message':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                oldest_date = get_oldest_message(data)['date']
                formatted_date = f"{oldest_date['day']}/{oldest_date['month']}/{oldest_date['year']}"
                await query.message.reply_text(f"The oldest message in the chat was sent on {formatted_date}.")
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'latest_message':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                latest_date = get_latest_message(data)['date']
                formatted_date = f"{latest_date['day']}/{latest_date['month']}/{latest_date['year']}"
                await query.message.reply_text(f"The latest message in the chat was sent on {formatted_date}.")
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'rank_senders':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                senders = get_senders(data)[:100]
                senders_text = "Rank of Top 100 Senders:\n"
                for index, sender in enumerate(senders, start=1):
                    senders_text += f"{index}. {sender['sender']} - Messages: {sender['messages']}\n"
                keyboard = [
                    [InlineKeyboardButton("Visualize Senders", callback_data='visualize_senders')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(senders_text, reply_markup=reply_markup, )

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'rank_forwarders':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                all_forwarders = count_forwarded_messages(data)
                forwarders = get_forwarders(data)
                forwarders_text = "Rank of Top 100 Forwarders:\n"
                for index, (forwarder, count) in enumerate(forwarders.items(), start=1):
                    forwarders_text += f"{index}. {forwarder} - FMessages: {count}\n"
                reply_text = f"Total forwarded messages: {all_forwarders}\n\n{forwarders_text}"
                keyboard = [
                    [InlineKeyboardButton("Visualize Forwarders", callback_data='visualize_forwarders')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(reply_text, reply_markup=reply_markup, )

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'forward_sources':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                forward_sources = get_forward_sources(data)
                forward_sources_text = "Rank of Top 100  Forward Sources:\n"
                for index, (forward_source, count) in enumerate(forward_sources.items(), start=1):
                    forward_sources_text += f"{index}. {forward_source} - FMessages: {count}\n"
                keyboard = [
                    [InlineKeyboardButton("Visualize Sources", callback_data='visualize_sources')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(forward_sources_text, reply_markup=reply_markup, )

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'rank_repliers':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                total_repliers = count_replies(data)
                repliers_ranking = get_repliers(data)
                repliers_text = f"Total replies: {total_repliers}\n\nRank of Top 100  Repliers:\n"
                for index, (replier, count) in enumerate(repliers_ranking.items(), start=1):
                    repliers_text += f"{index}. {replier} - Replies: {count}\n"

                keyboard = [
                    [InlineKeyboardButton("Visualize Repliers", callback_data='visualize_repliers')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(repliers_text, reply_markup=reply_markup, )

            else:
                query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'rank_editors':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                total_edited_messages = count_edited_messages(data)
                editors_ranking = get_editors(data)
                editors_text = f"Total edited messages: {total_edited_messages}\n\nRank of Top 100  Editors:\n"
                for index, (editor, count) in enumerate(editors_ranking.items(), start=1):
                    editors_text += f"{index}. {editor} - Edits: {count}\n"

                keyboard = [
                    [InlineKeyboardButton("Visualize Editors", callback_data='visualize_editors')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(editors_text, reply_markup=reply_markup)

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'most_common_words':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                most_common_words_list = get_most_common_words(data)
                words_text = "Top 10 most common words:\n"
                words_text += "{:<3} {:<15} {:<10}\n".format("No.", "Word", "Occurrence")
                for index, word_info in enumerate(most_common_words_list, start=1):
                    words_text += f"{index:<3} {word_info['word']:<15} {word_info['occurrence']:<10}\n"

                keyboard = [
                    [InlineKeyboardButton("Visualize Words", callback_data='visualize_words')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(words_text, reply_markup=reply_markup)


            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'most_active_hours':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                active_hours = get_most_active_hours(data)
                hours, counts = zip(*active_hours)
                ethiopian_hours = [(datetime.strptime(str(hour), '%H') + timedelta(hours=3)).strftime('%I %p') for hour
                                   in hours]

                hours_text = "Most active hours:\n"
                for rank, (hour, count) in enumerate(zip(ethiopian_hours, counts), start=1):
                    hours_text += f"{rank}. {hour}: {count} Messages\n"
                keyboard = [
                    [InlineKeyboardButton("Visualize Hours", callback_data='visualize_hours')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(hours_text, reply_markup=reply_markup, )

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'most_active_weekdays':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                active_weekdays = get_most_active_weekdays(data)

                weekdays_text = "Most active weekdays:\n\n"
                for weekday, count in active_weekdays:
                    weekdays_text += f"{weekday}: {count} Messages\n"
                keyboard = [
                    [InlineKeyboardButton("Visualize Weekdays", callback_data='visualize_weekdays')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(weekdays_text, reply_markup=reply_markup, )

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'most_active_months':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                active_months = get_most_active_months(data)

                active_months = active_months[:100]

                months_text = "Most active months:\n\n"
                for month, count in active_months:
                    months_text += f"{month}: {count} Messages\n"
                keyboard = [
                    [InlineKeyboardButton("Visualize Months", callback_data='visualize_months')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(months_text, reply_markup=reply_markup, )

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'most_active_year':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                active_years = get_most_active_year(data)

                active_years = active_years[:100]

                years_text = "Most active years:\n\n"
                for year, count in active_years:
                    years_text += f"{year}: {count} Messages\n"

                keyboard = [
                    [InlineKeyboardButton("Visualize Years", callback_data='visualize_years')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.message.reply_text(years_text, reply_markup=reply_markup, )
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'most_active_months_all_time':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                active_months_list = get_most_active_months_all_time(data)

                months_text = "Most active months of all time:\n"
                for index, month_info in enumerate(active_months_list, start=1):
                    months_text += f"{index}. {month_info['name']}: {month_info['messages']}\n"

                keyboard = [
                    [InlineKeyboardButton("Visualize AllTimeMonths", callback_data='visualize_months_all')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(months_text, reply_markup=reply_markup, )
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'most_active_months_by_year':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                active_months_by_year = get_most_active_months_by_year(data)

                response_text = "Most active months by year:\n"
                for year, months in active_months_by_year.items():
                    response_text += f"\n{year}:\n"
                    for index, month_info in enumerate(months, start=1):
                        response_text += f"    {index}. {month_info['name']}: {month_info['messages']}\n"
                keyboard = [
                    [InlineKeyboardButton("Visualize MonthsByYear", callback_data='visualize_months_year')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text(response_text, reply_markup=reply_markup)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'visualize_senders':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                bar_chart_file = visualize_bar_chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='Top 10 most active users based on the number of messages they sent.')
                os.remove(bar_chart_file)
                pie_chart_file = visualize_pie_chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(pie_chart_file, 'rb'),
                    caption='Proportion of messages sent by each sender using a pie chart.')
                os.remove(pie_chart_file)
                area_chart_file = visualize_area_chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(area_chart_file, 'rb'),
                    caption='Area chart ')
                os.remove(area_chart_file)
                line_chart_file = visualize_line__chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(line_chart_file, 'rb'), )
                os.remove(line_chart_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'visualize_weekdays':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                bar_chart_file = visualize_most_active_weekdays_bar(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='The most active weekdays bar chart.')
                os.remove(bar_chart_file)
                pie_chart_file = visualize_most_active_weekdays_pie(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(pie_chart_file, 'rb'),
                    caption='The most active weekdays pie chart.')
                os.remove(pie_chart_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'visualize_forwarders':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                bar_chart_file = visualize_forwarders_bar_chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='The most active forwarders bar chart.')
                os.remove(bar_chart_file)
                pie_chart_file = visualize_forwarders_pie_chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(pie_chart_file, 'rb'),
                    caption='The most active forwarders pie chart.')
                os.remove(pie_chart_file)
                line_chart_file = visualize_forwarders_line_chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(line_chart_file, 'rb'),
                    caption='The most active forwarders line chart.')
                os.remove(line_chart_file)

                vertical_chart_file = visualize_forwarders_vertical_bar_chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(vertical_chart_file, 'rb'),
                    caption='The most active forwarders vertical bar chart.')
                os.remove(vertical_chart_file)

                area_chart_file = visualize_forwarders_area_chart(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(area_chart_file, 'rb'),
                    caption='The most active forwarders area chart.')
                os.remove(area_chart_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'visualize_repliers':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                bar_chart_file = visualize_bar_chart_repliers(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='The most active repliers bar chart.')
                os.remove(bar_chart_file)

                pie_chart_file = visualize_pie_chart_repliers(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(pie_chart_file, 'rb'),
                    caption='The most active repliers pie chart.')
                os.remove(pie_chart_file)

                line_chart_file = visualize_line_chart_repliers(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(line_chart_file, 'rb'),
                    caption='The most active repliers line chart.')
                os.remove(line_chart_file)

                vertical_chart_file = visualize_vertical_bar_chart_repliers(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(vertical_chart_file, 'rb'),
                    caption='The most active repliers vertical bar chart.')
                os.remove(vertical_chart_file)

                area_chart_file = visualize_area_chart_repliers(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(area_chart_file, 'rb'),
                    caption='The most active repliers area chart.')
                os.remove(area_chart_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'visualize_editors':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                bar_chart_file = visualize_bar_chart_editors(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='The most active editors bar chart.')
                os.remove(bar_chart_file)

                pie_chart_file = visualize_pie_chart_editors(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(pie_chart_file, 'rb'),
                    caption='The most active editors pie chart.')
                os.remove(pie_chart_file)

                line_chart_file = visualize_line_chart_editors(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(line_chart_file, 'rb'),
                    caption='The most active editors line chart.')
                os.remove(line_chart_file)

                vertical_chart_file = visualize_vertical_bar_chart_editors(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(vertical_chart_file, 'rb'),
                    caption='The most active editors vertical bar chart.')
                os.remove(vertical_chart_file)

                area_chart_file = visualize_area_chart_editors(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(area_chart_file, 'rb'),
                    caption='The most active editors area chart.')
                os.remove(area_chart_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'visualize_sources':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                bar_chart_file = visualize_bar_chart_sources(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='Top forward sources bar chart based on the number of messages they sent.')
                os.remove(bar_chart_file)

                pie_chart_file = visualize_pie_chart_sources(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(pie_chart_file, 'rb'),
                    caption='Proportion of messages forward sources  using a pie chart.')
                os.remove(pie_chart_file)

                area_chart_file = visualize_area_chart_sources(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(area_chart_file, 'rb'),
                    caption='Area chart ')
                os.remove(area_chart_file)

                line_chart_file = visualize_line_chart_sources(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(line_chart_file, 'rb'), )
                os.remove(line_chart_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'visualize_words':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                bar_chart_file = visualize_most_common_words(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='Top 10 most common words in the chat.')
                os.remove(bar_chart_file)

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")
    elif query.data == 'visualize_hours':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                bar_chart_file = visualize_bar_hours(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='Active hours bar chart.')
                os.remove(bar_chart_file)

                line_chart_file = visualize_line_hours(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(line_chart_file, 'rb'), caption='Active hours line chart.')
                os.remove(line_chart_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'visualize_months':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:
                months_trend_file = visualize_most_active_months_trend(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(months_trend_file, 'rb'), caption='Active months trend chart.')
                os.remove(months_trend_file)

                top_10_months_file = visualize_top_10_most_active_months(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(top_10_months_file, 'rb'), caption='Top 10 most active months.')
                os.remove(top_10_months_file)

            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'visualize_months_year':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:

                months_per_year_file = visualize_most_active_months_by_year(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(months_per_year_file, 'rb'), caption='Active months by year.')
                os.remove(months_per_year_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'visualize_months_all':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:

                bar_chart_file = visualize_bar_chart_months(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(bar_chart_file, 'rb'),
                    caption='Active months bar chart.')
                os.remove(bar_chart_file)

                line_chart_file = visualize_line_chart_months(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(line_chart_file, 'rb'), caption='Active months line chart.')
                os.remove(line_chart_file)

                pie_chart_file = visualize_pie_chart_months(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(pie_chart_file, 'rb'), caption='Active months pie chart.')
                os.remove(pie_chart_file)

                area_chart_file = visualize_area_chart_months(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(area_chart_file, 'rb'), caption='Active months area chart.')
                os.remove(area_chart_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    elif query.data == 'visualize_years':
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
        file_path = context.user_data.get('file_path')
        if file_path:
            data = load_json(file_path)
            if data:

                trend_chart_year = visualize_message_trend_over_year(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(trend_chart_year, 'rb'),
                    caption='Active years bar chart.')
                os.remove(trend_chart_year)

                trend_bar_file = visualize_message_trend_over_year_bar(data)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(trend_bar_file, 'rb'), caption='Active years bar chart.')
                os.remove(trend_bar_file)
            else:
                await query.message.reply_text("Failed to process the JSON file.")
        else:
            await query.message.reply_text("No JSON file found.")

    else:
        await query.message.reply_text("Invalid option selected.")
    

async def bot_tele(text):
    # Create application
    application = (
        Application.builder().token(os.getenv('TOKEN')).build()
    )

    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('visualize', visualize))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, filter_photos))
    application.add_handler(MessageHandler(filters.VIDEO, filter_videos))
    application.add_handler(MessageHandler(filters.AUDIO, filter_audios))
    application.add_handler(MessageHandler(filters.VOICE, filter_voice))
    application.add_handler(MessageHandler(filters.LOCATION, filter_location))
    application.add_handler(MessageHandler(filters.CONTACT, filter_contact))
    application.add_handler(MessageHandler(filters.Sticker.ALL, filter_sticker))
    application.add_handler(MessageHandler(filters.POLL, filter_poll))
    application.add_handler(CallbackQueryHandler(button_press))
    application.add_handler(MessageHandler(filters.command, unknown_command))
    application.add_handler(MessageHandler(filters.text, unknown_text))

    # Schedule jobs
    schedule.every(12).hours.do(delete_json_files)

    # Set webhook and start the bot
    await application.bot.set_webhook(url=os.getenv('webhook'))
    await application.update_queue.put(
        Update.de_json(data=text, bot=application.bot)
    )

    # Start and stop the application
    async with application:
        await application.start()
        await application.stop()

