import aiohttp
import asyncio


class TwinRepository:

    def __init__(
            self,
            auth_url: str,
            login: str,
            password: str,
            contacts_url: str,
    ):
        self.auth_url = auth_url
        self.contacts_url = contacts_url
        self.login = login
        self.password = password

    async def get_auth_token(self):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        json_data = {
            'email': self.login,
            'password': self.password,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.auth_url, headers=headers, json=json_data) as response:
                response.raise_for_status()
                if response.status == 200:
                    data = await response.json()
                    return data.get("token")

    async def get_call_data(self, token: str, params: dict) -> dict:
        """
        Получение данных по звонкам из TWIN

        :param token: str - TWIN токен
        :param params: параметры запроса
        """
        await asyncio.sleep(5)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.contacts_url, params=params, headers={"Authorization": f"Bearer {token}"}
            ) as response:
                response.raise_for_status()
                if response.status == 200:
                    data = await response.json()
                    return data
