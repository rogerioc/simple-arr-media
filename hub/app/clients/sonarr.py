import httpx
from typing import Dict, Any, Optional

class SonarrClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """Testa conexão e retorna status do sistema."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v3/system/status", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_root_folders(self) -> list[Dict[str, Any]]:
        """Obtém as pastas raiz configuradas."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v3/rootfolder", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def add_root_folder(self, path: str = "/data/media/tv") -> Dict[str, Any]:
        """Adiciona a pasta raiz se não existir."""
        existing = await self.get_root_folders()
        for folder in existing:
            if folder.get("path") == path:
                return {"status": "already_exists", "folder": folder}

        payload = {"path": path}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}/api/v3/rootfolder", headers=self.headers, json=payload)
            resp.raise_for_status()
            return {"status": "created", "folder": resp.json()}

    async def get_download_clients(self) -> list[Dict[str, Any]]:
        """Lista clientes de download existentes."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v3/downloadclient", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def add_qbittorrent_client(
        self,
        name: str = "qBittorrent",
        host: str = "qbittorrent",
        port: int = 8081,
        username: str = "admin",
        password: str = "adminadmin",
        category: str = "tv"
    ) -> Dict[str, Any]:
        """Cadastra o qBittorrent como Download Client no Sonarr."""
        existing = await self.get_download_clients()
        for client_cfg in existing:
            if client_cfg.get("name") == name or client_cfg.get("implementation") == "QBittorrent":
                return {"status": "already_exists", "client": client_cfg}

        payload = {
            "name": name,
            "enable": True,
            "protocol": "torrent",
            "priority": 1,
            "removeCompletedDownloads": True,
            "removeFailedDownloads": True,
            "implementation": "QBittorrent",
            "configContract": "QBittorrentSettings",
            "fields": [
                {"name": "host", "value": host},
                {"name": "port", "value": port},
                {"name": "useSsl", "value": False},
                {"name": "urlBase", "value": ""},
                {"name": "username", "value": username},
                {"name": "password", "value": password},
                {"name": "tvCategory", "value": category},
                {"name": "recentTvPriority", "value": 0},
                {"name": "olderTvPriority", "value": 0},
                {"name": "initialState", "value": 0}
            ]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}/api/v3/downloadclient", headers=self.headers, json=payload)
            resp.raise_for_status()
            return {"status": "created", "client": resp.json()}
