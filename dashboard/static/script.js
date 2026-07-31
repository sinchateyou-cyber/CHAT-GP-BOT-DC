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
// VARIABLES
// ============================================================
let currentGuildId = null;
let guildsCache = [];
// ============================================================
// CARGAR USUARIO
// ============================================================
async function loadCurrentUser() {
    try {
        const response =
            await fetch(
                "/api/me"
            );
        if (!response.ok) {
            throw new Error(
                "No se pudo comprobar la sesión."
            );
        }
        const data =
            await response.json();
        const loginButton =
            document.getElementById(
                "login-button"
            );
        const loggedUser =
            document.getElementById(
                "logged-user"
            );
        const configLogin =
            document.getElementById(
                "config-login"
            );
        const configLogout =
            document.getElementById(
                "config-logout"
            );
        const accountInfo =
            document.getElementById(
                "account-info"
            );
        if (
            data.logged_in &&
            data.user
        ) {
            const user =
                data.user;
            const username =
                user.global_name ||
                user.username ||
                "Usuario";
            // =================================================
            // MOSTRAR USUARIO EN HEADER
            // =================================================
            if (loginButton) {
                loginButton.style.display =
                    "none";
            }
            if (loggedUser) {
                loggedUser.style.display =
                    "flex";
            }
            const userName =
                document.getElementById(
                    "user-name"
                );
            if (userName) {
                userName.textContent =
                    username;
            }
            // =================================================
            // AVATAR
            // =================================================
            const userAvatar =
                document.getElementById(
                    "user-avatar"
                );
            const sidebarAvatar =
                document.getElementById(
                    "sidebar-user-avatar"
                );
            let avatarUrl =
                "https://cdn.discordapp.com/embed/avatars/0.png";
            if (
                user.avatar &&
                user.id
            ) {
                avatarUrl =
                    `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png?size=128`;
            }
            if (userAvatar) {
                userAvatar.src =
                    avatarUrl;
            }
            if (sidebarAvatar) {
                sidebarAvatar.innerHTML = `
                    <img
                        src="${avatarUrl}"
                        alt="Avatar"
                    >
                `;
            }
            // =================================================
            // SIDEBAR
            // =================================================
            const sidebarUserName =
                document.getElementById(
                    "sidebar-user-name"
                );
            const sidebarUserStatus =
                document.getElementById(
                    "sidebar-user-status"
                );
            if (sidebarUserName) {
                sidebarUserName.textContent =
                    username;
            }
            if (sidebarUserStatus) {
                sidebarUserStatus.textContent =
                    "Conectado con Discord";
            }
            // =================================================
            // CONFIGURACIÓN
            // =================================================
            if (configLogin) {
                configLogin.style.display =
                    "none";
            }
            if (configLogout) {
                configLogout.style.display =
                    "inline-block";
            }
            if (accountInfo) {
                accountInfo.innerHTML = `
                    <div class="info-row">
                        <span>
                            Usuario
                        </span>
                        <strong>
                            ${escapeHtml(username)}
                        </strong>
                    </div>
                    <div class="info-row">
                        <span>
                            ID
                        </span>
                        <strong>
                            ${escapeHtml(
                                user.id || "N/A"
                            )}
                        </strong>
                    </div>
                `;
            }
        } else {
            // =================================================
            // USUARIO NO CONECTADO
            // =================================================
            if (loginButton) {
                loginButton.style.display =
                    "inline-block";
            }
            if (loggedUser) {
                loggedUser.style.display =
                    "none";
            }
            if (configLogin) {
                configLogin.style.display =
                    "inline-block";
            }
            if (configLogout) {
                configLogout.style.display =
                    "none";
            }
            const sidebarUserName =
                document.getElementById(
                    "sidebar-user-name"
                );
            const sidebarUserStatus =
                document.getElementById(
                    "sidebar-user-status"
                );
            if (sidebarUserName) {
                sidebarUserName.textContent =
                    "Invitado";
            }
            if (sidebarUserStatus) {
                sidebarUserStatus.textContent =
                    "No conectado";
            }
            if (accountInfo) {
                accountInfo.innerHTML = `
                    <p>
                        🔐 Iniciá sesión con Discord
                        para administrar tu cuenta.
                    </p>
                `;
            }
        }
    } catch (error) {
        console.error(
            "Error cargando usuario:",
            error
        );
    }
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
            } else {
                connectionStatus.innerHTML =
                    "🔴 Bot offline";
            }
        }
        // ====================================================
        // ESTADO
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
        // NOMBRE
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
            botLatency.textContent =
                data.latency !== null &&
                data.latency !== undefined
                    ? `${data.latency} ms`
                    : "N/A";
            }
        // ====================================================
        // INFORMACIÓN
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
        const statsGuilds =
            document.getElementById(
                "stats-guilds"
            );
        if (statsGuilds) {
            statsGuilds.textContent =
                data.guilds ||
                0;
        }
        const statsLatency =
            document.getElementById(
                "stats-latency"
            );
        if (statsLatency) {
            statsLatency.textContent =
                data.latency !== null
                    ? `${data.latency} ms`
                    : "N/A";
        }
    } catch (error) {
        console.error(
            "Error cargando estado:",
            error
        );
        const connectionStatus =
            document.getElementById(
                "connection-status"
            );
        if (connectionStatus) {
            connectionStatus.innerHTML =
                "🔴 Error de conexión";
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
    const guildSelect =
        document.getElementById(
            "security-guild-select"
        );
    try {
        const response =
            await fetch(
                "/api/guilds"
            );
        if (response.status === 401) {
            if (guildList) {
                guildList.innerHTML = `
                    <div class="loading">
                        🔐 Iniciá sesión con Discord
                        para ver tus servidores.
                    </div>
                `;
            }
            return;
        }
        if (!response.ok) {
            throw new Error(
                "No se pudieron obtener los servidores."
            );
        }
        const data =
            await response.json();
        if (
            !data.success ||
            !data.guilds
        ) {
            return;
        }
        guildsCache =
            data.guilds;
        // ====================================================
        // LISTA DE SERVIDORES
        // ====================================================
        if (guildList) {
            guildList.innerHTML =
                "";
        }
        // ====================================================
        // SELECT DE SEGURIDAD
        // ====================================================
        if (guildSelect) {
            guildSelect.innerHTML = `
                <option value="">
                    Seleccioná un servidor...
                </option>
            `;
        }
        data.guilds.forEach(
            guild => {
                // ==========================================
                // TARJETA
                // ==========================================
                if (guildList) {
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
                                alt="Icono"
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
                        <button
                            class="security-button"
                            onclick="selectGuild('${guild.id}')"
                        >
                            ⚙️ Configurar
                        </button>
                    `;
                    guildList.appendChild(
                        card
                    );
                }
                // ==========================================
                // SELECT
                // ==========================================
                if (guildSelect) {
                    const option =
                        document.createElement(
                            "option"
                        );
                    option.value =
                        guild.id;
                    option.textContent =
                        guild.name;
                    guildSelect.appendChild(
                        option
                    );
                }
            }
        );
    } catch (error) {
        console.error(
            "Error cargando servidores:",
            error
        );
        if (guildList) {
            guildList.innerHTML = `
                <div class="loading">
                    ❌ No se pudieron cargar
                    los servidores.
                </div>
            `;
        }
    }
}
// ============================================================
// SELECCIONAR SERVIDOR
// ============================================================
function selectGuild(
    guildId
) {
    currentGuildId =
        guildId;
    const guildSelect =
        document.getElementById(
            "security-guild-select"
        );
    if (guildSelect) {
        guildSelect.value =
            guildId;
    }
    showSection(
        "seguridad"
    );
    loadSecurityConfig();
}
// ============================================================
// CAMBIO DE SERVIDOR
// ============================================================
document.addEventListener(
    "DOMContentLoaded",
    () => {
        const guildSelect =
            document.getElementById(
                "security-guild-select"
            );
        if (guildSelect) {
            guildSelect.addEventListener(
                "change",
                () => {
                    currentGuildId =
                        guildSelect.value ||
                        null;
                    if (
                        currentGuildId
                    ) {
                        loadSecurityConfig();
                    } else {
                        hideSecurityControls();
                    }
                }
            );
        }
    }
);
// ============================================================
// CARGAR CONFIGURACIÓN DE SEGURIDAD
// ============================================================
async function loadSecurityConfig() {
    if (!currentGuildId) {
        hideSecurityControls();
        return;
    }
    try {
        const response =
            await fetch(
                `/api/security/${currentGuildId}`
            );
        if (response.status === 401) {
            showSecurityMessage(
                "🔐 Debes iniciar sesión con Discord.",
                "error"
            );
            hideSecurityControls();
            return;
        }
        if (response.status === 403) {
            showSecurityMessage(
                "🚫 No tienes permisos para administrar este servidor.",
                "error"
            );
            hideSecurityControls();
            return;
        }
        if (!response.ok) {
            throw new Error(
                "No se pudo cargar la configuración."
            );
        }
        const data =
            await response.json();
        if (!data.success) {
            showSecurityMessage(
                data.message ||
                "No se pudo cargar la configuración.",
                "error"
            );
            hideSecurityControls();
            return;
        }
        showSecurityControls();
        updateSecurityButton(
            "antispam",
            data.security.antispam
        );
        updateSecurityButton(
            "antiflood",
            data.security.antiflood
        );
        updateSecurityButton(
            "antilink",
            data.security.antilink
        );
        showSecurityMessage(
            "✅ Configuración cargada correctamente.",
            "success"
        );
    } catch (error) {
        console.error(
            "Error cargando seguridad:",
            error
        );
        showSecurityMessage(
            "❌ Error al cargar la configuración.",
            "error"
        );
    }
}
// ============================================================
// ACTIVAR / DESACTIVAR SEGURIDAD
// ============================================================
async function toggleSecurity(
    type
) {
    if (!currentGuildId) {
        showSecurityMessage(
            "⚠️ Primero seleccioná un servidor.",
            "error"
        );
        return;
    }
    const button =
        document.getElementById(
            `${type}-toggle`
        );
    const status =
        document.getElementById(
            `${type}-status`
        );
    const currentlyEnabled =
        status &&
        status.dataset.enabled ===
        "true";
    const newState =
        !currentlyEnabled;
    if (button) {
        button.disabled =
            true;
        button.textContent =
            "Guardando...";
    }
    try {
        const response =
            await fetch(
                `/api/security/${currentGuildId}/${type}`,
                {
                    method:
                        "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body:
                        JSON.stringify({
                            enabled:
                                newState
                        })
                }
            );
        const data =
            await response.json();
        if (!response.ok) {
            throw new Error(
                data.message ||
                "No se pudo cambiar la configuración."
            );
        }
        updateSecurityButton(
            type,
            data.enabled
        );
        showSecurityMessage(
            data.enabled
                ? `✅ ${type} activado correctamente.`
                : `🔴 ${type} desactivado correctamente.`,
            "success"
        );
    } catch (error) {
        console.error(
            "Error cambiando seguridad:",
            error
        );
        showSecurityMessage(
            `❌ ${error.message}`,
            "error"
        );
        if (button) {
            button.textContent =
                currentlyEnabled
                    ? "Desactivar"
                    : "Activar";
        }
    } finally {
        if (button) {
            button.disabled =
                false;
        }
    }
}
// ============================================================
// ACTUALIZAR BOTÓN
// ============================================================
function updateSecurityButton(
    type,
    enabled
) {
    const button =
        document.getElementById(
            `${type}-toggle`
        );
    const status =
        document.getElementById(
            `${type}-status`
        );
    if (status) {
        status.dataset.enabled =
            enabled
                ? "true"
                : "false";
        status.textContent =
            enabled
                ? "Activado"
                : "Desactivado";
    }
    if (button) {
        button.textContent =
            enabled
                ? "Desactivar"
                : "Activar";
    }
}
// ============================================================
// MOSTRAR CONTROLES
// ============================================================
function showSecurityControls() {
    const controls =
        document.getElementById(
            "security-controls"
        );
    if (controls) {
        controls.style.display =
            "block";
    }
}
// ============================================================
// OCULTAR CONTROLES
// ============================================================
function hideSecurityControls() {
    const controls =
        document.getElementById(
            "security-controls"
        );
    if (controls) {
        controls.style.display =
            "none";
    }
}
// ============================================================
// MENSAJES
// ============================================================
function showSecurityMessage(
    message,
    type
) {
    const element =
        document.getElementById(
            "security-message"
        );
    if (!element) {
        return;
    }
    element.textContent =
        message;
    element.className =
        `security-message ${type}`;
}
// ============================================================
// SEGURIDAD HTML
// ============================================================
function escapeHtml(
    text
) {
    const div =
        document.createElement(
            "div"
        );
    div.textContent =
        text;
    return div.innerHTML;
}
// ============================================================
// ACTUALIZAR DASHBOARD
// ============================================================
async function updateDashboard() {
    await loadCurrentUser();
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
        setInterval(
            updateDashboard,
            30000
        );
    }
);