from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ProvisioningConfig(BaseModel):
    # Radarr & Sonarr Root Folders
    radarr_root_folder: str = Field(default="/data/media/movies", description="Caminho raiz para filmes")
    sonarr_root_folder: str = Field(default="/data/media/tv", description="Caminho raiz para séries")

    # qBittorrent Config
    qbit_host: str = Field(default="qbittorrent", description="Host interno do qBittorrent")
    qbit_port: int = Field(default=8081, description="Porta do qBittorrent")
    qbit_user: str = Field(default="admin", description="Usuário do qBittorrent")
    qbit_password: str = Field(default="adminadmin", description="Senha do qBittorrent")
    qbit_movie_category: str = Field(default="movies", description="Categoria para filmes no qBit")
    qbit_tv_category: str = Field(default="tv", description="Categoria para séries no qBit")
    qbit_remove_completed: bool = Field(default=True, description="Remover torrents completados e importados")

    # Prowlarr & FlareSolverr Config
    flaresolverr_enabled: bool = Field(default=True, description="Ativar proxy FlareSolverr para Cloudflare")
    flaresolverr_url: str = Field(default="http://flaresolverr:8191", description="URL do FlareSolverr")
    prowlarr_indexers: List[str] = Field(
        default=["1337x", "YTS", "The Pirate Bay", "TorrentGalaxy", "EZTV"],
        description="Lista de indexadores a serem ativados no Prowlarr"
    )

    # Bazarr Config
    bazarr_language: str = Field(default="pt-BR", description="Idioma padrão de legendas")
    bazarr_ffsubsync: bool = Field(default=True, description="Ativar sincronização por análise de áudio")

    # Chaves customizadas manuais (opcional)
    custom_keys: Optional[Dict[str, Optional[str]]] = None
