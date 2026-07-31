// ============================================================
// DASHBOARD DEL BOT
// ============================================================
// ============================================================
// CAMBIAR DE SECCIÓN
// ============================================================
function showSection(sectionId) {
    const sections =
        document.querySelectorAll(".section");
    sections.forEach(section => {
        section.classList.remove(
            "active-section"
        );
    });
    const selectedSection =
        document.getElementById(
            sectionId
        );
    if (selectedSection) {
        selectedSection.classList.add(
            "active-section"
        );
    }
    const buttons =
        document.querySelectorAll(
            ".menu-item"
        );
    buttons.forEach(button => {
        button.classList.remove(
            "active"
        );
    });
    buttons.forEach(button => {
        if (
            button.getAttribute(
                "onclick"
            ) ===
            `showSection('${sectionId}')`
        ) {
            button.classList.add(
                "active"
            );
        }
    });
}
// ============================================================
// CARGAR ESTADO DEL BOT
// ============================================================
async function loadBotStatus() {
    try {
        const response =
            await fetch(
                "/api/status"
            );
        if (!response.ok) {
            throw new Error(
                "No se pudo obtener el estado del bot."
            );
        }
        const data =
            await response.json();
        // ====================================================
        // ESTADO DE CONEXIÓN
        // ====================================================
        const connectionStatus =
            document.getElementById(
                "connection-status"
            );
        if (connectionStatus) {
            if (data.online) {
                connectionStatus.innerHTML =
                    "🟢 Bot online";
                connectionStatus.style.color =
                    "#43e97b";
            } else {
                connectionStatus.innerHTML =
                    "🔴 Bot offline";
                connectionStatus.style.color =
                    "#ff5c5c";
            }
        }
        // ====================================================
        // ESTADO DEL BOT
        // ====================================================
        const botStatus =
            document.getElementById(
                "bot-status"
            );
        if (botStatus) {
            botStatus.textContent =
                data.online
                    ? "Online"
                    : "Offline";
        }
        // ====================================================
        // NOMBRE DEL BOT
        // ====================================================
        const botName =
            document.getElementById(
                "bot-name"
            );
        if (botName) {
            botName.textContent =
                data.bot ||
                "Desconocido";
        }
        // ====================================================
        // SERVIDORES
        // ====================================================
        const guildCount =
            document.getElementById(
                "guild-count"
            );
        if (guildCount) {
            guildCount.textContent =
                data.guilds ||
                0;
        }
        // ====================================================
        // LATENCIA
        // ====================================================
        const botLatency =
            document.getElementById(
                "bot-latency"
            );
        if (botLatency) {
            if (
                data.latency !== null &&
                data.latency !== undefined
            ) {
                botLatency.textContent =
                    `${data.latency} ms`;
            } else {
                botLatency.textContent =
                    "N/A";
            }
        }
        // ====================================================
        // INFORMACIÓN DEL BOT
        // ====================================================
        const infoBotName =
            document.getElementById(
                "info-bot-name"
            );
        if (infoBotName) {
            infoBotName.textContent =
                data.bot ||
                "Desconocido";
        }
        const infoBotId =
            document.getElementById(
                "info-bot-id"
            );
        if (infoBotId) {
            infoBotId.textContent =
                data.bot_id ||
                "N/A";
        }
        const infoBotStatus =
            document.getElementById(
                "info-bot-status"
            );
        if (infoBotStatus) {
            infoBotStatus.textContent =
                data.online
                    ? "Online"
                    : "Offline";
        }
        // ====================================================
        // ESTADÍSTICAS
        // ====================================================
        const statsGuilds =
            document.getElementById(
                "stats-guilds"
            );
        if (statsGuilds) {
            statsGuilds.textContent =
                data.guilds ||
                0;
        }
    } catch (error) {
        console.error(
            "Error cargando el estado:",
            error
        );
        const connectionStatus =
            document.getElementById(
                "connection-status"
            );
        if (connectionStatus) {
            connectionStatus.innerHTML =
                "🔴 Error de conexión";
            connectionStatus.style.color =
                "#ff5c5c";
        }
    }
}
// ============================================================
// CARGAR SERVIDORES
// ============================================================
async function loadGuilds() {
    const guildList =
        document.getElementById(
            "guild-list"
        );
    if (!guildList) {
        return;
    }
    try {
        const response =
            await fetch(
                "/api/guilds"
            );
        if (!response.ok) {
            throw new Error(
                "No se pudieron obtener los servidores."
            );
        }
        const data =
            await response.json();
        if (
            !data.success ||
            !data.guilds ||
            data.guilds.length === 0
        ) {
            guildList.innerHTML = `
                <div class="loading">
                    🤖 El bot no está
                    en ningún servidor.
                </div>
            `;
            return;
        }
        // Limpiar lista
        guildList.innerHTML = "";
        // Crear tarjetas
        data.guilds.forEach(
            guild => {
                const card =
                    document.createElement(
                        "div"
                    );
                card.className =
                    "guild-card";
                const icon =
                    guild.icon ||
                    "https://cdn.discordapp.com/embed/avatars/0.png";
                card.innerHTML = `
                    <div class="guild-header">
                        <img
                            class="guild-icon"
                            src="${icon}"
                            alt="Icono del servidor"
                        >
                        <div>
                            <div class="guild-name">
                                ${escapeHtml(
                                    guild.name
                                )}
                            </div>
                            <div class="guild-members">
                                👥
                                ${guild.member_count || 0}
                                miembros
                            </div>
                        </div>
                    </div>
                `;
                guildList.appendChild(
                    card
                );
            }
        );
    } catch (error) {
        console.error(
            "Error cargando servidores:",
            error
        );
        guildList.innerHTML = `
            <div class="loading">
                ❌ No se pudieron cargar
                los servidores.
            </div>
        `;
    }
}
// ============================================================
// SEGURIDAD HTML
// ============================================================
function escapeHtml(text) {
    const div =
        document.createElement(
            "div"
        );
    div.textContent =
        text;
    return div.innerHTML;
}
// ============================================================
// ACTUALIZAR TODO EL DASHBOARD
// ============================================================
async function updateDashboard() {
    await loadBotStatus();
    await loadGuilds();
}
// ============================================================
// INICIAR DASHBOARD
// ============================================================
document.addEventListener(
    "DOMContentLoaded",
    () => {
        updateDashboard();
        // Actualizar automáticamente
        // cada 30 segundos
        setInterval(
            updateDashboard,
            30000
        );
    }
);