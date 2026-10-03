# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
