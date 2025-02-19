## Windows

### 1. Instalar Python y Git
Instalar los paquetes necesarios: Ejecuta:
pip install discord.py python-dotenv eyed3 PyNaCl

Estos paquetes son:

discord.py: Para interactuar con la API de Discord.
python-dotenv: Para cargar variables de entorno desde un archivo .env.
eyed3: Para leer y editar etiquetas ID3 de archivos MP3.
PyNaCl: Requerido para la funcionalidad de voz en Discord.

### 2. Descargar FFmpeg
Extrae el contenido del archivo descargado y copia la carpeta extraída (o al menos la carpeta bin) a C:/ffmpeg/. 
Asegúrate de que el ejecutable ffmpeg.exe esté en C:/ffmpeg/bin.
Agregar FFmpeg al PATH:
Abre el Panel de Control > Sistema y Seguridad > Sistema > Configuración avanzada del sistema > Variables de entorno.
En "Variables del sistema", busca la variable Path y edítala.
Agrega una nueva entrada con C:\ffmpeg\bin.
Guarda y cierra las ventanas.
Puedes verificar la instalación abriendo una terminal (CMD o PowerShell) y ejecutando: ffmpeg -version
Deberías ver información de FFmpeg.

### 3. Preparar el proyecto del bot
Clona o copia el código fuente
Asegúrate de que la estructura sea similar a:

root/
  ├── src/rocolaser_bot.py
  └── music/    <-- Aquí deben ir tus archivos MP3

Configurar el archivo .env: En el directorio del proyecto, crea un archivo llamado .env con el siguiente contenido:
DISCORD_TOKEN=tu_token_del_bot_aquí
Reemplaza tu_token_del_bot_aquí con el token de tu bot obtenido en el Discord Developer Portal.

4. Ejecutar el bot
Con el entorno virtual activado y estando en el directorio del proyecto, ejecuta:

python src/rocolaser_bot.py
Si todo está configurado correctamente, verás mensajes en la consola indicando que el bot se ha iniciado y se han cargado las canciones.

## Ubuntu

Guía de instalación en Ubuntu

### 1. Instalar Python y dependencias básicas
Abre una terminal y ejecuta:

sudo apt update
sudo apt install python3 python3-pip python3-venv git
### 2. Instalar FFmpeg
sudo apt install ffmpeg
ffmpeg -version

### 3. Preparar el proyecto del bot
Clonar o copiar el código fuente
Asegúrate de tener la siguiente estructura:

root/
  ├── src/rocolaser_bot.py
  └── music/    <-- Aquí van tus archivos MP3

Crear un entorno virtual: Navega al directorio del proyecto y ejecuta:

python3 -m venv venv
source venv/bin/activate
Instalar los paquetes necesarios: 

Ejecuta:

pip install discord.py python-dotenv eyed3 PyNaCl

Esto instalará los mismos paquetes mencionados en la guía de Windows.

Configurar el archivo .env: En el directorio del proyecto, crea un archivo llamado .env y coloca:

DISCORD_TOKEN=tu_token_del_bot_aquí

Reemplaza tu_token_del_bot_aquí con el token de tu bot.

### 4. Ejecutar el bot
Con el entorno virtual activado y en el directorio del proyecto, ejecuta:

python3 src/rocolaser_bot.py
Deberías ver en la terminal que el bot se inicia y que se han cargado las canciones.
