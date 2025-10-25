import firebase_admin
from firebase_admin import credentials, db
import os
import json

# Initialize Firebase (solo una volta)
_firebase_initialized = False

def init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    
    try:
        # Usa le credenziali dal file JSON (se locale) o dalla variabile d'ambiente
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        
        if cred_path and os.path.exists(cred_path):
            # Locale: usa il file JSON
            cred = credentials.Certificate(cred_path)
        else:
            # Render: usa la variabile d'ambiente
            firebase_creds = os.getenv('FIREBASE_CREDENTIALS')
            if firebase_creds:
                cred_dict = json.loads(firebase_creds)
                cred = credentials.Certificate(cred_dict)
            else:
                raise ValueError("Firebase credentials not found!")
        
        # Database URL
        database_url = os.getenv('FIREBASE_DATABASE_URL')
        if not database_url:
            raise ValueError("FIREBASE_DATABASE_URL not set!")
        
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        
        _firebase_initialized = True
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        raise

def get_all_configs():
    """Recupera tutte le configurazioni dei server"""
    try:
        ref = db.reference('guilds')
        configs = ref.get()
        return configs if configs else {}
    except Exception as e:
        print(f"Error getting configs: {e}")
        return {}

def get_guild_config(guild_id):
    """Recupera la configurazione di un singolo server"""
    try:
        ref = db.reference(f'guilds/{guild_id}')
        config = ref.get()
        return config if config else {}
    except Exception as e:
        print(f"Error getting guild config: {e}")
        return {}

def save_guild_config(guild_id, config):
    """Salva la configurazione di un server"""
    try:
        ref = db.reference(f'guilds/{guild_id}')
        ref.set(config)
        print(f"✅ Config saved for guild {guild_id}")
        return True
    except Exception as e:
        print(f"Error saving guild config: {e}")
        return False

def update_guild_config(guild_id, updates):
    """Aggiorna parzialmente la configurazione di un server"""
    try:
        ref = db.reference(f'guilds/{guild_id}')
        ref.update(updates)
        print(f"✅ Config updated for guild {guild_id}")
        return True
    except Exception as e:
        print(f"Error updating guild config: {e}")
        return False

def delete_guild_field(guild_id, field):
    """Elimina un campo specifico dalla configurazione di un server"""
    try:
        ref = db.reference(f'guilds/{guild_id}/{field}')
        ref.delete()
        print(f"✅ Field {field} deleted for guild {guild_id}")
        return True
    except Exception as e:
        print(f"Error deleting field: {e}")
        return False
