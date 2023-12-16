import pytest
from typing import AsyncIterator
from httpx import AsyncClient

import unapi.webhooks as webhooks
from unapi.main import app
from dotenv import load_dotenv
from os import environ

load_dotenv()


@pytest.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url=environ['API_URL']) as client:
        yield client


class TestMain:
    #  Tests that text returns the correct value
    @pytest.mark.anyio
    async def test_index(self, client: AsyncClient):
        response = await client.get('/')
        assert response.status_code == 200
        assert response.json() == "I'm ok"

    # @pytest.mark.anyio
    # async def test_init(self, client: AsyncClient, mocker):
    #     mocker.patch('unapi.webhooks.init', return_value=None)
    #     response = await client.get('/init')
    #     assert response.status_code == 200
    #     assert response.json() == "I'm ok"
    #     webhooks.init.assert_called_once()


