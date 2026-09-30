import os
import xml.etree.ElementTree as ET
from pathlib import Path
import yaml
from typing import Dict, Any, Optional

from app.core.config import settings

def _get_search_dirs(service_name: str) -> list[Path]:
    """Retorna possíveis caminhos para a pasta de configuração do serviço."""
    candidates = [
        settings.CONFIG_BASE_DIR / service_name,
        Path(f"./config/{service_name}"),
        Path(f"../config/{service_name}")
    ]
    return [p for p in candidates if p.exists()]

def extract_api_key_from_xml(config_path: Path) -> Optional[str]:
    """Lê o arquivo config.xml de aplicações *arr e extrai a API Key."""
    if not config_path.exists():
        return None
    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
        api_key = root.findtext("ApiKey")
        return api_key.strip() if api_key else None
    except Exception as e:
        print(f"[Discovery] Erro ao ler XML em {config_path}: {e}")
        return None

def extract_api_key_from_yaml(config_path: Path) -> Optional[str]:
    """Lê o arquivo config.yaml do Bazarr e extrai a API Key."""
    if not config_path.exists():
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                return data.get("auth", {}).get("apikey")
    except Exception as e:
        print(f"[Discovery] Erro ao ler YAML em {config_path}: {e}")
        return None

def discover_all_keys() -> Dict[str, Any]:
    """Varre todas as configurações e extrai chaves e portas de todos os serviços."""
    discovered = {
        "radarr": {"apiKey": None, "found": False, "configFile": None},
        "sonarr": {"apiKey": None, "found": False, "configFile": None},
        "prowlarr": {"apiKey": None, "found": False, "configFile": None},
        "bazarr": {"apiKey": None, "found": False, "configFile": None},
    }

    # Radarr, Sonarr, Prowlarr (XML)
    for service in ["radarr", "sonarr", "prowlarr"]:
        dirs = _get_search_dirs(service)
        for base in dirs:
            xml_file = base / "config.xml"
            if xml_file.exists():
                key = extract_api_key_from_xml(xml_file)
                if key:
                    discovered[service]["apiKey"] = key
                    discovered[service]["found"] = True
                    discovered[service]["configFile"] = str(xml_file)
                    break

    # Bazarr (YAML em bazarr/config/config.yaml ou bazarr/config.yaml)
    bazarr_dirs = _get_search_dirs("bazarr")
    for base in bazarr_dirs:
        yaml_candidates = [
            base / "config" / "config.yaml",
            base / "config.yaml"
        ]
        for yf in yaml_candidates:
            if yf.exists():
                key = extract_api_key_from_yaml(yf)
                if key:
                    discovered["bazarr"]["apiKey"] = key
                    discovered["bazarr"]["found"] = True
                    discovered["bazarr"]["configFile"] = str(yf)
                    break
        if discovered["bazarr"]["found"]:
            break

    return discovered
