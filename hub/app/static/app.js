document.addEventListener('DOMContentLoaded', () => {
    // Referências aos elementos da DOM
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

    const customConfigForm = document.getElementById('customConfigForm');
    const btnResetDefaults = document.getElementById('btnResetDefaults');
    const btnApplyCustom = document.getElementById('btnApplyCustom');
    const btnCardActions = document.querySelectorAll('.btn-card-action');

    let discoveredKeys = {};
    let defaultSettings = {};

    // 1. Gerenciador de Abas
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

    // 2. Buscar API Keys Descobertas
    async function loadDiscoveredKeys() {
        try {
            const res = await fetch('/api/discovery');
            if (!res.ok) throw new Error('Falha ao obter chaves');
            discoveredKeys = await res.json();
            
            renderQuickKeys();
            renderFullKeys();
        } catch (err) {
            console.error('Erro ao carregar chaves:', err);
            quickKeyStatusList.innerHTML = `<p class="text-danger">Erro ao carregar chaves do host.</p>`;
        }
    }

    function renderQuickKeys() {
        quickKeyStatusList.innerHTML = '';
        Object.entries(discoveredKeys).forEach(([name, data]) => {
            const div = document.createElement('div');
            div.className = 'key-status-item';
            div.innerHTML = `
                <span class="key-name">${name}</span>
                <span class="key-badge ${data.found ? 'found' : 'missing'}">
                    ${data.found ? '✓ Carregada' : '✗ Ausente'}
                </span>
            `;
            quickKeyStatusList.appendChild(div);
        });
    }

    function renderFullKeys() {
        keysGrid.innerHTML = '';
        Object.entries(discoveredKeys).forEach(([name, data]) => {
            const card = document.createElement('div');
            card.className = 'key-card';
            card.innerHTML = `
                <h3>${name}</h3>
                <p class="key-file-path">${data.configFile || 'Arquivo não encontrado'}</p>
                <div class="key-input-box">
                    ${data.apiKey ? data.apiKey : '<em>Nenhuma chave detectada</em>'}
                </div>
            `;
            keysGrid.appendChild(card);
        });
    }

    // 3. Buscar e Preencher Configurações Padrão
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
        
        document.getElementById('qbit_host').value = cfg.qbit_host || 'qbittorrent';
        document.getElementById('qbit_port').value = cfg.qbit_port || 8081;
        document.getElementById('qbit_user').value = cfg.qbit_user || 'admin';
        document.getElementById('qbit_password').value = cfg.qbit_password || 'adminadmin';
        document.getElementById('qbit_movie_category').value = cfg.qbit_movie_category || 'movies';
        document.getElementById('qbit_tv_category').value = cfg.qbit_tv_category || 'tv';
        document.getElementById('qbit_remove_completed').checked = !!cfg.qbit_remove_completed;

        document.getElementById('radarr_root_folder').value = cfg.radarr_root_folder || '/data/media/movies';
        document.getElementById('sonarr_root_folder').value = cfg.sonarr_root_folder || '/data/media/tv';

        document.getElementById('flaresolverr_enabled').checked = !!cfg.flaresolverr_enabled;

        const defaultIndexers = cfg.prowlarr_indexers || ["1337x", "YTS", "The Pirate Bay", "TorrentGalaxy", "EZTV"];
        const checkboxes = document.querySelectorAll('input[name="prowlarr_indexers"]');
        checkboxes.forEach(cb => {
            cb.checked = defaultIndexers.includes(cb.value);
        });

        document.getElementById('bazarr_language').value = cfg.bazarr_language || 'pt-BR';
        document.getElementById('bazarr_ffsubsync').checked = !!cfg.bazarr_ffsubsync;
    }

    function getFormPayload() {
        const selectedIndexers = Array.from(document.querySelectorAll('input[name="prowlarr_indexers"]:checked')).map(cb => cb.value);

        return {
            radarr_root_folder: document.getElementById('radarr_root_folder').value,
            sonarr_root_folder: document.getElementById('sonarr_root_folder').value,
            qbit_host: document.getElementById('qbit_host').value,
            qbit_port: parseInt(document.getElementById('qbit_port').value),
            qbit_user: document.getElementById('qbit_user').value,
            qbit_password: document.getElementById('qbit_password').value,
            qbit_movie_category: document.getElementById('qbit_movie_category').value,
            qbit_tv_category: document.getElementById('qbit_tv_category').value,
            qbit_remove_completed: document.getElementById('qbit_remove_completed').checked,
            flaresolverr_enabled: document.getElementById('flaresolverr_enabled').checked,
            flaresolverr_url: 'http://flaresolverr:8191',
            prowlarr_indexers: selectedIndexers,
            bazarr_language: document.getElementById('bazarr_language').value,
            bazarr_ffsubsync: document.getElementById('bazarr_ffsubsync').checked
        };
    }

    btnResetDefaults.addEventListener('click', () => {
        populateForm(defaultSettings);
    });

    // 4. Buscar Status de Saúde dos Serviços
    async function loadHealthStatus() {
        globalStatusText.textContent = 'Checando serviços...';
        globalStatusDot.className = 'status-dot pulsing';

        try {
            const res = await fetch('/api/health');
            if (!res.ok) throw new Error('Falha na requisição de saúde');
            const data = await res.json();
            
            const onlineCount = data.total_online;
            const totalCount = data.total_services;
            
            globalStatusText.textContent = `${onlineCount}/${totalCount} Serviços Online`;
            globalStatusDot.className = `status-dot ${onlineCount === totalCount ? 'online' : ''}`;

            renderServices(data.services);
        } catch (err) {
            console.error('Erro de saúde:', err);
            globalStatusText.textContent = 'Erro ao conectar à API';
            globalStatusDot.className = 'status-dot';
        }
    }

    const hostPortMapping = {
        jellyfin: 8096,
        qbittorrent: 8081,
        radarr: 7878,
        sonarr: 8989,
        prowlarr: 9696,
        flaresolverr: 8191,
        bazarr: 6767,
        jellyseerr: 5055
    };

    function renderServices(services) {
        servicesGrid.innerHTML = '';
        Object.entries(services).forEach(([name, s]) => {
            const card = document.createElement('div');
            card.className = 'service-card';
            
            const hostPort = hostPortMapping[name] || '';
            const webLink = hostPort ? `http://${window.location.hostname}:${hostPort}` : s.url;

            card.innerHTML = `
                <div class="service-card-header">
                    <span class="service-title">${s.name}</span>
                    <span class="service-latency">${s.latency_ms ? s.latency_ms + 'ms' : '--'}</span>
                </div>
                <div class="service-url">${s.url}</div>
                <div class="service-card-footer">
                    <span class="badge-status ${s.online ? 'online' : 'offline'}">
                        ${s.online ? 'ONLINE' : 'OFFLINE'}
                    </span>
                    <a href="${webLink}" target="_blank" class="btn btn-secondary" style="padding: 0.25rem 0.6rem; font-size: 0.75rem;">
                        Abrir WebUI ↗
                    </a>
                </div>
            `;
            servicesGrid.appendChild(card);
        });
    }

    // 5. Execução do Provisionamento (1-Click, Custom ou Single-Service)
    async function executeProvisioning(url, payload, specificServiceName = null) {
        switchTab('wizard');
        window.scrollTo({ top: document.getElementById('consoleCard').offsetTop - 100, behavior: 'smooth' });

        btnRunProvision.disabled = true;
        btnApplyCustom.disabled = true;
        btnCardActions.forEach(b => b.disabled = true);

        const targetLabel = specificServiceName ? `no ${specificServiceName.toUpperCase()}` : 'na Stack';
        consoleStatus.textContent = `Modificando ${specificServiceName || 'todos'}...`;
        consoleBody.innerHTML = `<p class="log-line text-muted">[START] Iniciando atualização ${targetLabel}...</p>`;

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
                        line.textContent = `[${item.service.toUpperCase()}] ${prefix} ${item.message}`;
                        consoleBody.appendChild(line);
                        consoleBody.scrollTop = consoleBody.scrollHeight;
                    }, index * 120);
                });
            }

            setTimeout(() => {
                const finalLine = document.createElement('p');
                finalLine.className = `log-line ${data.success ? 'log-success' : 'log-warning'}`;
                finalLine.style.fontWeight = 'bold';
                finalLine.style.marginTop = '10px';
                finalLine.textContent = data.success 
                    ? `🎉 [SUCESSO] Configuração ${targetLabel} concluída com êxito!` 
                    : `⚠️ [ATENÇÃO] Alguma etapa ${targetLabel} apresentou avisos ou erros.`;
                consoleBody.appendChild(finalLine);
                consoleBody.scrollTop = consoleBody.scrollHeight;

                consoleStatus.textContent = 'Concluído';
                btnRunProvision.disabled = false;
                btnApplyCustom.disabled = false;
                btnCardActions.forEach(b => b.disabled = false);

                loadHealthStatus();
            }, (data.logs ? data.logs.length : 1) * 130 + 300);

        } catch (err) {
            console.error('Erro no provisionamento:', err);
            const errLine = document.createElement('p');
            errLine.className = 'log-line log-error';
            errLine.textContent = `[ERRO FATAL] Falha de comunicação com o backend: ${err.message}`;
            consoleBody.appendChild(errLine);
            
            consoleStatus.textContent = 'Erro';
            btnRunProvision.disabled = false;
            btnApplyCustom.disabled = false;
            btnCardActions.forEach(b => b.disabled = false);
        }
    }

    // Submit 1-Click Geral
    btnRunProvision.addEventListener('click', () => {
        executeProvisioning('/api/provision/all', null);
    });

    // Submit Custom Geral
    customConfigForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const customPayload = getFormPayload();
        executeProvisioning('/api/provision/custom', customPayload);
    });

    // Submit Individual por Serviço
    btnCardActions.forEach(btn => {
        btn.addEventListener('click', () => {
            const serviceName = btn.getAttribute('data-service');
            if (!serviceName) return;
            const customPayload = getFormPayload();
            executeProvisioning(`/api/provision/service/${serviceName}`, customPayload, serviceName);
        });
    });

    // 6. Botão de Atualizar
    btnRefreshHealth.addEventListener('click', () => {
        loadHealthStatus();
        loadDiscoveredKeys();
    });

    // Inicialização
    loadDiscoveredKeys();
    loadDefaultSettings();
    loadHealthStatus();
});
