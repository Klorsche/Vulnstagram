from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

# Inizializzazione estensioni (pattern Factory)
db = SQLAlchemy()
csrf = CSRFProtect() # [SECURE BY DEFAULT] Protezione globale CSRF attiva
login_manager = LoginManager()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
