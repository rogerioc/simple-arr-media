import os
from pathlib import Path
from pydantic import BaseModel

class Settings(BaseModel):
    # Diretórios de montagem
    CONFIG_BASE_DIR: Path = Path(os.getenv("CONFIG_BASE_DIR", "/config"))
    DATA_BASE_DIR: Path = Path(os.getenv("DATA_BASE_DIR", "/data"))

    # URLs dos serviços na rede interna Docker
    RADARR_URL: str = os.getenv("RADARR_URL", "http://radarr:7878")
    SONARR_URL: str = os.getenv("SONARR_URL", "http://sonarr:8989")
    PROWLARR_URL: str = os.getenv("PROWLARR_URL", "http://prowlarr:9696")
    BAZARR_URL: str = os.getenv("BAZARR_URL", "http://bazarr:6767")
    QBITTORRENT_URL: str = os.getenv("QBITTORRENT_URL", "http://qbittorrent:8081")
    FLARESOLVERR_URL: str = os.getenv("FLARESOLVERR_URL", "http://flaresolverr:8191")
    JELLYFIN_URL: str = os.getenv("JELLYFIN_URL", "http://jellyfin:8096")
    JELLYSEERR_URL: str = os.getenv("JELLYSEERR_URL", "http://jellyseerr:5055")

    # Credenciais padrão qBittorrent
    QBIT_USER: str = os.getenv("QBIT_USER", "admin")
    QBIT_PASSWORD: str = os.getenv("QBIT_PASSWORD", "adminadmin")

    # Caminhos internos de mídia (Hardlink compliant)
    MEDIA_MOVIES_PATH: str = "/data/media/movies"
    MEDIA_TV_PATH: str = "/data/media/tv"
    TORRENTS_PATH: str = "/data/torrents"

settings = Settings()
