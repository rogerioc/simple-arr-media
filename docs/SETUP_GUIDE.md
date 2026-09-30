# 📖 Guia Completo de Configuração & Integrações

Este guia contém todos os passos e parâmetros utilizados para conectar os serviços entre si e configurar as Smart TVs e aparelhos de streaming.

---

## 1. Jellyfin (Streaming & Reprodução)

* **URL Local**: `http://<IP_DO_SERVIDOR>:8096`
* **Bibliotecas Configuradas**:
  * **Filmes**: Tipo `Filmes`, pasta `/data/media/movies`.
  * **Séries**: Tipo `Programas de TV`, pasta `/data/media/tv`.
* **Aceleração de Hardware**:
  * Acesse **Painel de Controle > Reprodução > Transcodificação**.
  * Selecione **Intel QuickSync (QSV)** ou **VAAPI**.
  * Dispositivo: `/dev/dri/renderD128`.

---

## 2. qBittorrent (Gerenciador de Downloads)

* **URL Local**: `http://<IP_DO_SERVIDOR>:8081`
* **Usuário**: `admin`
* **Configurações essenciais**:
  * Em **Ferramentas > Opções > Downloads**:
    * Diretório padrão: `/data/torrents/`
  * Em **Ferramentas > Opções > Web UI**:
    * Altere a senha padrão do administrador.

---

## 3. Radarr (Filmes)

* **URL Local**: `http://<IP_DO_SERVIDOR>:7878`
* **Root Folder**: `/data/media/movies` (com a opção *Use Hardlinks* ativada).
* **Download Client**:
  * **Host**: `qbittorrent`
  * **Porta**: `8081`
  * **Categoria**: `movies`
* **API Key**: Disponível em *Settings > General > Security*.

---

## 4. Sonarr (Séries)

* **URL Local**: `http://<IP_DO_SERVIDOR>:8989`
* **Root Folder**: `/data/media/tv`
* **Download Client**:
  * **Host**: `qbittorrent`
  * **Porta**: `8081`
  * **Categoria**: `tv`
* **Estrutura de Pastas de Séries**:
  ```text
  /data/media/tv/NomeDaSerie/Season 01/NomeDaSerie - S01E01.mkv
  ```

---

## 5. Prowlarr & FlareSolverr (Trackers e Bypass de Cloudflare)

* **Prowlarr URL**: `http://<IP_DO_SERVIDOR>:9696`
* **FlareSolverr URL**: `http://flaresolverr:8191` (porta host `8191`)
* **Configuração de Proxy no Prowlarr**:
  * Em **Settings > Indexers > Proxy > Add FlareSolverr**:
    * **Host**: `http://flaresolverr:8191`
    * **Tag**: `flaresolverr`
* **Indexadores Configurados**:
  * **YTS**: Filmes leves em 1080p/4K (sem tag).
  * **The Pirate Bay**: Acervo geral (sem tag).
  * **1337x**: Catálogo amplo com tag `flaresolverr`.
  * **EZTV**: Séries de TV (sem tag).
* **Sincronização com Radarr e Sonarr**:
  * Em **Settings > Apps**: Adicione Radarr (`http://radarr:7878`) e Sonarr (`http://sonarr:8989`) com suas respectivas API Keys.

---

## 6. Bazarr (Legendas Sincronizadas em pt-BR)

* **URL Local**: `http://<IP_DO_SERVIDOR>:6767`
* **Idiomas (Languages)**:
  * Perfil criado com **Portuguese (Brazil)**.
* **Sincronização por Áudio (Audio Synchronization)**:
  * Ativado em **Settings > Subtitles > Audio Synchronization**.
  * Referência: **Audio Track** (compara diretamente com o áudio do vídeo).
* **Conexões**:
  * Radarr: `http://radarr:7878`
  * Sonarr: `http://sonarr:8989`

---

## 7. Jellyseerr (Portal de Requisições com Aprovação)

* **URL Local**: `http://<IP_DO_SERVIDOR>:5055`
* **Usuário Admin Local**: `admin@local.com`
* **Aprovação Prévia de Downloads**:
  * Em **Settings > Users > Default Permissions**:
    * ❌ Desmarcar *Auto-Approve Movies*
    * ❌ Desmarcar *Auto-Approve Series*
    * ✅ Manter *Request*

---

## 8. Clientes de Reprodução (Smart TVs e Roku)

### Roku
1. Na loja de canais Roku, instale o canal oficial **Jellyfin**.
2. Conecte no servidor: `http://<IP_DO_SERVIDOR>:8096`.

### LG webOS
1. Na LG Content Store / Apps, instale o app **Jellyfin**.
2. Aponte para `http://<IP_DO_SERVIDOR>:8096`.

### Samsung Tizen
1. Se disponível na loja oficial do modelo, instale o app **Jellyfin**.
2. Alternativamente, abra o **Navegador Web da Samsung** e acesse `http://<IP_DO_SERVIDOR>:8096` em tela cheia.
3. Via DLNA: Em "Fontes / Dispositivos", o Jellyfin aparecerá como servidor de mídia nativo.
