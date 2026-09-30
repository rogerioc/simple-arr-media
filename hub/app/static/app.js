document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    const globalStatusDot = document.querySelector('.status-dot');
    const globalStatusText = document.getElementById('globalStatusText');
    const btnRefreshHealth = document.getElementById('btnRefreshHealth');
    
    const quickKeyStatusList = document.getElementById('quickKeyStatusList');
    const servicesGrid = document.getElementById('servicesGrid');
    const keysGrid = document.getElementById('keysGrid');
    
    const btnRunProvision = document.getElementById('btnRunProvision');
    const consoleBody = document.getElementById('consoleBody');
    const consoleStatus = document.getElementById('consoleStatus');
    const btnCopyLogs = document.getElementById('btnCopyLogs');
    const btnClearLogs = document.getElementById('btnClearLogs');

    const customConfigForm = document.getElementById('customConfigForm');
    const btnResetDefaults = document.getElementById('btnResetDefaults');
    const btnApplyCustom = document.getElementById('btnApplyCustom');
    const btnCardActions = document.querySelectorAll('.btn-card-action');
    const toastContainer = document.getElementById('toastContainer');

    let discoveredKeys = {};
    let defaultSettings = {};

    // 1. Toast Notification Helper
    function showToast(message, type = 'info') {
        if (!toastContainer) return;
        const toast = document.createElement('div');
        toast.className = 'toast';
        
        let icon = 'ℹ';
        if (type === 'success') icon = '✓';
        if (type === 'error') icon = '✗';

        toast.innerHTML = `
            <span style="font-weight: 700; color: ${type === 'success' ? '#34d399' : type === 'error' ? '#f87171' : '#818cf8'}">${icon}</span>
            <span>${message}</span>
        `;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    }

    // 2. Tab Navigation
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    function switchTab(tabName) {
        tabButtons.forEach(b => {
            if (b.getAttribute('data-tab') === tabName) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });
        tabContents.forEach(c => {
            if (c.id === `tab-${tabName}`) {
                c.classList.add('active');
            } else {
                c.classList.remove('active');
            }
        });
    }

    // 3. API Keys Discovery
    async function loadDiscoveredKeys() {
        try {
            const res = await fetch('/api/discovery');
            if (!res.ok) throw new Error('Falha ao obter chaves');
            discoveredKeys = await res.json();
            
            renderQuickKeys();
            renderFullKeys();
        } catch (err) {
            console.error('Erro ao carregar chaves:', err);
            if (quickKeyStatusList) {
                quickKeyStatusList.innerHTML = `<p style="color: var(--danger); font-size: 0.85rem;">Erro ao ler chaves do host.</p>`;
            }
        }
    }

    function renderQuickKeys() {
        if (!quickKeyStatusList) return;
        quickKeyStatusList.innerHTML = '';
        Object.entries(discoveredKeys).forEach(([name, data]) => {
            const div = document.createElement('div');
            div.className = 'key-status-item';
            div.innerHTML = `
                <span class="key-name">
                    <span style="color: var(--primary-light);">●</span> ${name}
                </span>
                <span class="key-badge ${data.found ? 'found' : 'missing'}">
                    ${data.found ? '✓ Carregada' : '✗ Ausente'}
                </span>
            `;
            quickKeyStatusList.appendChild(div);
        });
    }

    function renderFullKeys() {
        if (!keysGrid) return;
        keysGrid.innerHTML = '';
        Object.entries(discoveredKeys).forEach(([name, data]) => {
            const card = document.createElement('div');
            card.className = 'key-card';
            const maskedKey = data.apiKey ? '•'.repeat(Math.min(data.apiKey.length, 32)) : 'Nenhuma chave encontrada';

            card.innerHTML = `
                <div class="key-card-top">
                    <span class="key-card-title">${name}</span>
                    <span class="key-badge ${data.found ? 'found' : 'missing'}">
                        ${data.found ? '✓ Detectada' : '✗ Não encontrada'}
                    </span>
                </div>
                <div class="key-file-path" title="Caminho do arquivo de configuração">${data.configFile || 'Arquivo não encontrado'}</div>
                <div class="key-input-container">
                    <div class="key-input-box" data-raw="${data.apiKey || ''}" data-masked="${maskedKey}">
                        ${maskedKey}
                    </div>
                    ${data.apiKey ? `
                        <button type="button" class="key-action-btn btn-toggle-mask" title="Mostrar/Ocultar chave">
                            👁
                        </button>
                        <button type="button" class="key-action-btn btn-copy-key" title="Copiar chave">
                            Copiar
                        </button>
                    ` : ''}
                </div>
            `;

            // Listeners para toggle e copy
            const btnToggle = card.querySelector('.btn-toggle-mask');
            const btnCopy = card.querySelector('.btn-copy-key');
            const inputBox = card.querySelector('.key-input-box');

            if (btnToggle && inputBox) {
                let isRevealed = false;
                btnToggle.addEventListener('click', () => {
                    isRevealed = !isRevealed;
                    inputBox.textContent = isRevealed ? inputBox.getAttribute('data-raw') : inputBox.getAttribute('data-masked');
                    btnToggle.textContent = isRevealed ? '🔒' : '👁';
                });
            }

            if (btnCopy && inputBox) {
                btnCopy.addEventListener('click', () => {
                    const rawKey = inputBox.getAttribute('data-raw');
                    navigator.clipboard.writeText(rawKey).then(() => {
                        showToast(`Chave de ${name} copiada!`, 'success');
                    });
                });
            }

            keysGrid.appendChild(card);
        });
    }

    // 4. Default Settings Loader
    async function loadDefaultSettings() {
        try {
            const res = await fetch('/api/setup/defaults');
            if (!res.ok) throw new Error('Falha ao obter defaults');
            defaultSettings = await res.json();
            populateForm(defaultSettings);
        } catch (err) {
            console.error('Erro ao carregar defaults:', err);
        }
    }

    function populateForm(cfg) {
        if (!cfg) return;
        
        const qbitHost = document.getElementById('qbit_host');
        if (qbitHost) qbitHost.value = cfg.qbit_host || 'qbittorrent';
        
        const qbitPort = document.getElementById('qbit_port');
        if (qbitPort) qbitPort.value = cfg.qbit_port || 8081;

        const qbitUser = document.getElementById('qbit_user');
        if (qbitUser) qbitUser.value = cfg.qbit_user || 'admin';

        const qbitPass = document.getElementById('qbit_password');
        if (qbitPass) qbitPass.value = cfg.qbit_password || 'adminadmin';

        const qbitMovieCat = document.getElementById('qbit_movie_category');
        if (qbitMovieCat) qbitMovieCat.value = cfg.qbit_movie_category || 'movies';

        const qbitTvCat = document.getElementById('qbit_tv_category');
        if (qbitTvCat) qbitTvCat.value = cfg.qbit_tv_category || 'tv';

        const qbitRemove = document.getElementById('qbit_remove_completed');
        if (qbitRemove) qbitRemove.checked = !!cfg.qbit_remove_completed;

        const radarrFolder = document.getElementById('radarr_root_folder');
        if (radarrFolder) radarrFolder.value = cfg.radarr_root_folder || '/data/media/movies';

        const sonarrFolder = document.getElementById('sonarr_root_folder');
        if (sonarrFolder) sonarrFolder.value = cfg.sonarr_root_folder || '/data/media/tv';

        const flareCheck = document.getElementById('flaresolverr_enabled');
        if (flareCheck) flareCheck.checked = !!cfg.flaresolverr_enabled;

        const defaultIndexers = cfg.prowlarr_indexers || ["1337x", "YTS", "The Pirate Bay", "TorrentGalaxy", "EZTV"];
        const checkboxes = document.querySelectorAll('input[name="prowlarr_indexers"]');
        checkboxes.forEach(cb => {
            cb.checked = defaultIndexers.includes(cb.value);
        });

        const bazarrLang = document.getElementById('bazarr_language');
        if (bazarrLang) bazarrLang.value = cfg.bazarr_language || 'pt-BR';

        const bazarrSubsync = document.getElementById('bazarr_ffsubsync');
        if (bazarrSubsync) bazarrSubsync.checked = !!cfg.bazarr_ffsubsync;
    }

    function getFormPayload() {
        const selectedIndexers = Array.from(document.querySelectorAll('input[name="prowlarr_indexers"]:checked')).map(cb => cb.value);

        return {
            radarr_root_folder: document.getElementById('radarr_root_folder') ? document.getElementById('radarr_root_folder').value : '/data/media/movies',
            sonarr_root_folder: document.getElementById('sonarr_root_folder') ? document.getElementById('sonarr_root_folder').value : '/data/media/tv',
            qbit_host: document.getElementById('qbit_host') ? document.getElementById('qbit_host').value : 'qbittorrent',
            qbit_port: document.getElementById('qbit_port') ? parseInt(document.getElementById('qbit_port').value) : 8081,
            qbit_user: document.getElementById('qbit_user') ? document.getElementById('qbit_user').value : 'admin',
            qbit_password: document.getElementById('qbit_password') ? document.getElementById('qbit_password').value : 'adminadmin',
            qbit_movie_category: document.getElementById('qbit_movie_category') ? document.getElementById('qbit_movie_category').value : 'movies',
            qbit_tv_category: document.getElementById('qbit_tv_category') ? document.getElementById('qbit_tv_category').value : 'tv',
            qbit_remove_completed: document.getElementById('qbit_remove_completed') ? document.getElementById('qbit_remove_completed').checked : true,
            flaresolverr_enabled: document.getElementById('flaresolverr_enabled') ? document.getElementById('flaresolverr_enabled').checked : true,
            flaresolverr_url: 'http://flaresolverr:8191',
            prowlarr_indexers: selectedIndexers,
            bazarr_language: document.getElementById('bazarr_language') ? document.getElementById('bazarr_language').value : 'pt-BR',
            bazarr_ffsubsync: document.getElementById('bazarr_ffsubsync') ? document.getElementById('bazarr_ffsubsync').checked : true
        };
    }

    if (btnResetDefaults) {
        btnResetDefaults.addEventListener('click', () => {
            populateForm(defaultSettings);
            showToast('Valores restaurados para o padrão recomendado.', 'info');
        });
    }

    const serviceMeta = {
        jellyfin: { icon: '🍿', port: 8096, label: 'Media Server', desc: 'Transmite filmes e séries para Smart TVs e celulares com transcodificação por hardware.' },
        qbittorrent: { icon: '📥', port: 8081, label: 'Download Client', desc: 'Executa os downloads de mídia via torrent e mantém seeding com Hardlinks atômicos.' },
        radarr: { icon: '🎬', port: 7878, label: 'Gerenciador Filmes', desc: 'Monitora lançamentos de filmes, seleciona qualidades desejadas e importa na biblioteca.' },
        sonarr: { icon: '📺', port: 8989, label: 'Gerenciador Séries', desc: 'Acompanha novas temporadas e episódios, organizando e renomeando por temporada.' },
        prowlarr: { icon: '🔍', port: 9696, label: 'Indexadores & Trackers', desc: 'Hub central que distribui seus indexadores e trackers para o Radarr e Sonarr em 1 só lugar.' },
        flaresolverr: { icon: '🛡️', port: 8191, label: 'Anti-Bot Proxy', desc: 'Proxy que resolve proteções Cloudflare para indexadores públicos funcionarem no Prowlarr.' },
        bazarr: { icon: '📝', port: 6767, label: 'Legendas Automáticas', desc: 'Busca legendas em pt-BR e sincroniza perfeitamente com o áudio original via ffsubsync.' },
        jellyseerr: { icon: '✨', port: 5055, label: 'Descoberta & Pedidos', desc: 'Portal visual moderno onde os usuários da casa buscam lançamentos e solicitam títulos.' }
    };

    async function loadHealthStatus(isManual = false) {
        if (isManual) {
            if (globalStatusText) globalStatusText.textContent = 'Checando rede...';
            if (globalStatusDot) globalStatusDot.className = 'status-dot pulsing';
        }

        try {
            const res = await fetch('/api/health');
            if (!res.ok) throw new Error('Falha na requisição de saúde');
            const data = await res.json();
            
            const onlineCount = data.total_online;
            const totalCount = data.total_services;
            
            if (globalStatusText) globalStatusText.textContent = `${onlineCount}/${totalCount} Serviços Online`;
            if (globalStatusDot) {
                globalStatusDot.className = `status-dot ${onlineCount === totalCount ? 'online' : ''}`;
            }

            renderServices(data.services);
        } catch (err) {
            console.error('Erro de saúde:', err);
            if (globalStatusText) globalStatusText.textContent = 'Erro ao conectar à API';
            if (globalStatusDot) globalStatusDot.className = 'status-dot';
        }
    }

    function renderServices(services) {
        if (!servicesGrid) return;
        servicesGrid.innerHTML = '';
        Object.entries(services).forEach(([name, s]) => {
            const card = document.createElement('div');
            card.className = 'service-card';
            
            const meta = serviceMeta[name] || { icon: '📦', port: '', label: 'Container', desc: 'Serviço da stack de mídia.' };
            const webLink = meta.port ? `http://${window.location.hostname}:${meta.port}` : s.url;
            
            let latencyClass = 'fast';
            if (s.latency_ms > 80) latencyClass = 'slow';
            else if (s.latency_ms > 35) latencyClass = 'medium';

            card.innerHTML = `
                <div class="service-card-header">
                    <div class="service-header-left">
                        <div class="service-avatar">${meta.icon}</div>
                        <div>
                            <div class="service-title">${s.name}</div>
                            <div style="font-size: 0.72rem; color: var(--text-muted);">${meta.label}</div>
                        </div>
                    </div>
                    <span class="service-latency-pill ${latencyClass}">
                        ${s.latency_ms ? s.latency_ms + 'ms' : '--'}
                    </span>
                </div>

                <div class="service-desc-box">
                    ${meta.desc}
                </div>

                <div class="service-url-box">
                    <span>${s.url}</span>
                    <span style="font-size: 0.7rem; color: var(--text-muted);">:${meta.port || ''}</span>
                </div>

                <div class="service-card-footer">
                    <span class="badge-status ${s.online ? 'online' : 'offline'}">
                        ● ${s.online ? 'ONLINE' : 'OFFLINE'}
                    </span>
                    <a href="${webLink}" target="_blank" rel="noopener noreferrer" class="service-open-btn">
                        Abrir WebUI ↗
                    </a>
                </div>
            `;
            servicesGrid.appendChild(card);
        });
    }

    // 6. Provisioning Execution
    function formatTime() {
        const d = new Date();
        return d.toTimeString().split(' ')[0];
    }

    async function executeProvisioning(url, payload, specificServiceName = null) {
        switchTab('wizard');
        const consoleCard = document.getElementById('consoleCard');
        if (consoleCard) {
            window.scrollTo({ top: consoleCard.offsetTop - 80, behavior: 'smooth' });
        }

        if (btnRunProvision) btnRunProvision.disabled = true;
        if (btnApplyCustom) btnApplyCustom.disabled = true;
        btnCardActions.forEach(b => b.disabled = true);

        const targetLabel = specificServiceName ? `no ${specificServiceName.toUpperCase()}` : 'na Stack Completa';
        if (consoleStatus) {
            consoleStatus.innerHTML = `<span class="status-dot pulsing"></span> Executando ${specificServiceName || 'tudo'}...`;
        }

        const now = formatTime();
        consoleBody.innerHTML = `<p class="log-line log-info"><span class="log-time">[${now}]</span> [START] Iniciando provisionamento ${targetLabel}...</p>`;

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: payload ? JSON.stringify(payload) : undefined
            });

            const data = await res.json();
            
            if (data.logs && data.logs.length > 0) {
                data.logs.forEach((item, index) => {
                    setTimeout(() => {
                        const line = document.createElement('p');
                        line.className = `log-line log-${item.status}`;
                        const prefix = item.status === 'success' ? '✓' : item.status === 'error' ? '✗' : 'ℹ';
                        const time = formatTime();
                        line.innerHTML = `<span class="log-time">[${time}]</span> <strong style="color: var(--primary-light);">[${item.service.toUpperCase()}]</strong> ${prefix} ${item.message}`;
                        consoleBody.appendChild(line);
                        consoleBody.scrollTop = consoleBody.scrollHeight;
                    }, index * 100);
                });
            }

            setTimeout(() => {
                const finalLine = document.createElement('p');
                finalLine.className = `log-line ${data.success ? 'log-success' : 'log-warning'}`;
                finalLine.style.fontWeight = 'bold';
                finalLine.style.marginTop = '12px';
                finalLine.style.padding = '8px';
                finalLine.style.background = 'rgba(255, 255, 255, 0.03)';
                finalLine.style.borderRadius = '6px';
                
                const time = formatTime();
                finalLine.innerHTML = data.success 
                    ? `<span class="log-time">[${time}]</span> 🎉 [SUCESSO] Provisionamento ${targetLabel} concluído com êxito!` 
                    : `<span class="log-time">[${time}]</span> ⚠️ [ATENÇÃO] Ocorreram avisos ou etapas incompletas ${targetLabel}.`;
                
                consoleBody.appendChild(finalLine);
                consoleBody.scrollTop = consoleBody.scrollHeight;

                if (consoleStatus) {
                    consoleStatus.innerHTML = `<span class="status-dot online"></span> Concluído`;
                }

                if (btnRunProvision) btnRunProvision.disabled = false;
                if (btnApplyCustom) btnApplyCustom.disabled = false;
                btnCardActions.forEach(b => b.disabled = false);

                showToast(data.success ? 'Provisionamento concluído com sucesso!' : 'Provisionamento finalizado com alertas.', data.success ? 'success' : 'error');
                loadHealthStatus();
            }, (data.logs ? data.logs.length : 1) * 110 + 350);

        } catch (err) {
            console.error('Erro no provisionamento:', err);
            const errLine = document.createElement('p');
            errLine.className = 'log-line log-error';
            const time = formatTime();
            errLine.innerHTML = `<span class="log-time">[${time}]</span> [ERRO CRÍTICO] Falha de comunicação: ${err.message}`;
            consoleBody.appendChild(errLine);
            
            if (consoleStatus) {
                consoleStatus.innerHTML = `<span class="status-dot" style="background: var(--danger)"></span> Erro`;
            }
            if (btnRunProvision) btnRunProvision.disabled = false;
            if (btnApplyCustom) btnApplyCustom.disabled = false;
            btnCardActions.forEach(b => b.disabled = false);

            showToast(`Falha de conexão: ${err.message}`, 'error');
        }
    }

    // Submit 1-Click Geral
    if (btnRunProvision) {
        btnRunProvision.addEventListener('click', () => {
            executeProvisioning('/api/provision/all', null);
        });
    }

    // Submit Custom Geral
    if (customConfigForm) {
        customConfigForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const customPayload = getFormPayload();
            executeProvisioning('/api/provision/custom', customPayload);
        });
    }

    // Submit Individual por Serviço
    btnCardActions.forEach(btn => {
        btn.addEventListener('click', () => {
            const serviceName = btn.getAttribute('data-service');
            if (!serviceName) return;
            const customPayload = getFormPayload();
            executeProvisioning(`/api/provision/service/${serviceName}`, customPayload, serviceName);
        });
    });

    // Console Action: Copiar Logs
    if (btnCopyLogs && consoleBody) {
        btnCopyLogs.addEventListener('click', () => {
            const text = consoleBody.innerText;
            navigator.clipboard.writeText(text).then(() => {
                showToast('Logs do terminal copiados para a área de transferência!', 'success');
            });
        });
    }

    // Console Action: Limpar Console
    if (btnClearLogs && consoleBody) {
        btnClearLogs.addEventListener('click', () => {
            const time = formatTime();
            consoleBody.innerHTML = `<p class="log-line log-info"><span class="log-time">[${time}]</span> Terminal limpo. Aguardando novos comandos.</p>`;
            if (consoleStatus) {
                consoleStatus.innerHTML = `<span class="status-dot"></span> Aguardando comando`;
            }
            showToast('Terminal limpo.', 'info');
        });
    }

    // Botão de Atualizar
    if (btnRefreshHealth) {
        btnRefreshHealth.addEventListener('click', () => {
            loadHealthStatus(true);
            loadDiscoveredKeys();
            showToast('Status e latência dos serviços atualizados!', 'info');
        });
    }

    // Toggle do Balão de Detalhes
    const btnToggleDetails = document.getElementById('btnToggleDetails');
    const setupDetailsBox = document.getElementById('setupDetailsBox');
    if (btnToggleDetails && setupDetailsBox) {
        btnToggleDetails.addEventListener('click', () => {
            setupDetailsBox.classList.toggle('closed');
        });
    }

    // Inicialização
    loadDiscoveredKeys();
    loadDefaultSettings();
    loadHealthStatus();

    const urlParams = new URLSearchParams(window.location.search);
    const initialTab = urlParams.get('tab');
    if (initialTab) {
        switchTab(initialTab);
    }
});
