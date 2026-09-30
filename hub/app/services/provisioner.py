from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.discovery import discover_all_keys
from app.core.models import ProvisioningConfig
from app.clients.radarr import RadarrClient
from app.clients.sonarr import SonarrClient
from app.clients.prowlarr import ProwlarrClient
from app.clients.bazarr import BazarrClient

def _resolve_keys(config: Optional[ProvisioningConfig] = None) -> Dict[str, Optional[str]]:
    discovered = discover_all_keys()
    custom_keys = (config.custom_keys if config else None) or {}
    return {
        "radarr": custom_keys.get("radarr") or discovered["radarr"]["apiKey"],
        "sonarr": custom_keys.get("sonarr") or discovered["sonarr"]["apiKey"],
        "prowlarr": custom_keys.get("prowlarr") or discovered["prowlarr"]["apiKey"],
        "bazarr": custom_keys.get("bazarr") or discovered["bazarr"]["apiKey"],
    }

async def provision_prowlarr(config: ProvisioningConfig, keys: Dict[str, Optional[str]], logs: List[Dict[str, Any]]):
    """Aplica configurações exclusivas do Prowlarr."""
    if not keys.get("prowlarr"):
        logs.append({"step": "prowlarr", "service": "prowlarr", "status": "error", "message": "API Key do Prowlarr não encontrada."})
        return

    try:
        prowlarr = ProwlarrClient(settings.PROWLARR_URL, keys["prowlarr"])
        
        # Proxy FlareSolverr
        if config.flaresolverr_enabled:
            proxy_res = await prowlarr.add_flaresolverr_proxy(config.flaresolverr_url)
            logs.append({"step": "prowlarr_proxy", "service": "prowlarr", "status": "success", "message": f"Proxy FlareSolverr ({config.flaresolverr_url}) configurado", "data": proxy_res})

        # Sincroniza Radarr
        if keys.get("radarr"):
            radarr_app_res = await prowlarr.add_radarr_app(
                radarr_url=settings.RADARR_URL,
                radarr_api_key=keys["radarr"],
                prowlarr_url=settings.PROWLARR_URL
            )
            logs.append({"step": "prowlarr_sync_radarr", "service": "prowlarr", "status": "success", "message": "Radarr vinculado como aplicação no Prowlarr", "data": radarr_app_res})

        # Sincroniza Sonarr
        if keys.get("sonarr"):
            sonarr_app_res = await prowlarr.add_sonarr_app(
                sonarr_url=settings.SONARR_URL,
                sonarr_api_key=keys["sonarr"],
                prowlarr_url=settings.PROWLARR_URL
            )
            logs.append({"step": "prowlarr_sync_sonarr", "service": "prowlarr", "status": "success", "message": "Sonarr vinculado como aplicação no Prowlarr", "data": sonarr_app_res})

        # Adiciona Indexadores Selecionados
        if config.prowlarr_indexers:
            idx_res = await prowlarr.add_popular_indexers(config.prowlarr_indexers)
            logs.append({"step": "prowlarr_indexers", "service": "prowlarr", "status": "success", "message": f"Indexadores processados ({len(idx_res)} adicionados): {', '.join(config.prowlarr_indexers)}", "data": idx_res})

    except Exception as e:
        logs.append({"step": "prowlarr_setup", "service": "prowlarr", "status": "error", "message": f"Falha ao configurar Prowlarr: {str(e)}"})

async def provision_radarr(config: ProvisioningConfig, keys: Dict[str, Optional[str]], logs: List[Dict[str, Any]]):
    """Aplica configurações exclusivas do Radarr (Root Folders e qBittorrent)."""
    if not keys.get("radarr"):
        logs.append({"step": "radarr", "service": "radarr", "status": "error", "message": "API Key do Radarr não encontrada."})
        return

    try:
        radarr = RadarrClient(settings.RADARR_URL, keys["radarr"])
        # Root Folder
        rf_res = await radarr.add_root_folder(config.radarr_root_folder)
        logs.append({"step": "radarr_root_folder", "service": "radarr", "status": "success", "message": f"Root Folder '{config.radarr_root_folder}' configurado no Radarr", "data": rf_res})

        # qBittorrent
        qbit_res = await radarr.add_qbittorrent_client(
            name="qBittorrent",
            host=config.qbit_host,
            port=config.qbit_port,
            username=config.qbit_user,
            password=config.qbit_password,
            category=config.qbit_movie_category
        )
        logs.append({"step": "radarr_download_client", "service": "radarr", "status": "success", "message": f"qBittorrent ({config.qbit_host}:{config.qbit_port}, cat: {config.qbit_movie_category}) cadastrado no Radarr", "data": qbit_res})
    except Exception as e:
        logs.append({"step": "radarr_setup", "service": "radarr", "status": "error", "message": f"Falha ao configurar Radarr: {str(e)}"})

async def provision_sonarr(config: ProvisioningConfig, keys: Dict[str, Optional[str]], logs: List[Dict[str, Any]]):
    """Aplica configurações exclusivas do Sonarr (Root Folders e qBittorrent)."""
    if not keys.get("sonarr"):
        logs.append({"step": "sonarr", "service": "sonarr", "status": "error", "message": "API Key do Sonarr não encontrada."})
        return

    try:
        sonarr = SonarrClient(settings.SONARR_URL, keys["sonarr"])
        # Root Folder
        rf_res = await sonarr.add_root_folder(config.sonarr_root_folder)
        logs.append({"step": "sonarr_root_folder", "service": "sonarr", "status": "success", "message": f"Root Folder '{config.sonarr_root_folder}' configurado no Sonarr", "data": rf_res})

        # qBittorrent
        qbit_res = await sonarr.add_qbittorrent_client(
            name="qBittorrent",
            host=config.qbit_host,
            port=config.qbit_port,
            username=config.qbit_user,
            password=config.qbit_password,
            category=config.qbit_tv_category
        )
        logs.append({"step": "sonarr_download_client", "service": "sonarr", "status": "success", "message": f"qBittorrent ({config.qbit_host}:{config.qbit_port}, cat: {config.qbit_tv_category}) cadastrado no Sonarr", "data": qbit_res})
    except Exception as e:
        logs.append({"step": "sonarr_setup", "service": "sonarr", "status": "error", "message": f"Falha ao configurar Sonarr: {str(e)}"})

async def provision_bazarr(config: ProvisioningConfig, keys: Dict[str, Optional[str]], logs: List[Dict[str, Any]]):
    """Aplica configurações exclusivas do Bazarr."""
    if not keys.get("bazarr"):
        logs.append({"step": "bazarr", "service": "bazarr", "status": "warning", "message": "API Key do Bazarr não encontrada."})
        return

    try:
        bazarr = BazarrClient(settings.BAZARR_URL, keys["bazarr"])
        if keys.get("radarr"):
            bz_radarr = await bazarr.configure_radarr(settings.RADARR_URL, keys["radarr"])
            logs.append({"step": "bazarr_radarr", "service": "bazarr", "status": "success", "message": f"Radarr vinculado no Bazarr para legendas ({config.bazarr_language})", "data": bz_radarr})
        if keys.get("sonarr"):
            bz_sonarr = await bazarr.configure_sonarr(settings.SONARR_URL, keys["sonarr"])
            logs.append({"step": "bazarr_sonarr", "service": "bazarr", "status": "success", "message": f"Sonarr vinculado no Bazarr para legendas ({config.bazarr_language})", "data": bz_sonarr})
    except Exception as e:
        logs.append({"step": "bazarr_setup", "service": "bazarr", "status": "error", "message": f"Falha ao configurar Bazarr: {str(e)}"})

async def run_single_service_provisioning(service_name: str, config: Optional[ProvisioningConfig] = None) -> Dict[str, Any]:
    """Executa o provisionamento isolado de um único serviço."""
    if config is None:
        config = ProvisioningConfig()
    keys = _resolve_keys(config)
    logs: List[Dict[str, Any]] = []

    if service_name == "prowlarr":
        await provision_prowlarr(config, keys, logs)
    elif service_name == "radarr":
        await provision_radarr(config, keys, logs)
    elif service_name == "sonarr":
        await provision_sonarr(config, keys, logs)
    elif service_name == "bazarr":
        await provision_bazarr(config, keys, logs)
    else:
        logs.append({"step": "error", "service": service_name, "status": "error", "message": f"Serviço '{service_name}' desconhecido."})

    return {
        "success": not any(l["status"] == "error" for l in logs),
        "service": service_name,
        "logs": logs
    }

async def run_full_auto_provisioning(config: Optional[ProvisioningConfig] = None) -> Dict[str, Any]:
    """Executa o pipeline completo chamando cada serviço modularmente."""
    if config is None:
        config = ProvisioningConfig()
    keys = _resolve_keys(config)
    logs: List[Dict[str, Any]] = []

    logs.append({
        "step": "discovery",
        "service": "system",
        "status": "info",
        "message": f"Chaves detectadas: Prowlarr ({'✓' if keys['prowlarr'] else '✗'}), Radarr ({'✓' if keys['radarr'] else '✗'}), Sonarr ({'✓' if keys['sonarr'] else '✗'}), Bazarr ({'✓' if keys['bazarr'] else '✗'})"
    })

    await provision_prowlarr(config, keys, logs)
    await provision_radarr(config, keys, logs)
    await provision_sonarr(config, keys, logs)
    await provision_bazarr(config, keys, logs)

    return {
        "success": not any(l["status"] == "error" for l in logs),
        "total_steps": len(logs),
        "logs": logs
    }
