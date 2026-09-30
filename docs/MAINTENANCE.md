# 🛠️ Manutenção, Backups e Troubleshooting

Instruções para manter o servidor de mídia saudável, realizar backups e solucionar eventuais problemas comuns.

---

## 1. Atualizações dos Containers

Para atualizar todas as imagens para suas versões mais recentes:

```bash
# Baixar as versões mais recentes
docker compose pull

# Recriar apenas os containers que receberam atualização
docker compose up -d

# Limpar imagens antigas sem uso
docker image prune -f
```

---

## 2. Estratégia de Backup

Todos os bancos de dados, metadados de mídia e configurações dos containers ficam centralizados na pasta `./config`.

### Como fazer backup completo das configurações:
```bash
# Criar um arquivo compactado com as configurações
tar -czvf ~/backup_autoarr_$(date +%Y%m%d).tar.gz ./config
```

### Como restaurar o backup em uma máquina nova:
```bash
# Extrair o backup de volta na pasta do projeto
tar -xzvf backup_autoarr_YYYYMMDD.tar.gz -C ./
docker compose up -d
```

---

## 3. Gestão de Permissões no Linux

Se você criar pastas de mídia manualmente no terminal ou mover arquivos de outros discos, certifique-se de que o seu usuário e grupo possuam permissão:

```bash
# Ajustar permissões da partição de dados
sudo chown -R $USER:$USER /caminho/para/seu/data
sudo chmod -R 775 /caminho/para/seu/data

# Ajustar permissões das configurações
sudo chown -R $USER:$USER ./config
```

---

## 4. Solução de Problemas Frequentes (Troubleshooting)

### A. O 1337x ou TorrentGalaxy parou de responder no Prowlarr
* **Causa**: Mudança de proteção da Cloudflare ou IP do FlareSolverr.
* **Solução**:
  1. Verifique se o container do FlareSolverr está rodando (`docker --context default ps | grep flaresolverr`).
  2. No Prowlarr, vá em **Settings > Indexers > FlareSolverr**, clique em **Test** e salve.
  3. No indexador 1337x, teste um domínio espelho alternativo (ex: `https://1337x.so` ou `https://1337x.st`).

### B. O download terminou mas o filme não aparece no Jellyfin
* **Causa**: Falha no Hardlink ou categoria incorreta.
* **Solução**:
  1. No Radarr/Sonarr, vá em **Activity > Queue**. Se houver um ícone amarelo/laranja, passe o mouse para ler a mensagem (ex: *Waiting for import*).
  2. Confirme se o qBittorrent baixou o arquivo dentro da pasta `/data/torrents/` e não fora dela.

### C. A legenda está fora de sincronia na TV
* **Causa**: Taxa de quadros (FPS) diferente do release original.
* **Solução**:
  1. Abra o **Bazarr** (`http://<IP_DO_SERVIDOR>:6767`).
  2. Vá no filme/série e clique no ícone da **varinha mágica / sincronização**. O Bazarr comparará o áudio novamente e corrigirá os milissegundos do arquivo `.srt`.

### D. Reprodução travando ou CPU em 100% no Jellyfin
* **Causa**: Transcodificação rodando por software (CPU) em vez de hardware (GPU).
* **Solução**:
  1. No Jellyfin, vá em **Painel de Controle > Reprodução > Transcodificação**.
  2. Certifique-se de que **Intel QuickSync (QSV)** ou **VAAPI** está selecionado e o dispositivo `/dev/dri/renderD128` está configurado.
