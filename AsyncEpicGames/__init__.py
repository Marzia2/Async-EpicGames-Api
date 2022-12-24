import asyncio
import json
import os
import aiohttp
from pathlib import Path
from .m_types.Exeption import AuthorisationError
from .m_types import EpicGames


class EpicApi(object):
    __data_items__ = Path(os.getcwd(), "dataitems.json")

    def __init__(self, access_token: str, account_id: str, auth_data: dict, *args, **kwargs):
        self.access_token = access_token
        self.account_id = account_id
        self.auth_data = auth_data
        self.headers = {"Authorization": f"bearer {access_token}", "Content-Type": "application/json"}
        self.aio_client = aiohttp.ClientSession

    @property
    async def raw_fortnite_account(self) -> dict:
        async with self.aio_client(headers=self.headers) as client:
            response = await client.post(
                f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{self.account_id}/client/QueryProfile?profileId=athena&rvn=-1',
                json=self.auth_data)
            return await response.json()

    @property
    def metadata(self) -> dict:
        return {"access_token": self.access_token, "account_id": self.account_id}

    @property
    async def my_account(self) -> EpicGames.Account:
        async with self.aio_client(headers=self.headers) as client:
            response = await client.get(
                f'https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{self.account_id}')
            return EpicGames.Account(**(await response.json()))

    @property
    async def my_fortnite_account(self) -> EpicGames.FortniteAccount:
        account_data = await self.raw_fortnite_account
        return EpicGames.FortniteAccount(**(account_data["profileChanges"][0]['profile']))

    @property
    async def items(self) -> list[EpicGames.Item]:
        """
        The function gets a list of items, to get the name, rarity, use the serialize_items method
        :return: EpicGames.Item
        """
        account_data = await self.raw_fortnite_account
        account_data = account_data["profileChanges"][0]['profile']
        items = []
        for item in account_data["items"].values():
            type_, id = item['templateId'].split(":")
            item_seen = False
            if 'item_seen' in item['attributes']:
                item_seen = item['attributes']['item_seen']
            items.append(EpicGames.Item(id=id, type_=type_, item_seen=item_seen))
        return items

    async def __generate_data_items(self):
        async with self.aio_client() as client:
            response = await client.get("https://fortnite-api.com/v2/cosmetics/br")
            response_json = await response.json()
            items = {}
            for item in response_json['data']:
                items[item["id"].lower()] = {"id": item["id"], "name": item["name"], "rarity": item["rarity"]['value']}
            with open(self.__data_items__, 'w', encoding='utf-8') as outfile:
                json.dump(items, outfile, indent=4, ensure_ascii=False)

    async def serialize_items(self, items: list[EpicGames.Item], refresh: bool = True):
        """
        Gets the item's rarity and name
        :param items: Items obtained with items
        :param refresh: Recreates the file with the item date
        :return:
        """
        if not os.path.exists(self.__data_items__) or refresh:
            await self.__generate_data_items()
        with open(self.__data_items__, "r", encoding="utf-8") as file:
            data_items = json.loads(file.read())
        r_items = []
        for item in items:
            if item.item_seen and item.type_ in ('AthenaCharacter', 'AthenaPickaxe'):
                r_items.append(data_items.get(item.id, {"id": item.id, "name": "None", "rarity": "None"}))
        return r_items


class EpicAuth(object):
    __clint_id__ = "3446cd72694c4a4485d81b77adbb2141"
    __authorization__ = "basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="

    def __init__(self, epic_session_ap: str = "", epic_bearer_token: str = "", raw_cookies: dict = None):
        '''

        :param epic_session_ap: Need cookie value this name
        :param epic_bearer_token: Need cookie value this name
        :param raw_cookies: If you want to pass cookies as a dictionary then epic_session_ap, epic_bearer_token are not used
        '''
        self.cookies = dict(EPIC_SESSION_AP=epic_session_ap, EPIC_BEARER_TOKEN=epic_bearer_token)
        if raw_cookies:
            self.cookies = raw_cookies
        self.aio_client = aiohttp.ClientSession
        self.authorization_code = None

    @property
    async def generate_authorization_code(self) -> str:
        """
        The function sends a request to receive an authorization code
        It also sets the code to an instance of the class
        :return: Authorization code
        """
        async with self.aio_client(cookies=self.cookies) as client:
            response = await client.get(
                f'https://www.epicgames.com/id/api/redirect?clientId={self.__clint_id__}&responseType=code', timeout=10)
            self.authorization_code = (await response.json())['authorizationCode']
            if not self.authorization_code:
                raise AuthorisationError("Authorization error, cookies outdated/invalid")
            return self.authorization_code

    async def get_api(self, authorization_code: str = None) -> EpicApi:
        """
        The function receives an api key and an account ID
        :param authorization_code: If you want to pass your authorization code
        :return: API for working with epic account
        """
        async with self.aio_client(cookies=self.cookies) as client:
            if authorization_code:
                self.authorization_code = authorization_code
            elif not self.authorization_code:
                await self.generate_authorization_code

            headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": self.__authorization__}
            data = {"grant_type": "authorization_code", "code": self.authorization_code, "token_type": "eg1"}
            response = await client.post('https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token',
                                         data=data, headers=headers, timeout=10)
            response_json = await response.json()
            return EpicApi(**response_json, auth_data=data)
