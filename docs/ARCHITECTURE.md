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
