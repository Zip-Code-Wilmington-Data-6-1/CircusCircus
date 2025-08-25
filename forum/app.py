from flask import render_template, Flask
from flask_login import LoginManager
from forum.models import Subforum, db, User
from forum.posts import posts_bp
from forum.routes import rt
from forum.reactions import reactions_bp
from forum.comments import comments_bp
from forum.auth import auth_bp
from forum.messages import messages_bp
from forum.filters import embed_media

from forum.settings import settings_bp
from datetime import datetime


from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
db.init_app(app)

app.register_blueprint(posts_bp)
app.register_blueprint(rt)
app.register_blueprint(reactions_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(messages_bp)
app.jinja_env.filters['embed_media'] = embed_media
app.register_blueprint(settings_bp)

app.config['SITE_NAME'] = 'Schooner'
app.config['SITE_DESCRIPTION'] = 'a schooner forum'
app.config['FLASK_DEBUG'] = 1

def init_site():
    print("creating initial subforums")
    admin = add_subforum("Forum", "Announcements, bug reports, and general discussion about the forum belongs here")
    add_subforum("Announcements", "View forum announcements here", admin)
    add_subforum("Bug Reports", "Report bugs with the forum here", admin)
    add_subforum("General Discussion", "Use this subforum to post anything you want")
    add_subforum("Other", "Discuss other things here")

def add_subforum(title, description, parent=None):
    sub = Subforum(title, description)
    if parent:
        for subforum in parent.subforums:
            if subforum.title == title:
                return
        parent.subforums.append(sub)
    else:
        subforums = Subforum.query.filter(Subforum.parent_id == None).all()
        for subforum in subforums:
            if subforum.title == title:
                return
        db.session.add(sub)
    print("adding " + title)
    db.session.commit()
    return sub

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

with app.app_context():
    db.create_all()
    if not Subforum.query.all():
        init_site()

@app.route('/')
def index():
    subforums = Subforum.query.filter(Subforum.parent_id == None).order_by(Subforum.id)
    return render_template("subforums.html", subforums=subforums)

@app.context_processor
def inject_now():
    return {'current_year': datetime.now().year}





