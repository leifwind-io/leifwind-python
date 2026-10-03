#
#  Copyright (C)  2025 bbruhn(leifwind)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import httpx
import pytest

from leifwind.stream.client import client as lw_client


@pytest.mark.asyncio(loop_scope="function")
async def test_static_token_on_raw_client_requests():
    seen = []

    def handler(request):
        seen.append(request.headers.get("Authorization"))
        return httpx.Response(200, json={"status": "ok"})

    lw = lw_client.Leifwind("http://api.test", auth="tok-123")
    # mirror __aenter__ but with a mock transport
    lw._client = httpx.AsyncClient(
        base_url="http://api.test",
        auth=lw._auth,
        transport=httpx.MockTransport(handler),
    )
    await lw._client.get("/healthz")  # raw usage (test_security.py style)
    await lw._request("GET", "/healthz")  # funneled usage
    assert seen == ["Bearer tok-123", "Bearer tok-123"]


@pytest.mark.asyncio(loop_scope="function")
async def test_anonymous_client_sends_no_auth_header():
    seen = []

    def handler(request):
        seen.append("Authorization" in request.headers)
        return httpx.Response(200, json={"status": "ok"})

    lw = lw_client.Leifwind("http://api.test")
    lw._client = httpx.AsyncClient(
        base_url="http://api.test",
        auth=lw._auth,
        transport=httpx.MockTransport(handler),
    )
    await lw._client.get("/healthz")
    assert seen == [False]


@pytest.mark.asyncio(loop_scope="function")
async def test_client_credentials_caches_until_expiry():
    calls = []

    def handler(request):
        calls.append(dict(httpx.QueryParams(request.content.decode())))
        return httpx.Response(
            200, json={"access_token": f"tok-{len(calls)}", "expires_in": 3600}
        )

    provider = lw_client.ClientCredentialsTokenProvider(
        issuer="http://idp.test",
        client_id="cid",
        client_secret="sec",
        audience="326102453042806786",
        transport=httpx.MockTransport(handler),
    )
    assert await provider.get_token() == "tok-1"
    assert await provider.get_token() == "tok-1"  # cached
    assert len(calls) == 1
    assert calls[0]["grant_type"] == "client_credentials"
    scope = calls[0]["scope"]
    assert "openid" in scope
    assert "urn:zitadel:iam:user:resourceowner" in scope
    assert "urn:zitadel:iam:org:project:id:326102453042806786:aud" in scope


@pytest.mark.asyncio(loop_scope="function")
async def test_client_credentials_refreshes_expired_token():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx.Response(
            200, json={"access_token": f"tok-{len(calls)}", "expires_in": 30}
        )

    provider = lw_client.ClientCredentialsTokenProvider(
        issuer="http://idp.test",
        client_id="cid",
        client_secret="sec",
        transport=httpx.MockTransport(handler),
    )
    assert await provider.get_token() == "tok-1"
    # expires_in 30s minus the 60s refresh margin -> immediately stale
    assert await provider.get_token() == "tok-2"
