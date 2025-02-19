import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

# Configuración de paths
LOCAL_MUSIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'music')
SFTP_REMOTE_PATH = '/uploads/data'

def update():
    """Sincroniza archivos MP3 desde SFTP a la carpeta local"""
    try:
        # Conexión SFTP
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=os.getenv('SFTP_HOST'),
            port=int(os.getenv('SFTP_PORT', 22)),
            username=os.getenv('SFTP_USER'),
            password=os.getenv('SFTP_PASSWORD')
        )
        
        sftp = ssh.open_sftp()
        sftp.chdir(SFTP_REMOTE_PATH)
        
        # Obtener lista de archivos
        remote_files = sftp.listdir()
        mp3_files = [f for f in remote_files if f.lower().endswith('.mp3')]
        
        # Descargar nuevos archivos
        downloaded = []
        errors = []
        
        for filename in mp3_files:
            local_path = os.path.join(LOCAL_MUSIC_DIR, filename)
            remote_path = os.path.join(SFTP_REMOTE_PATH, filename)
            
            if not os.path.exists(local_path):
                try:
                    sftp.get(remote_path, local_path)
                    downloaded.append(filename)
                except Exception as e:
                    errors.append(f"{filename}: {str(e)}")
        
        sftp.close()
        ssh.close()
        
        return {
            'success': True,
            'downloaded': downloaded,
            'errors': errors,
            'message': f"Descargados {len(downloaded)} archivos, {len(errors)} errores"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }