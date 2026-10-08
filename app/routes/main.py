from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.models import User, Post, Comment, DirectMessage
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    # Nel feed principale (Home), mostriamo solo i post degli utenti pubblici (is_private=False)
    # oppure i post dell'utente stesso.
    # Se volessimo implementare un vero "Follow", aggiungeremmo i post dei followed.
    posts = Post.query.join(User).filter(
        (User.is_private == False) | (Post.user_id == current_user.id)
    ).order_by(Post.created_at.desc()).all()
    
    return render_template('main/index.html', posts=posts)

@main_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    users = []
    if query:
        # Ricerca case-insensitive per username
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    return render_template('main/search.html', users=users, query=query)

@main_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image part', 'danger')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            
            upload_folder = os.path.join(os.getcwd(), current_app.config['UPLOAD_FOLDER'])
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            caption = request.form.get('caption', '')
            post = Post(image_filename=filename, caption=caption, author=current_user)
            db.session.add(post)
            db.session.commit()
            
            flash('Post created successfully!', 'success')
            return redirect(url_for('main.index'))
            
    return render_template('main/new_post.html')

@main_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, author=current_user, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.', 'success')
    else:
        flash('Comment cannot be empty.', 'danger')
    return redirect(url_for('main.index'))

@main_bp.route('/messages')
@login_required
def messages():
    # Carica la cronologia dei messaggi reali dell'utente per la sidebar
    user_msgs = DirectMessage.query.filter(
        (DirectMessage.sender_id == current_user.id) | (DirectMessage.receiver_id == current_user.id)
    ).order_by(DirectMessage.created_at.desc()).all()
    return render_template('main/messages.html', messages=user_msgs, active_message=None)


# --- INIZIO MODULO VULNERABILITA': IDOR / BROKEN ACCESS CONTROL ---

# [VULN-START: Insecure Direct Object Reference (IDOR)]
# Spiegazione: L'app prende l'ID del messaggio dall'URL e renderizza la pagina HTML.
# Non viene effettuato il controllo che l'utente loggato sia mittente o destinatario.
@main_bp.route('/messages/<int:message_id>')
@login_required
def message_detail(message_id):
    # Sidebar: carichiamo i messaggi legittimi dell'utente
    user_msgs = DirectMessage.query.filter(
        (DirectMessage.sender_id == current_user.id) | (DirectMessage.receiver_id == current_user.id)
    ).order_by(DirectMessage.created_at.desc()).all()
    
    # Main Chat: recuperiamo il messaggio richiesto dall'URL (VULNERABILE)
    msg = DirectMessage.query.get_or_404(message_id)
    
    # VERSIONE SICURA (Commentata per il lab)
    # Se il codice fosse sicuro, qui ci sarebbe il seguente controllo:
    # if msg.sender_id != current_user.id and msg.receiver_id != current_user.id:
    #     abort(403) # L'utente sta cercando di leggere un messaggio non suo
        
    return render_template('main/messages.html', messages=user_msgs, active_message=msg)
# [VULN-END]

# --- INIZIO MODULO VULNERABILITA': CLIENT-SIDE ACCESS CONTROL (PRIVATE PROFILES) ---

# [VULN-START: Client-Side Authorization]
# Spiegazione: Quando un utente richiede il profilo di un altro utente "privato" (is_private=True),
# il backend restituisce COMUNQUE tutti i post di quell'utente al frontend.
# E' il frontend (Jinja2/JS) che si occupera' di nasconderli visivamente se l'utente non è autorizzato.
# Questo viola la regola "Secure by Default" perche' i dati sensibili non dovrebbero mai 
# lasciare il server se l'utente non ha i permessi per vederli.
@main_bp.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # Recuperiamo tutti i post dell'utente, INDIPENDENTEMENTE dal fatto che il profilo sia privato o meno.
    # Un'implementazione sicura filtrerebbe i post lato server:
    # if user.is_private and user.id != current_user.id:
    #     posts = []
    # else:
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    
    return render_template('main/profile.html', user=user, posts=posts)
# [VULN-END]
