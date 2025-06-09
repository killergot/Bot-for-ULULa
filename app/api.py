import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.users import User # Твоя модель
from app.repositoryes.user_repository import UserRepository


class ApiClient:
    def __init__(self, telegram_id: int, session: AsyncSession, base_url: str = "http://http://185.95.159.198/api"):
        self.telegram_id = telegram_id
        self.base_url = base_url
        self.repo = UserRepository(session)

    async def _refresh_tokens(self, user: User):
        headers = {"Authorization": f"Bearer {user.refresh_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/refresh",
                                     headers=headers)
            resp.raise_for_status()
            new_tokens = resp.json()

        # Обновляем токены в БД
        user = await self.repo.save_tokens(self.telegram_id,
                                    new_tokens["access_token"],
                                    new_tokens["refresh_token"])
        return new_tokens["access_token"]

    async def _request_with_token(self, method: str, url: str, **kwargs):
        user = await self.repo.get(self.telegram_id)
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {user.access_token}"

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.request(method, f"{self.base_url}{url}", headers=headers, **kwargs)
                if resp.status_code == 401:
                    raise httpx.HTTPStatusError("Unauthorized", request=resp.request, response=resp)
                return resp
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # Пробуем обновить токен и повторить запрос
                new_access_token = await self._refresh_tokens(user)
                headers["Authorization"] = f"Bearer {new_access_token}"

                async with httpx.AsyncClient() as client:
                    retry_resp = await client.request(method, f"{self.base_url}{url}", headers=headers, **kwargs)
                    retry_resp.raise_for_status()
                    return retry_resp
            raise

    async def get(self, url: str, **kwargs):
        return await self._request_with_token("GET", url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self._request_with_token("POST", url, **kwargs)

    async def put(self, url: str, **kwargs):
        return await self._request_with_token("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs):
        return await self._request_with_token("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs):
        return await self._request_with_token("DELETE", url, **kwargs)
