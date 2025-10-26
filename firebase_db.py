import firebase_admin
from firebase_admin import credentials, db
import os
import json

# Initialize Firebase (only once)
_firebase_initialized = False

def init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    
    try:
        # Use credentials from JSON file (if local) or environment variable
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        
        if cred_path and os.path.exists(cred_path):
            # Local: use JSON file
            cred = credentials.Certificate(cred_path)
        else:
            # Render: use environment variable
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
    """Retrieves all server configurations"""
    try:
        ref = db.reference('guilds')
        configs = ref.get()
        return configs if configs else {}
    except Exception as e:
        print(f"Error getting configs: {e}")
        return {}

def get_guild_config(guild_id):
    """Retrieves a single server's configuration"""
    try:
        ref = db.reference(f'guilds/{guild_id}')
        config = ref.get()
        return config if config else {}
    except Exception as e:
        print(f"Error getting guild config: {e}")
        return {}

def save_guild_config(guild_id, config):
    """Saves a server's configuration"""
    try:
        ref = db.reference(f'guilds/{guild_id}')
        ref.set(config)
        print(f"✅ Config saved for guild {guild_id}")
        return True
    except Exception as e:
        print(f"Error saving guild config: {e}")
        return False

def update_guild_config(guild_id, updates):
    """Partially updates a server's configuration"""
    try:
        ref = db.reference(f'guilds/{guild_id}')
        ref.update(updates)
        print(f"✅ Config updated for guild {guild_id}")
        return True
    except Exception as e:
        print(f"Error updating guild config: {e}")
        return False

def delete_guild_field(guild_id, field):
    """Deletes a specific field from a server's configuration"""
    try:
        ref = db.reference(f'guilds/{guild_id}/{field}')
        ref.delete()
        print(f"✅ Field {field} deleted for guild {guild_id}")
        return True
    except Exception as e:
        print(f"Error deleting field: {e}")
        return False
