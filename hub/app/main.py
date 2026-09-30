import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict

from app.core.config import settings
from app.core.models import ProvisioningConfig
from app.core.discovery import discover_all_keys
from app.services.health import check_all_services_health
from app.services.provisioner import run_full_auto_provisioning, run_single_service_provisioning

app = FastAPI(
    title="SimpleArrMedia Hub & Control Plane",
    description="Central de automação, configuração e diagnóstico da stack Jellyfin, Radarr, Sonarr, Prowlarr e Bazarr",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/discovery")
async def get_discovered_keys():
    """Retorna as API Keys descobertas automaticamente nos arquivos de config."""
    return discover_all_keys()

@app.get("/api/health")
async def get_health_status():
    """Verifica a saúde e latência de todos os 8 containers."""
    return await check_all_services_health()

@app.get("/api/setup/defaults")
async def get_setup_defaults():
    """Retorna a configuração padrão recomendada (TRaSH Guides)."""
    return ProvisioningConfig().model_dump()

@app.post("/api/provision/all")
async def provision_all():
    """Executa a configuração padrão recomendada em 1 clique em toda a stack."""
    result = await run_full_auto_provisioning(ProvisioningConfig())
    return result

@app.post("/api/provision/custom")
async def provision_custom(config: ProvisioningConfig):
    """Executa a configuração com os parâmetros customizados informados pelo usuário."""
    result = await run_full_auto_provisioning(config)
    return result

@app.post("/api/provision/service/{service_name}")
async def provision_single_service(service_name: str, config: Optional[ProvisioningConfig] = None):
    """Executa a configuração exclusiva de um único serviço modificado."""
    valid_services = ["radarr", "sonarr", "prowlarr", "bazarr"]
    if service_name.lower() not in valid_services:
        raise HTTPException(status_code=400, detail=f"Serviço inválido. Escolha entre: {', '.join(valid_services)}")
    result = await run_single_service_provisioning(service_name.lower(), config)
    return result

@app.get("/api/info")
async def get_system_info():
    """Retorna parâmetros do host e caminhos de montagem."""
    return {
        "media_movies": settings.MEDIA_MOVIES_PATH,
        "media_tv": settings.MEDIA_TV_PATH,
        "torrents": settings.TORRENTS_PATH,
        "config_base": str(settings.CONFIG_BASE_DIR),
        "data_base": str(settings.DATA_BASE_DIR),
    }

# Montagem de arquivos estáticos da UI
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
