from __future__ import annotations

from bughunter.plugins.web.headers import SecurityHeadersPlugin
from bughunter.plugins.web.js_endpoints import JavaScriptEndpointsPlugin
from bughunter.plugins.web.jwt import JWTClaimsPlugin

BUILTIN_WEB_PLUGINS = (
    SecurityHeadersPlugin,
    JWTClaimsPlugin,
    JavaScriptEndpointsPlugin,
)


__all__ = [
    "BUILTIN_WEB_PLUGINS",
    "JWTClaimsPlugin",
    "JavaScriptEndpointsPlugin",
    "SecurityHeadersPlugin",
]
