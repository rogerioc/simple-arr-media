# 🏗️ Arquitetura Detalhada & TRaSH Guides

Este documento descreve as decisões de arquitetura e o fluxo de dados implementados no servidor de mídia.

---

## 1. O Conceito de Hardlinks e Volume Unificado

### O Problema do Mapeamento Tradicional (Ingênuo):
Em setups comuns, as pessoas costumam mapear dois volumes separados:
- `/downloads:/downloads`
- `/movies:/movies`

Quando o Radarr/Sonarr termina de baixar um filme de 20 GB em `/downloads`, o sistema operacional precisa **copiar os 20 GB** para `/movies` para que o Jellyfin possa ler. Isso resulta em:
1. **O dobro de espaço em disco ocupado** (40 GB para 1 único filme).
2. **Uso intenso de I/O de disco** (o servidor fica lento copiando gigabytes).
3. **Impossibilidade de semear o torrent (seeding)** sem manter arquivos duplicados.

---

### A Solução do TRaSH Guides Implementada:
Mapeamos um único ponto de montagem `<DATA_DIR>` como `/data` em todos os containers:

```text
/data (Host: <DATA_DIR>)
├── torrents/ (Onde o qBittorrent escreve)
└── media/    (Onde o Jellyfin lê e o Radarr/Sonarr organiza)
```

Como tanto a pasta de download quanto a pasta de exibição estão **no mesmo sistema de arquivos**, o Radarr e Sonarr utilizam **Hardlinks do Linux**:
* O arquivo de vídeo físico existe apenas uma vez no disco.
* Existem dois ponteiros de diretório para o mesmo bloco de dados: `/data/torrents/movies/Filme.mkv` e `/data/media/movies/Filme (2024)/Filme (2024).mkv`.
* O torrent continua semeando normalmente no qBittorrent enquanto o Jellyfin transmite o filme na TV com nome perfeito e metadados, **consumindo 0 bytes extras**!

---

## 2. Aceleração Gráfica por Hardware (Transcoding)

O Jellyfin está configurado para acessar a GPU integrada Intel através do dispositivo `/dev/dri`:

```yaml
    devices:
      - /dev/dri:/dev/dri
    group_add:
      - "44"   # GID video
      - "992"  # GID render
```

### Benefícios:
- O processador (CPU) não sofre picos de 100% de uso quando um cliente (ex: navegador web ou TV antiga) precisa converter formatos como HEVC/x265 para H.264.
- Suporte a **Intel QuickSync (QSV)** e **VAAPI**.
- Suporte a decodificação direta de vídeos 4K HDR e mapeamento de tons (Tone Mapping).

---

## 3. Rede e Descoberta de Dispositivos (Roku / DLNA)

O Jellyfin expõe as portas de rede necessárias para descoberta automática sem necessidade de configuração manual em cada TV:
* **`8096/tcp`**: Interface Web e streaming HTTP.
* **`7359/udp`**: Protocolo de descoberta automática de clientes Jellyfin (Roku, Android TV, webOS, Tizen).
* **`1900/udp`**: Protocolo SSDP / DLNA (para aparelhos e TVs antigas que não possuem o app na loja e transmitem via "Fontes de Mídia").

---

## 4. Matriz de Responsabilidades da Stack

Cada container possui uma responsabilidade única e bem delimitada para garantir que falhas isoladas não paralisem toda a mídia:

1. **Jellyseerr (`:5055`)**:
   - **Papel**: Interface de descoberta para os usuários finais da casa.
   - **Isolação**: Não faz downloads nem manipula arquivos de disco. Apenas se comunica via REST API com Radarr e Sonarr.

2. **Radarr (`:7878`) & Sonarr (`:8989`)**:
   - **Papel**: Inteligência de catalogação, verificação de qualidade (perfis 1080p/4K) e ordenação de arquivos.
   - **Isolação**: Não baixam torrents diretamente; delegam o tráfego de rede P2P para o qBittorrent.

3. **Prowlarr (`:9696`) & FlareSolverr (`:8191`)**:
   - **Papel**: Abstração de indexadores e proxy anti-bot.
   - **Isolação**: Radarr e Sonarr não precisam saber como resolver Cloudflare ou se comunicar com 10 sites diferentes; consultam apenas o Prowlarr.

4. **qBittorrent (`:8081`)**:
   - **Papel**: Motor exclusivo de download e upload (seeding).
   - **Isolação**: Não renomeia nem decide onde os filmes finais devem ficar; salva em `/data/torrents` e deixa o Radarr/Sonarr criar os hardlinks em `/data/media`.

5. **Bazarr (`:6767`)**:
   - **Papel**: Busca e sincronização cirúrgica de legendas.
   - **Isolação**: Executa em segundo plano sem travar o download do vídeo principal, corrigindo discrepâncias de tempo via `ffsubsync`.

6. **Jellyfin (`:8096`)**:
   - **Papel**: Entrega de streaming de alta fidelidade e transcodificação.
   - **Isolação**: Apenas leitura em `/data/media`.

---

## 5. Stack Tecnológica & Decisões de Engenharia

| Camada | Tecnologia | Decisão de Engenharia |
| :--- | :--- | :--- |
| **Orquestrador Hub** | Python 3.11 + FastAPI + Uvicorn | Alta velocidade de execução assíncrona para chamadas concorrentes às APIs sem bloquear o servidor. |
| **Cliente de Rede** | HTTPX (`asyncio`) | Permite disparar requisições simultâneas para Radarr, Sonarr, Prowlarr e Bazarr em milissegundos. |
| **Validação** | Pydantic v2 | Garantia de tipos e parsing seguro de configurações JSON submetidas pelo usuário. |
| **Descoberta de Chaves** | XML/YAML Parsers Nativos | Lê diretamente os arquivos de configuração montados do host como `ro` (read-only), sem expor chaves via comandos de shell. |
| **Frontend Web** | Vanilla HTML5 / CSS3 / ES6+ | Zero frameworks pesados (Node, Webpack, React ou Tailwind). Carregamento instantâneo (<50ms) e estilo Obsidian Dark sob medida. |
| **Containers** | Docker Engine nativa + Compose v2 | Sem camadas virtuais lentas (Docker Desktop), garantindo I/O nativo nos discos e acesso à GPU Intel (`/dev/dri`). |
| **Storage** | Linux POSIX Hardlinks | Evita duplicação de dados, preservando espaço em disco e permitindo seeding contínuo. |


