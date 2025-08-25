import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
import markdown
from forum.models import Post, Subforum, error, valid_title, valid_content, db, generateLinkPath, Comment

posts_bp = Blueprint('posts', __name__, template_folder='templates')


@login_required
@posts_bp.route('/addpost')
def addpost():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return error("That subforum does not exist!")

    return render_template("createpost.html", subforum=subforum)

@posts_bp.route('/viewpost')
def viewpost():
    postid = int(request.args.get("post"))
    post = Post.query.filter(Post.id == postid).first()
    if not post:
        return error("That post does not exist!")
    if not post.subforum.path:
        subforumpath = generateLinkPath(post.subforum.id)
    comments = Comment.query.filter(Comment.post_id == postid).order_by(Comment.id.desc())

    # Render Markdown if needed
    if getattr(post, "is_markdown", False):
        rendered_content = markdown.markdown(post.content)
    else:
        rendered_content = post.content

    return render_template(
        "viewpost.html",
        post=post,
        path=subforumpath,
        comments=comments,
        rendered_content=rendered_content
    )

@login_required
@posts_bp.route('/action_post', methods=['POST'])
def action_post():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return redirect(url_for("subforums"))

    user = current_user
    title = request.form['title']
    content = request.form['content']
    is_markdown = 'is_markdown' in request.form  # Get checkbox value

    #check for valid posting
    errors = []
    retry = False
    if not valid_title(title):
        errors.append("Title must be between 4 and 140 characters long!")
        retry = True
    if not valid_content(content):
        errors.append("Post must be between 10 and 5000 characters long!")
        retry = True
    if retry:
        return render_template("createpost.html",subforum=subforum,  errors=errors)
    post = Post(title, content, datetime.datetime.now(), is_markdown=is_markdown)
    subforum.posts.append(post)
    user.posts.append(post)
    db.session.commit()
    return redirect("/viewpost?post=" + str(post.id))

@login_required
@posts_bp.route('/delete_post', methods=['POST'])
def delete_post():
    post_id = int(request.form.get('post_id'))
    post = Post.query.get(post_id)
    if not post:
        return redirect('/')
    # Only allow author or admin to delete
    if not current_user.is_authenticated or (current_user.id != post.user.id and not current_user.admin):
        return "Unauthorized", 403
    db.session.delete(post)
    db.session.commit()
    return redirect('/')
