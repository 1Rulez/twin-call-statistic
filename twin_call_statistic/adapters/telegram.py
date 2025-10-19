import aiohttp

class Telegram:
    def __init__(self, tg_token, tg_chat_id):
        self.tg_token = tg_token
        self.tg_chat_id = tg_chat_id

    async def send_telegram_message(self, message):
        url = f'https://api.telegram.org/bot{self.tg_token}/sendMessage'
        payload = {
            'chat_id': self.tg_chat_id,
            'text': message
        }
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                if response.status == 200:
                    data = await response.json()
                    return data
