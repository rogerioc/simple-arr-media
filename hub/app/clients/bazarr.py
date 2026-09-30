import os
from pathlib import Path
import httpx
import yaml
from typing import Dict, Any, Optional

from app.core.config import settings

class BazarrClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """Testa conexão e retorna status do Bazarr."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/system/status", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_system_health(self) -> list[Dict[str, Any]]:
        """Retorna alertas e integridade do Bazarr."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/system/health", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    def _find_bazarr_yaml(self) -> Optional[Path]:
        """Localiza o arquivo config.yaml do Bazarr."""
        candidates = [
            settings.CONFIG_BASE_DIR / "bazarr" / "config" / "config.yaml",
            settings.CONFIG_BASE_DIR / "bazarr" / "config.yaml",
            Path("./config/bazarr/config/config.yaml"),
            Path("../config/bazarr/config/config.yaml")
        ]
        for p in candidates:
            if p.exists():
                return p
        return None

    async def configure_radarr(
        self,
        radarr_url: str = "http://radarr:7878",
        radarr_api_key: str = ""
    ) -> Dict[str, Any]:
        """Configura e valida os parâmetros do Radarr no Bazarr."""
        # O Bazarr lê os parâmetros de Radarr do config.yaml
        yaml_path = self._find_bazarr_yaml()
        if yaml_path and os.access(yaml_path, os.W_OK):
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

                if "radarr" not in data:
                    data["radarr"] = {}
                data["radarr"]["ip"] = "radarr"
                data["radarr"]["port"] = 7878
                data["radarr"]["apikey"] = radarr_api_key
                data["radarr"]["ssl"] = False
                data["radarr"]["base_url"] = ""

                with open(yaml_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f)
                return {"status": "configured_via_yaml", "file": str(yaml_path)}
            except Exception as e:
                print(f"[BazarrClient] Erro ao gravar YAML: {e}")

        # Se for somente leitura ou configurado anteriormente, valida status
        status = await self.get_system_status()
        return {"status": "validated", "bazarr_version": status.get("version")}

    async def configure_sonarr(
        self,
        sonarr_url: str = "http://sonarr:8989",
        sonarr_api_key: str = ""
    ) -> Dict[str, Any]:
        """Configura e valida os parâmetros do Sonarr no Bazarr."""
        yaml_path = self._find_bazarr_yaml()
        if yaml_path and os.access(yaml_path, os.W_OK):
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

                if "sonarr" not in data:
                    data["sonarr"] = {}
                data["sonarr"]["ip"] = "sonarr"
                data["sonarr"]["port"] = 8989
                data["sonarr"]["apikey"] = sonarr_api_key
                data["sonarr"]["ssl"] = False
                data["sonarr"]["base_url"] = ""

                with open(yaml_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f)
                return {"status": "configured_via_yaml", "file": str(yaml_path)}
            except Exception as e:
                print(f"[BazarrClient] Erro ao gravar YAML: {e}")

        status = await self.get_system_status()
        return {"status": "validated", "bazarr_version": status.get("version")}
