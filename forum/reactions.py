# Modularized reactions logic from routes.py
from flask import Blueprint, request
from flask_login import current_user, login_required
from forum.models import Post, Reaction, db, error

reactions_bp = Blueprint('reactions', __name__)

@login_required
@reactions_bp.route('/action_react', methods=['POST'])
def action_react():
    post_id = int(request.form.get('post_id'))
    emoji = request.form.get('emoji')
    post = Post.query.filter(Post.id == post_id).first()
    if not post:
        return error("That post does not exist!")
    existing = Reaction.query.filter_by(user_id=current_user.id, post_id=post_id, emoji=emoji).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return {'status': 'removed'}
    else:
        reaction = Reaction(emoji=emoji, user_id=current_user.id, post_id=post_id)
        db.session.add(reaction)
        db.session.commit()
        return {'status': 'added'}

