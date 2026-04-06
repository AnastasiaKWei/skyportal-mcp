# pyright: reportMissingTypeStubs=false
"""SkyPortal MCP server — config, auth, and entrypoint.

Tools are defined in the tools/ package and register themselves on import.
"""

import logging
import os

import httpx
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


# ─── Configuration (environment variables) ───────────────────────────────────

SKYPORTAL_URL = os.getenv("SKYPORTAL_URL", "http://localhost:5001")
SKYPORTAL_TOKEN = os.getenv("SKYPORTAL_TOKEN")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_BASE_URL = os.getenv("MCP_BASE_URL", f"http://localhost:{MCP_PORT}")


# ─── Auth helper for tools ──────────────────────────────────────────────────


def get_skyportal_token() -> str | None:
    """
    Get SkyPortal API token for the current request.

    In stdio mode: uses SKYPORTAL_TOKEN environment variable
    In HTTP mode: retrieves token from OAuth provider (per-request auth)

    Returns:
        API token string, or None if not authenticated
    """
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "stdio":
        return SKYPORTAL_TOKEN
    else:
        from fastmcp.server.dependencies import get_access_token

        access_token = get_access_token()
        return access_token.token if access_token else None


# ─── MCP server instance ────────────────────────────────────────────────────

_transport = os.getenv("MCP_TRANSPORT", "stdio")

_MCP_INSTRUCTIONS = (
    "Use the get_api_quick_reference tool to learn about available "
    "SkyPortal API endpoints and their parameters. Call it once at the "
    "start of a session or when you need to look up endpoint details."
)

if _transport == "stdio":
    # In stdio mode, no multi-user auth - use SKYPORTAL_TOKEN env var
    mcp = FastMCP("SkyPortal", instructions=_MCP_INSTRUCTIONS)
else:
    # In HTTP mode, use OAuth provider for multi-user bearer token auth
    from fastmcp.server.auth import AccessToken, OAuthProvider
    from mcp.server.auth.provider import AuthorizationCode, AuthorizationParams
    from mcp.server.auth.settings import ClientRegistrationOptions
    from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

    class SkyPortalOAuthProvider(OAuthProvider):
        """
        OAuth provider for bearer-token authentication.

        MCP clients send a SkyPortal API token as a Bearer header on every
        request.  FastMCP's auth layer calls load_access_token() to validate
        it against SkyPortal's /api/internal/profile endpoint.

        The remaining OAuth methods (client registration, authorize, token
        exchange) are required by the OAuthProvider interface but are not
        used in the normal flow — clients pass their token directly.
        """

        def __init__(self) -> None:
            super().__init__(
                base_url=MCP_BASE_URL,
                client_registration_options=ClientRegistrationOptions(enabled=True),
            )
            self._clients: dict[str, OAuthClientInformationFull] = {}

        async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
            return self._clients.get(client_id)

        async def register_client(self, client_info: OAuthClientInformationFull) -> None:
            if client_info.client_id:
                self._clients[client_info.client_id] = client_info

        async def authorize(
            self, client: OAuthClientInformationFull, params: AuthorizationParams
        ) -> str:
            raise NotImplementedError("Direct bearer-token auth is used instead")

        async def load_authorization_code(
            self, client: OAuthClientInformationFull, authorization_code: str
        ) -> AuthorizationCode | None:
            return None

        async def exchange_authorization_code(
            self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
        ) -> OAuthToken:
            raise NotImplementedError("Direct bearer-token auth is used instead")

        async def load_refresh_token(
            self, client: OAuthClientInformationFull, refresh_token: str
        ):
            return None

        async def exchange_refresh_token(self, client, refresh_token, scopes):
            raise NotImplementedError("Refresh tokens are not supported")

        async def load_access_token(self, token: str) -> AccessToken | None:
            """Validate a SkyPortal token against /api/internal/profile."""
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(
                        f"{SKYPORTAL_URL}/api/internal/profile",
                        headers={"Authorization": f"token {token}"},
                    )
                if not resp.is_success:
                    logger.warning(
                        "Token validation failed: SkyPortal returned %s", resp.status_code
                    )
                    return None
                data = resp.json().get("data", {})
                username = data.get("username", "unknown")
                user_id = data.get("id")
                logger.info("Token validated for user: %s (id=%s)", username, user_id)
                return AccessToken(
                    token=token,
                    client_id=username,
                    scopes=[f"user_id:{user_id}"],
                )
            except Exception:
                logger.exception("Token validation error (SKYPORTAL_URL=%s)", SKYPORTAL_URL)
                return None

        async def revoke_token(self, token) -> None:
            pass

    mcp = FastMCP("SkyPortal", instructions=_MCP_INSTRUCTIONS, auth=SkyPortalOAuthProvider())

# Import tool modules — their @mcp.tool() decorators register on import.
# This MUST come after mcp is defined.
from . import tools  # noqa: E402, F401
