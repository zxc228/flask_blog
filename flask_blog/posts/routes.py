from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app
from flask_login import current_user, login_required
from flask_blog import db
from flask_blog.models import Post, Comment, Like
from flask_blog.posts.forms import PostForm, CommentForm, LikeForm
from flask_blog.users.utils import save_post_picture
import os

posts = Blueprint('posts', __name__)

@posts.route('/allpost', methods=['GET', 'POST'])
@login_required
def allpost():
    page = request.args.get('page', 1, type=int)
    posts_pagination = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    # Adding like and dislike counters for each post
    posts_with_likes = []
    for post in posts_pagination.items:
        likes_count = Like.query.filter_by(post_id=post.id, value=True).count()
        dislikes_count = Like.query.filter_by(post_id=post.id, value=False).count()
        
        posts_with_likes.append({
            'post': post,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
            'date_posted_utc': post.date_posted.isoformat() + "Z"
        })

    like_form = LikeForm()

    if like_form.validate_on_submit():
        post_id = request.form.get('post_id')
        post = Post.query.get_or_404(post_id)

        # Handling like
        if 'like' in request.form:
            like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
            if like:
                if like.value == True:
                    db.session.delete(like)
                    db.session.commit()
                    flash('Like removed!', 'info')
                else:
                    like.value = True
                    db.session.commit()
                    flash('Like updated!', 'success')
            else:
                new_like = Like(user_id=current_user.id, post_id=post_id, value=True)
                db.session.add(new_like)
                db.session.commit()
                flash('Like added!', 'success')

        # Handling dislike
        if 'dislike' in request.form:
            like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
            if like:
                if like.value == False:
                    db.session.delete(like)
                    db.session.commit()
                    flash('Dislike removed!', 'info')
                else:
                    like.value = False
                    db.session.commit()
                    flash('Dislike updated!', 'success')
            else:
                new_dislike = Like(user_id=current_user.id, post_id=post_id, value=False)
                db.session.add(new_dislike)
                db.session.commit()
                flash('Dislike added!', 'success')

        return redirect(url_for('posts.allpost', page=page))

    return render_template('allpost.html', posts_with_likes=posts_with_likes, pagination=posts_pagination, like_form=like_form)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        image_file = None
        if form.picture.data:
            image_file = save_post_picture(form.picture.data, 0)  # 0 is temporarily used until the real post ID is obtained
        post = Post(title=form.title.data, content=form.content.data, author=current_user, image_file=image_file or 'default.png')
        db.session.add(post)
        db.session.flush()  # Flush to get the post ID

        if image_file:
            # Update the filename with the real post ID after flush
            image_file = save_post_picture(form.picture.data, post.id)
            post.image_file = image_file
        
        db.session.commit()
        flash("Your post has been created!", 'success')
        return redirect(url_for('posts.allpost'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    
    form = CommentForm()
    like_form = LikeForm()

    # Counting likes and dislikes
    likes_count = Like.query.filter_by(post_id=post_id, value=True).count()
    dislikes_count = Like.query.filter_by(post_id=post_id, value=False).count()

    if form.validate_on_submit() and 'submit' in request.form:
        comment = Comment(body=form.comment.data, post_id=post_id, username=current_user.username)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))

    if like_form.validate_on_submit():
        # Handling like
        if 'like' in request.form:
            like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

            if like:
                if like.value == True:
                    db.session.delete(like)
                    db.session.commit()
                    flash('Like removed!', 'info')
                else:
                    like.value = True
                    db.session.commit()
                    flash('Like updated!', 'success')
            else:
                new_like = Like(user_id=current_user.id, post_id=post_id, value=True)
                db.session.add(new_like)
                db.session.commit()
                flash('Like added!', 'success')

        # Handling dislike
        if 'dislike' in request.form:
            like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

            if like:
                if like.value == False:
                    db.session.delete(like)
                    db.session.commit()
                    flash('Dislike removed!', 'info')
                else:
                    like.value = False
                    db.session.commit()
                    flash('Dislike updated!', 'success')
            else:
                new_dislike = Like(user_id=current_user.id, post_id=post_id, value=False)
                db.session.add(new_dislike)
                db.session.commit()
                flash('Dislike added!', 'success')

        return redirect(url_for('posts.post', post_id=post_id))

    return render_template('post.html', title=post.title, post=post, form=form, like_form=like_form, likes_count=likes_count, dislikes_count=dislikes_count, date_posted_utc=post.date_posted.isoformat() + "Z")


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.picture.data:
            # Remove old image if it exists
            if post.image_file:
                old_picture_path = os.path.join(current_app.root_path, 'static/post_pics', post.image_file)
                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)
            
            # Save new image
            picture_file = save_post_picture(form.picture.data, post.id)
            post.image_file = picture_file

        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        image_file = url_for('static', filename='post_pics/' + post.image_file) if post.image_file else None

    return render_template('create_post.html', title='Update Post', image_file=image_file, form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('posts.allpost'))


@posts.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.username != current_user.username:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('posts.post', post_id=comment.post_id))
