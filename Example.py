from AsyncEpicGames import EpicAuth
import asyncio


async def main():
    auth = EpicAuth(
        epic_session_ap="",
        epic_bearer_token=""
    )
    await auth.generate_authorization_code  # Генерируем код авторизации
    api = await auth.get_api()  # Создаем сессию, послче чего мы сможем получать информацию

    epic_games_account = await api.my_account
    fortnite_account = await api.my_fortnite_account
    items = await api.items
    serialize_items = await api.serialize_items(items=items, refresh=True)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
