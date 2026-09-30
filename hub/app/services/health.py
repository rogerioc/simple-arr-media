import time
import httpx
from typing import Dict, Any

from app.core.config import settings
from app.core.discovery import discover_all_keys

async def check_single_service(name: str, url: str, api_key: str = None, headers: dict = None) -> Dict[str, Any]:
    """Testa a conectividade de um serviço individual e mede o tempo de resposta."""
    start = time.time()
    req_headers = headers or {}
    if api_key:
        req_headers["X-Api-Key"] = api_key

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, headers=req_headers)
            latency_ms = round((time.time() - start) * 1000, 1)
            # 2xx, 3xx, 401 (auth required) e 403 (forbidden/CSRF) indicam que o servidor web está ativo
            is_ok = resp.status_code in [200, 201, 202, 204, 301, 302, 307, 308, 401, 403]
            return {
                "name": name,
                "online": is_ok,
                "status_code": resp.status_code,
                "latency_ms": latency_ms,
                "url": url,
                "error": None
            }
    except Exception as e:
        latency_ms = round((time.time() - start) * 1000, 1)
        return {
            "name": name,
            "online": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "url": url,
            "error": str(e)
        }

async def check_all_services_health() -> Dict[str, Any]:
    """Testa a saúde de todos os 8 containers da stack."""
    keys = discover_all_keys()
    
    # Lista de endpoints de checagem
    checks = [
        ("prowlarr", f"{settings.PROWLARR_URL}/api/v1/system/status", keys["prowlarr"]["apiKey"]),
        ("radarr", f"{settings.RADARR_URL}/api/v3/system/status", keys["radarr"]["apiKey"]),
        ("sonarr", f"{settings.SONARR_URL}/api/v3/system/status", keys["sonarr"]["apiKey"]),
        ("bazarr", f"{settings.BAZARR_URL}/api/system/status", keys["bazarr"]["apiKey"]),
        ("flaresolverr", f"{settings.FLARESOLVERR_URL}/", None),
        ("qbittorrent", f"{settings.QBITTORRENT_URL}/", None),
        ("jellyfin", f"{settings.JELLYFIN_URL}/System/Info/Public", None),
        ("jellyseerr", f"{settings.JELLYSEERR_URL}/api/v1/status", None),
    ]

    results = {}
    for name, url, key in checks:
        results[name] = await check_single_service(name, url, key)

    return {
        "services": results,
        "total_online": sum(1 for s in results.values() if s["online"]),
        "total_services": len(results)
    }
