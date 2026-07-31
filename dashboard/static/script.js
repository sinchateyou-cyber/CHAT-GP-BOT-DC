// ============================================================
// DASHBOARD DEL BOT
// ============================================================
// ============================================================
// CAMBIAR DE SECCIÓN
// ============================================================
function showSection(sectionId) {
    const sections =
        document.querySelectorAll(
            ".section"
        );
    sections.forEach(
        section => {
            section.classList.remove(
                "active-section"
            );
        }
    );
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
    buttons.forEach(
        button => {
            button.classList.remove(
                "active"
            );
        }
    );
    buttons.forEach(
        button => {
            if (
                button.getAttribute(
                    "onclick"
                )
                ===
                `showSection('${sectionId}')`
            ) {
                button.classList.add(
                    "active"
                );
            }
        }
    );
}
// ============================================================
// CARGAR USUARIO LOGUEADO
// ============================================================
async function loadUser() {
    try {
        const response =
            await fetch(
                "/api/me"
            );
        if (!response.ok) {
            throw new Error(
                "No se pudo obtener el usuario."
            );
        }
        const data =
            await response.json();
        const userName =
            document.getElementById(
                "user-name"
            );
        const userStatus =
            document.getElementById(
                "user-status"
            );
        const userAvatar =
            document.getElementById(
                "user-avatar"
            );
        const loginButton =
            document.getElementById(
                "login-button"
            );
        const logoutButton =
            document.getElementById(
                "logout-button"
            );
        // ====================================================
        // USUARIO LOGUEADO
        // ====================================================
        if (
            data.logged_in &&
            data.user
        ) {
            const user =
                data.user;
            if (userName) {
                userName.textContent =
                    user.global_name ||
                    user.username ||
                    "Usuario";
            }
            if (userStatus) {
                userStatus.textContent =
                    "🟢 Conectado";
            }
            if (loginButton) {
                loginButton.style.display =
                    "none";
            }
            if (logoutButton) {
                logoutButton.style.display =
                    "block";
            }
            // =================================================
            // AVATAR DE DISCORD
            // =================================================
            if (
                userAvatar &&
                user.id &&
                user.avatar
            ) {
                userAvatar.innerHTML = `
                    <img
                        src="https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png"
                        alt="Avatar de Discord"
                        class="user-avatar-image"
                    >
                `;
            }
        }
        // ====================================================
        // USUARIO NO LOGUEADO
        // ====================================================
        else {
            if (userName) {
                userName.textContent =
                    "Invitado";
            }
            if (userStatus) {
                userStatus.textContent =
                    "🔴 No conectado";
            }
            if (loginButton) {
                loginButton.style.display =
                    "block";
            }
            if (logoutButton) {
                logoutButton.style.display =
                    "none";
            }
        }
        return data.logged_in === true;
    }
    catch (error) {
        console.error(
            "Error cargando usuario:",
            error
        );
        return false;
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
                "No se pudo obtener " +
                "el estado del bot."
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
            }
            else {
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
        // CANTIDAD DE SERVIDORES
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
            }
            else {
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
    }
    catch (error) {
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
        // ====================================================
        // COMPROBAR LOGIN
        // ====================================================
        const userResponse =
            await fetch(
                "/api/me"
            );
        const userData =
            await userResponse.json();
        // ====================================================
        // NO LOGUEADO
        // ====================================================
        if (
            !userData.logged_in
        ) {
            guildList.innerHTML = `
                <div class="loading">
                    🔐
                    <br><br>
                    Necesitás iniciar sesión
                    con Discord para ver
                    tus servidores.
                    <br><br>
                    <a
                        href="/login"
                        class="login-button"
                    >
                        🔐 Iniciar sesión con Discord
                    </a>
                </div>
            `;
            return;
        }
        // ====================================================
        // SOLICITAR SERVIDORES
        // ====================================================
        const response =
            await fetch(
                "/api/guilds"
            );
        // ====================================================
        // SESIÓN NO AUTORIZADA
        // ====================================================
        if (
            response.status === 401
        ) {
            guildList.innerHTML = `
                <div class="loading">
                    🔐
                    <br><br>
                    Tu sesión expiró.
                    <br><br>
                    <a
                        href="/login"
                        class="login-button"
                    >
                        Iniciar sesión nuevamente
                    </a>
                </div>
            `;
            return;
        }
        if (!response.ok) {
            throw new Error(
                "No se pudieron obtener " +
                "los servidores."
            );
        }
        const data =
            await response.json();
        // ====================================================
        // SIN SERVIDORES
        // ====================================================
        if (
            !data.success ||
            !data.guilds ||
            data.guilds.length === 0
        ) {
            guildList.innerHTML = `
                <div class="loading">
                    🤖
                    <br><br>
                    El bot no está
                    en ningún servidor.
                </div>
            `;
            return;
        }
        // ====================================================
        // LIMPIAR LISTA
        // ====================================================
        guildList.innerHTML = "";
        // ====================================================
        // CREAR TARJETAS
        // ====================================================
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
                            src="${escapeHtml(icon)}"
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
                    <div class="guild-actions">
                        <button
                            class="configure-button"
                            onclick="configureGuild('${guild.id}')"
                        >
                            ⚙️ Configurar
                        </button>
                    </div>
                `;
                guildList.appendChild(
                    card
                );
            }
        );
    }
    catch (error) {
        console.error(
            "Error cargando servidores:",
            error
        );
        guildList.innerHTML = `
            <div class="loading">
                ❌
                <br><br>
                No se pudieron cargar
                los servidores.
            </div>
        `;
    }
}
// ============================================================
// CONFIGURAR SERVIDOR
// ============================================================
function configureGuild(
    guildId
) {
    // Guardar servidor seleccionado
    localStorage.setItem(
        "selectedGuild",
        guildId
    );
    // Ir a configuración
    showSection(
        "configuracion"
    );
    // Cargar información
    loadGuildInfo(
        guildId
    );
}
// ============================================================
// CARGAR INFORMACIÓN DEL SERVIDOR
// ============================================================
async function loadGuildInfo(
    guildId
) {
    const configSection =
        document.getElementById(
            "configuracion"
        );
    if (!configSection) {
        return;
    }
    try {
        const response =
            await fetch(
                `/api/guild/${guildId}`
            );
        if (
            response.status === 401
        ) {
            window.location.href =
                "/login";
            return;
        }
        if (!response.ok) {
            throw new Error(
                "No se pudo obtener " +
                "la información del servidor."
            );
        }
        const data =
            await response.json();
        if (
            !data.success ||
            !data.guild
        ) {
            throw new Error(
                "Servidor no encontrado."
            );
        }
        const guild =
            data.guild;
        // ====================================================
        // MOSTRAR INFORMACIÓN
        // ====================================================
        configSection.innerHTML = `
            <div class="section-header">
                <h2>
                    ⚙️ ${escapeHtml(
                        guild.name
                    )}
                </h2>
                <p>
                    Configuración del servidor
                </p>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">
                        👥
                    </div>
                    <div>
                        <span>
                            Miembros
                        </span>
                        <strong>
                            ${guild.member_count || 0}
                        </strong>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">
                        📁
                    </div>
                    <div>
                        <span>
                            Canales
                        </span>
                        <strong>
                            ${guild.channel_count || 0}
                        </strong>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">
                        🎭
                    </div>
                    <div>
                        <span>
                            Roles
                        </span>
                        <strong>
                            ${guild.role_count || 0}
                        </strong>
                    </div>
                </div>
            </div>
            <div class="panel">
                <h2>
                    🛠️ Módulos del bot
                </h2>
                <p>
                    Próximamente podrás
                    configurar los módulos
                    de tu bot desde aquí.
                </p>
                <div class="module-grid">
                    <button class="module-button">
                        👋 Bienvenida
                    </button>
                    <button class="module-button">
                        🛡️ Anti-Spam
                    </button>
                    <button class="module-button">
                        🔗 Anti-Links
                    </button>
                    <button class="module-button">
                        🌊 Anti-Flood
                    </button>
                    <button class="module-button">
                        📝 Logs
                    </button>
                    <button class="module-button">
                        🎫 Tickets
                    </button>
                    <button class="module-button">
                        🔒 Verificación
                    </button>
                    <button class="module-button">
                        🎭 Roles
                    </button>
                </div>
            </div>
        `;
    }
    catch (error) {
        console.error(
            "Error cargando servidor:",
            error
        );
        configSection.innerHTML = `
            <div class="loading">
                ❌
                <br><br>
                No se pudo cargar
                la configuración.
            </div>
        `;
    }
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
// ACTUALIZAR TODO EL DASHBOARD
// ============================================================
async function updateDashboard() {
    await loadUser();
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
        // ====================================================
        // ACTUALIZAR AUTOMÁTICAMENTE
        // ====================================================
        setInterval(
            updateDashboard,
            30000
        );
    }
);