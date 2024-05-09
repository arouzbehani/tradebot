import asyncio
import requests
import telegram
import config

def send_message_to_channel(channel_id, message):
    api_url = f'https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage'
    params = {
        'chat_id': channel_id,
        'text': message
    }
    response = requests.post(api_url, json=params)
    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print('Failed to send message.')
async def send_simple(channel_id, message):
    bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)
    await bot.sendMessage(chat_id=channel_id, text=message)

async def main(channel_id, message):
    await send_simple(channel_id, message)
    # bot = telegram.Bot(token='6256939846:AAFYhqqownIKVb5T-Bh5-r6ctwMmJWp_RfI')
    # updates = await bot.getUpdates(timeout=60)
    # print(updates)
    # chat =await bot.get_chat('@traderbotchannel')
    # print(chat)
    #chat_id = updates[-1].message.chat_id
    #print(chat_id)

#asyncio.run(main("-1001982135624","HI"))

