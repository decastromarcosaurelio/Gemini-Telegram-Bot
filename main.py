import argparse
import traceback
import asyncio
import re
import telebot
from telebot.async_telebot import AsyncTeleBot
import handlers
from config import conf, generation_config, safety_settings

# Init args
parser = argparse.ArgumentParser()
parser.add_argument("tg_token", help="telegram token")
parser.add_argument("GOOGLE_GEMINI_KEY", help="Google Gemini API key")
options = parser.parse_args()
print("Arg parse done.")


async def main():
    # Init bot
    bot = AsyncTeleBot(options.tg_token)

    # Delete webhook before starting polling to avoid conflict
    try:
        # The delete_webhook() method returns True on success
        webhook_deleted = await bot.delete_webhook()
        if webhook_deleted:
            print("Webhook deleted successfully.")
            # Add a small delay to give Telegram servers time to process the deletion
            await asyncio.sleep(1)
        else:
            print("Failed to delete webhook. The bot might not start correctly if a webhook is still active.")
            # You might want to add more robust error handling here,
            # for example, by not starting polling if the webhook wasn't deleted.
    except Exception as e:
        print(f"Error deleting webhook: {e}")
        # Depending on the error, you might want to decide if you should proceed or not.
        # For now, we'll let it try to poll anyway, but this could be the source of the conflict.

    try:
        await bot.delete_my_commands(scope=None, language_code=None)
        print("Bot commands deleted successfully.")
    except Exception as e:
        print(f"Error deleting bot commands: {e}")


    try:
        await bot.set_my_commands(
        commands=[
            telebot.types.BotCommand("start", "Start"),
            telebot.types.BotCommand("gemini", f"using {conf['model_1']}"),
            telebot.types.BotCommand("gemini_pro", f"using {conf['model_2']}"),
            telebot.types.BotCommand("draw", "draw picture"),
            telebot.types.BotCommand("edit", "edit photo"),
            telebot.types.BotCommand("clear", "Clear all history"),
            telebot.types.BotCommand("switch","switch default model")
        ],
    )
        print("Bot commands set successfully.")
    except Exception as e:
        print(f"Error setting bot commands: {e}")

    print("Bot init done.")

    # Init commands
    bot.register_message_handler(handlers.start,                         commands=['start'],         pass_bot=True)
    bot.register_message_handler(handlers.gemini_stream_handler,         commands=['gemini'],        pass_bot=True)
    bot.register_message_handler(handlers.gemini_pro_stream_handler,     commands=['gemini_pro'],    pass_bot=True)
    bot.register_message_handler(handlers.draw_handler,                  commands=['draw'],          pass_bot=True)
    bot.register_message_handler(handlers.gemini_edit_handler,           commands=['edit'],          pass_bot=True)
    bot.register_message_handler(handlers.clear,                         commands=['clear'],         pass_bot=True)
    bot.register_message_handler(handlers.switch,                        commands=['switch'],        pass_bot=True)
    bot.register_message_handler(handlers.gemini_photo_handler,          content_types=["photo"],    pass_bot=True)
    bot.register_message_handler(
        handlers.gemini_private_handler,
        func=lambda message: message.chat.type == "private",
        content_types=['text'],
        pass_bot=True)

    # Start bot
    print("Starting Gemini_Telegram_Bot polling...")
    try:
        await bot.polling(none_stop=True, timeout=60, long_polling_timeout = 60) # Added timeout parameters
    except Exception as e:
        print(f"Error during polling: {e}")
        traceback.print_exc() # Print full traceback for polling errors

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    except Exception as e:
        print(f"Unhandled exception in main: {e}")
        traceback.print_exc()
