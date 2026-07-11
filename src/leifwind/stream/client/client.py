# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import time
from typing import Any, AsyncGenerator, Dict, Protocol
from uuid import UUID

import httpx
from pydantic import BaseModel, computed_field

from .metadata import (
    DetailResponse,
    MetadataEntity,
    MetadataField,
    MetadataList,
    MetadataProject,
)


class HealthStatus(BaseModel):
    status: str
    version: str

    @computed_field
    @property
    def ok(self) -> bool:
        return self.status == "ok"


class TokenProvider(Protocol):
    async def get_token(self) -> str: ...


class StaticTokenProvider:
    def __init__(self, token: str):
        self._token = token

    async def get_token(self) -> str:
        return self._token


class BearerAuth(httpx.Auth):
    def __init__(self, provider: TokenProvider):
        self._provider = provider

    async def async_auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {await self._provider.get_token()}"
        yield request


class ClientCredentialsTokenProvider:
    """Machine-to-machine tokens from ZITADEL's token endpoint (design D5).

    Default scopes request the resourceowner org claim and the API-project
    audience — the same three values the Terraform provider needs.
    """

    REFRESH_MARGIN = 60.0

    def __init__(
        self,
        *,
        issuer: str,
        client_id: str,
        client_secret: str,
        audience: str | None = None,
        scopes: list[str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self._issuer = issuer.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        if scopes is None:
            scopes = ["openid", "urn:zitadel:iam:user:resourceowner"]
            if audience:
                scopes.append(f"urn:zitadel:iam:org:project:id:{audience}:aud")
        self._scopes = scopes
        self._transport = transport
        self._token: str | None = None
        self._expires_at = float("-inf")

    async def get_token(self) -> str:
        now = time.monotonic()
        if self._token and now < self._expires_at - self.REFRESH_MARGIN:
            return self._token
        async with httpx.AsyncClient(transport=self._transport) as http:
            response = await http.post(
                f"{self._issuer}/oauth/v2/token",
                data={
                    "grant_type": "client_credentials",
                    "scope": " ".join(self._scopes),
                },
                auth=(self._client_id, self._client_secret),
            )
            response.raise_for_status()
        payload = response.json()
        self._token = payload["access_token"]
        self._expires_at = now + float(payload.get("expires_in", 3600))
        return self._token


class Leifwind:
    class EntityClient:
        """Client for interacting with entity endpoints."""

        @property
        def _client(self):
            return self._leifwind_client._client

        async def _request(self, method, path, dry_run=False, *args, **kwargs):
            """
            Make a request to the entity endpoint.

            Args:
                method: HTTP method
                path: Path to the endpoint
                *args: Additional arguments
                **kwargs: Additional keyword arguments

            Returns:
                Response from the server
            """
            params = kwargs.setdefault("params", {})
            params["dry_run"] = dry_run
            return await self._leifwind_client._request(
                method,
                f"/generic{path}",
                *args,
                **kwargs,
            )

        def __init__(self, client):
            self._leifwind_client = client

        async def get_entity_key(
            self,
            project_id: UUID,
            entity_name: str | UUID,
            key: Dict[str, Any] | UUID | str,
        ) -> str:
            params = {}
            params.update(key)
            response = await self._request(
                "GET",
                f"/projects/{project_id}/entities/{entity_name}/key",
                params=params,
            )
            return response.json()

        async def get_entity(
            self, project_id: UUID, entity_name: str | UUID, entity_key: str | UUID
        ) -> dict:
            response = await self._request(
                "GET",
                f"/projects/{project_id}/entities/{entity_name}/{entity_key}",
            )
            return response.json()

        async def delete_entity(
            self,
            project_id: UUID,
            entity_name: str | UUID,
            enttiy_key: str | UUID,
            dry_run: bool = False,
        ):
            raise NotImplementedError()

        async def delete_entity_fragmet(
            self,
            project_id,
            entity_name: str | UUID,
            enttiy_key: str | UUID,
            fragment_name: str,
            dry_run: bool = False,
        ):
            raise NotImplementedError()

        async def upsert_entity_fragment(
            self,
            project_id: UUID,
            entity_name: str | UUID,
            fragment_name: str,
            entity: Dict[str, Any],
            dry_run: bool = False,
        ) -> Dict[str, Any]:
            """
            Upsert a fragment to an entity.

            Args:
                project_id: The project ID
                entity_name: The entity name or ID
                fragment_name: The fragment name
                entity: The entity data

            Returns:
                The upserted entity
            """
            response = await self._request(
                "POST",
                f"/projects/{project_id}/entities/{entity_name}/fragments/{fragment_name}",
                model=entity,
                dry_run=dry_run,
            )
            return response.json()

    class MetadataClient:
        @property
        def _client(self):
            return self._leifwind_client._client

        async def _request(self, method, path, dry_run=False, *args, **kwargs):
            params = kwargs.setdefault("params", {})
            params["dry_run"] = dry_run
            return await self._leifwind_client._request(
                method,
                f"/metadata{path}",
                *args,
                **kwargs,
            )

        def __init__(self, client):
            self._leifwind_client = client

        async def upsert_project(
            self, project: MetadataProject, dry_run=False
        ) -> MetadataProject:
            response = await self._request(
                "POST",
                "/projects",
                model=project,
                dry_run=dry_run,
            )
            return MetadataProject.model_validate(response.json())

        async def get_project(self, project_id: UUID) -> MetadataProject:
            response = await self._request(
                "GET",
                f"/projects/{project_id}",
            )
            return MetadataProject.model_validate(response.json())

        async def get_entity(self, project_id: UUID, entity_id: UUID) -> MetadataEntity:
            response = await self._request(
                "GET",
                f"/projects/{project_id}/entities/{entity_id}",
            )
            return MetadataEntity.model_validate(response.json())

        async def list_entities(
            self,
            project_id: UUID,
            cursor: str | None = None,
            limit: int | None = None,
            pattern: str | None = None,
        ) -> MetadataList:
            response = await self._request(
                "GET",
                f"/projects/{project_id}/entities",
                params={"cursor": cursor, "limit": limit, "pattern": pattern},
            )
            return MetadataList.model_validate(response.json())

        async def iter_entities(
            self, project_id: UUID, limit: int | None = None, pattern: str | None = None
        ) -> AsyncGenerator[MetadataEntity, None]:
            entities = await self.list_entities(
                limit=limit, pattern=pattern, project_id=project_id
            )
            while entities.cursor or entities.objects:
                for entity in entities.objects:
                    yield entity

                if not entities.cursor:
                    break

                entities = await self.list_entities(
                    project_id=project_id, cursor=entities.cursor
                )

        async def list_fields(
            self,
            project_id: UUID,
            entity_id: UUID,
            cursor: str | None = None,
            limit: int | None = None,
            pattern: str | None = None,
        ) -> MetadataList:
            response = await self._request(
                "GET",
                f"/projects/{project_id}/entities/{entity_id}/fields",
                params={"cursor": cursor, "limit": limit, "pattern": pattern},
            )
            return MetadataList.model_validate(response.json())

        async def iter_fields(
            self,
            project_id: UUID,
            entity_id: UUID,
            limit: int | None = None,
            pattern: str | None = None,
        ) -> AsyncGenerator[MetadataField, None]:
            fields = await self.list_fields(
                project_id=project_id,
                entity_id=entity_id,
                limit=limit,
                pattern=pattern,
            )
            while fields.cursor or fields.objects:
                for field in fields.objects:
                    yield field

                if not fields.cursor:
                    break

                fields = await self.list_fields(
                    project_id=project_id,
                    entity_id=entity_id,
                    cursor=fields.cursor,
                )

        async def get_field(
            self, project_id: UUID, entity_id: UUID, field_id: UUID
        ) -> MetadataField:
            response = await self._request(
                "GET",
                f"/projects/{project_id}/entities/{entity_id}/fields/{field_id}",
            )
            return MetadataField.model_validate(response.json())

        async def list_projects(
            self,
            cursor: str | None = None,
            limit: int | None = None,
            pattern: str | None = None,
        ) -> MetadataList:
            response = await self._request(
                "GET",
                "/projects",
                params={"cursor": cursor, "limit": limit, "pattern": pattern},
            )
            return MetadataList.model_validate(response.json())

        async def iter_projects(
            self, limit: int | None = None, pattern: str | None = None
        ) -> AsyncGenerator[MetadataProject, None]:
            projects = await self.list_projects(limit=limit, pattern=pattern)
            while projects.cursor or projects.objects:
                for project in projects.objects:
                    yield project

                if not projects.cursor:
                    break

                projects = await self.list_projects(cursor=projects.cursor)

        async def upsert_entity(
            self, entity: MetadataEntity, dry_run: bool = False
        ) -> MetadataEntity:
            response = await self._request(
                "POST",
                f"/projects/{entity.project_id}/entities",
                model=entity,
                dry_run=dry_run,
            )
            return MetadataEntity.model_validate(response.json())

        async def upsert_field(
            self, field: MetadataField, dry_run: bool = False
        ) -> MetadataField:
            response = await self._request(
                "POST",
                f"/projects/{field.project_id}/entities/{field.entity_id}/fields",
                model=field,
                dry_run=dry_run,
            )
            return MetadataField.model_validate(response.json())

        async def delete_field(
            self, field: MetadataField, dry_run: bool = False
        ) -> DetailResponse:
            response = await self._request(
                "DELETE",
                f"/projects/{field.project_id}/entities/{field.entity_id}/fields/{field.object_id}",
                dry_run=dry_run,
            )
            return DetailResponse.model_validate(response.json())

        async def delete_entity(
            self, entity: MetadataEntity, dry_run: bool = False
        ) -> DetailResponse:
            response = await self._request(
                "DELETE",
                f"/projects/{entity.project_id}/entities/{entity.object_id}",
                dry_run=dry_run,
            )
            return DetailResponse.model_validate(response.json())

        async def delete_project(
            self, project: MetadataProject, dry_run: bool = False
        ) -> DetailResponse:
            response = await self._request(
                "DELETE",
                f"/projects/{project.object_id}",
                dry_run=dry_run,
            )
            return DetailResponse.model_validate(response.json())

    def __init__(self, base_url, auth: "TokenProvider | str | None" = None):
        self._base_url = base_url
        self._client = None
        if isinstance(auth, str):
            auth = StaticTokenProvider(auth)
        # httpx.Auth on the AsyncClient covers raw ._client usage too
        # (test_security.py posts raw payloads) — design D5.
        self._auth = BearerAuth(auth) if auth is not None else None
        self.metadata = self.MetadataClient(self)
        self.entity = self.EntityClient(self)

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self._base_url, auth=self._auth)
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._client.__aexit__(exc_type, exc, tb)

    async def _request(self, method, path, *args, model=None, **kwargs):
        assert not kwargs.get("dry_run")
        if model:
            if "headers" in kwargs:
                kwargs["headers"]["Content-Type"] = "application/json"
            else:
                kwargs["headers"] = {"Content-Type": "application/json"}

            if hasattr(model, "model_dump_json"):
                kwargs["content"] = model.model_dump_json()
            else:
                kwargs["content"] = json.dumps(model)

        # httpx serializes None values as empty-string query parameters
        # (e.g. ?limit=), which FastAPI then rejects on int-typed params.
        # Drop them so server-side defaults apply.
        if kwargs.get("params"):
            kwargs["params"] = {
                k: v for k, v in kwargs["params"].items() if v is not None
            }

        response = await self._client.request(
            method, path, timeout=None, *args, **kwargs
        )
        response.raise_for_status()
        return response

    async def healthz(self) -> HealthStatus:
        response = await self._request("GET", "/healthz")
        return HealthStatus.model_validate(response.json())
