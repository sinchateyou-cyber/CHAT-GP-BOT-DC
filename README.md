🤖 Fire Nation Bot

Un bot de Discord moderno, completo y diseñado para la administración y gestión de servidores.

<p align="center">
  <strong>Moderación • Seguridad • Utilidades • Roles • Automatización</strong>
</p>

⸻

✨ Características

Fire Nation Bot ofrece un conjunto de herramientas para mejorar la administración y experiencia de los servidores de Discord.

🛡️ Moderación

* /clear — Elimina mensajes del canal.
* /kick — Expulsa usuarios.
* /ban — Banea usuarios.
* /unban — Desbanea usuarios mediante ID.
* /timeout — Aplica un timeout.
* /untimeout — Quita un timeout.
* /lock — Bloquea un canal.
* /unlock — Desbloquea un canal.

👑 Sistema de Owner

* Sistema de propietario del bot.
* Designación de un nuevo Owner.
* Identificación del Owner mediante ID.
* Acceso especial del Owner a funciones administrativas.

🎫 Sistemas

* Sistema de tickets.
* Sistema de verificación.
* Sistema AFK.
* Sistema de bienvenida.
* Sistema de logs.
* Sistema anti-spam.

🎭 Roles

* Gestión de roles.
* Automatización de roles.
* Herramientas para administración de miembros.

🔧 Utilidades

* Comandos de utilidad.
* Gestión de canales.
* Comandos personalizados.
* Sistema de invitaciones.
* Sistema de ayuda.
* Gestión de nombres de usuarios.

⸻

📁 Estructura del proyecto

Fire-Nation-Bot/
│
├── bot.py
├── config.py
├── owner.json
├── LICENSE
├── README.md
│
└── cogs/
    ├── moderacion.py
    ├── owner.py
    ├── afk.py
    ├── bienvenida.py
    ├── logs.py
    ├── tickets.py
    ├── verificado.py
    ├── antispam.py
    ├── utilidades.py
    ├── canales.py
    ├── say.py
    ├── nick.py
    ├── roles.py
    ├── status.py
    ├── invite.py
    └── help.py

⸻

⚙️ Requisitos

Para ejecutar Fire Nation Bot necesitás:

* Python 3.10 o superior.
* discord.py.
* Una aplicación creada en Discord Developer Portal.
* Un servidor de Discord.
* Un servicio de alojamiento compatible con Python.

⸻

📦 Instalación

Cloná el repositorio:

git clone TU_REPOSITORIO

Entrá en la carpeta:

cd Fire-Nation-Bot

Instalá las dependencias:

pip install -r requirements.txt

Configurá las variables necesarias y ejecutá:

python bot.py

⸻

🔐 Configuración

El bot utiliza una variable de entorno para proteger el token:

DISCORD_TOKEN=TU_TOKEN

El ID del Owner se configura en:

OWNER_ID = TU_ID_DE_DISCORD

⚠️ Nunca publiques tu token del bot en GitHub.

Si tu token se filtra, regeneralo inmediatamente desde el portal de desarrolladores de Discord.

⸻

🔑 Permisos

Para funcionar correctamente, el bot puede necesitar permisos como:

* Manage Messages
* Kick Members
* Ban Members
* Moderate Members
* Manage Channels
* Manage Roles
* View Channels
* Send Messages
* Embed Links
* Read Message History

Los permisos necesarios pueden variar según los módulos habilitados.

⸻

👑 Sistema de Owner

El sistema de Owner permite establecer un propietario principal mediante su ID de Discord.

El Owner puede tener acceso especial a determinadas funciones administrativas del bot.

El sistema utiliza:

OWNER_ID

para identificar al propietario.

⸻

📜 Licencia

Este proyecto está protegido por una Licencia Propietaria.

La copia, redistribución, modificación, publicación o comercialización del código está prohibida sin autorización previa del titular.

Consultá el archivo:

LICENSE

para conocer los términos completos.

⸻

🚀 Estado del proyecto

Estado: 🟢 En desarrollo activo

Fire Nation Bot continúa incorporando nuevas funciones, mejoras de seguridad y herramientas para la administración de servidores.

⸻

💎 Créditos

Desarrollado para ofrecer una experiencia moderna de administración y gestión de servidores de Discord.

Fire Nation Bot
© 2026 — Todos los derechos reservados.