import httpx
from typing import Dict, Any, List, Optional

class ProwlarrClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """Testa conexão e retorna status do Prowlarr."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/system/status", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_tags(self) -> List[Dict[str, Any]]:
        """Lista tags existentes."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/tag", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_or_create_tag(self, label: str = "flaresolverr") -> int:
        """Obtém ou cria uma tag e retorna seu ID numérico."""
        tags = await self.get_tags()
        for t in tags:
            if t.get("label", "").lower() == label.lower():
                return t["id"]

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}/api/v1/tag", headers=self.headers, json={"label": label})
            resp.raise_for_status()
            return resp.json()["id"]

    async def get_proxies(self) -> List[Dict[str, Any]]:
        """Lista proxies configurados."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/indexerproxy", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def add_flaresolverr_proxy(self, proxy_url: str = "http://flaresolverr:8191") -> Dict[str, Any]:
        """Adiciona o proxy FlareSolverr com tag flaresolverr."""
        tag_id = await self.get_or_create_tag("flaresolverr")
        existing = await self.get_proxies()
        for p in existing:
            if p.get("name") == "FlareSolverr" or p.get("implementation") == "FlareSolverr":
                return {"status": "already_exists", "proxy": p}

        payload = {
            "name": "FlareSolverr",
            "implementation": "FlareSolverr",
            "configContract": "FlareSolverrSettings",
            "tags": [tag_id],
            "fields": [
                {"name": "host", "value": proxy_url},
                {"name": "requestTimeout", "value": 60}
            ]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}/api/v1/indexerproxy", headers=self.headers, json=payload)
            resp.raise_for_status()
            return {"status": "created", "proxy": resp.json()}

    async def get_applications(self) -> List[Dict[str, Any]]:
        """Lista aplicações sincronizadas (Radarr/Sonarr)."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/applications", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def add_radarr_app(
        self,
        radarr_url: str = "http://radarr:7878",
        radarr_api_key: str = "",
        prowlarr_url: str = "http://prowlarr:9696"
    ) -> Dict[str, Any]:
        """Vincula o Radarr no Prowlarr com sincronização total."""
        apps = await self.get_applications()
        for app in apps:
            if app.get("name") == "Radarr" or app.get("implementation") == "Radarr":
                return {"status": "already_exists", "app": app}

        payload = {
            "name": "Radarr",
            "syncLevel": "fullSync",
            "implementation": "Radarr",
            "configContract": "RadarrSettings",
            "fields": [
                {"name": "prowlarrUrl", "value": prowlarr_url},
                {"name": "baseUrl", "value": radarr_url},
                {"name": "apiKey", "value": radarr_api_key},
                {"name": "syncCategories", "value": [2000, 2010, 2020, 2030, 2040, 2045, 2050, 2060]}
            ]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}/api/v1/applications", headers=self.headers, json=payload)
            resp.raise_for_status()
            return {"status": "created", "app": resp.json()}

    async def add_sonarr_app(
        self,
        sonarr_url: str = "http://sonarr:8989",
        sonarr_api_key: str = "",
        prowlarr_url: str = "http://prowlarr:9696"
    ) -> Dict[str, Any]:
        """Vincula o Sonarr no Prowlarr com sincronização total."""
        apps = await self.get_applications()
        for app in apps:
            if app.get("name") == "Sonarr" or app.get("implementation") == "Sonarr":
                return {"status": "already_exists", "app": app}

        payload = {
            "name": "Sonarr",
            "syncLevel": "fullSync",
            "implementation": "Sonarr",
            "configContract": "SonarrSettings",
            "fields": [
                {"name": "prowlarrUrl", "value": prowlarr_url},
                {"name": "baseUrl", "value": sonarr_url},
                {"name": "apiKey", "value": sonarr_api_key},
                {"name": "syncCategories", "value": [5000, 5010, 5020, 5030, 5040, 5045, 5050]}
            ]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{self.base_url}/api/v1/applications", headers=self.headers, json=payload)
            resp.raise_for_status()
            return {"status": "created", "app": resp.json()}

    async def get_indexers(self) -> List[Dict[str, Any]]:
        """Lista indexadores já cadastrados."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/indexer", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def get_indexer_schemas(self) -> List[Dict[str, Any]]:
        """Obtém schemas disponíveis para indexadores públicos/privados."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/v1/indexer/schema", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def add_popular_indexers(self, indexer_names: List[str] = None) -> List[Dict[str, Any]]:
        """Adiciona automaticamente indexadores recomendados com a tag do FlareSolverr e timeout resiliente."""
        if indexer_names is None:
            indexer_names = ["1337x", "YTS", "The Pirate Bay", "TorrentGalaxy", "EZTV"]

        tag_id = await self.get_or_create_tag("flaresolverr")
        existing_indexers = await self.get_indexers()
        existing_names = {idx.get("name", "").lower(): idx for idx in existing_indexers}

        schemas = await self.get_indexer_schemas()
        results = []

        for req_name in indexer_names:
            req_lower = req_name.strip().lower()
            
            # Se já existir, registra e não tenta duplicar
            if any(req_lower == name or req_lower in name for name in existing_names.keys()):
                results.append({"name": req_name, "status": "already_exists"})
                continue

            # Busca schema correspondente
            schema = next((s for s in schemas if req_lower in s.get("name", "").lower()), None)
            if not schema:
                results.append({"name": req_name, "status": "not_found_in_schemas"})
                continue

            schema["enable"] = True
            schema["tags"] = [tag_id]
            schema["appProfileId"] = 1

            # Garante baseUrl se necessário
            for f in schema.get("fields", []):
                if f.get("name") == "baseUrl" and not f.get("value"):
                    options = f.get("selectOptions", [])
                    if options and len(options) > 0:
                        f["value"] = options[0].get("value")

            try:
                # Indexadores como LimeTorrents realizam testes de scrape que podem levar até 60s
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(f"{self.base_url}/api/v1/indexer", headers=self.headers, json=schema)
                    if resp.status_code in [200, 201]:
                        results.append({"name": schema.get("name", req_name), "status": "created"})
                    elif "Should be unique" in resp.text:
                        results.append({"name": schema.get("name", req_name), "status": "already_exists"})
                    else:
                        results.append({"name": schema.get("name", req_name), "status": "failed", "error": resp.text})
            except httpx.TimeoutException:
                # Verifica se salvou mesmo com timeout
                check_existing = await self.get_indexers()
                if any(req_lower in idx.get("name", "").lower() for idx in check_existing):
                    results.append({"name": req_name, "status": "created"})
                else:
                    results.append({"name": req_name, "status": "timeout", "error": "Tempo limite excedido ao testar o indexador"})
            except Exception as e:
                results.append({"name": req_name, "status": "error", "error": str(e)})

        return results
