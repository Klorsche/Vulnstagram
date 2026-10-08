import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # [VULN-START: Session Hijacking via XSS]
    # Spiegazione: Disabilitiamo il flag HttpOnly sui cookie di sessione.
    # Questo permette a JavaScript (e quindi a un attacco XSS) di accedere al cookie
    # tramite document.cookie e rubare la sessione dell'utente.
    SESSION_COOKIE_HTTPONLY = False
    # [VULN-END]
    
    SESSION_COOKIE_SAMESITE = 'Lax'
    # In produzione (con HTTPS) andrebbe impostato su True
    SESSION_COOKIE_SECURE = False
