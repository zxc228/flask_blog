from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from flask_blog import db
from flask_blog.models import Post, Comment, Like
from flask_blog.posts.forms import PostForm, CommentForm, LikeForm
from flask_blog.users.utils import save_picture

posts = Blueprint('posts', __name__)

@posts.route('/allpost', methods=['GET', 'POST'])
@login_required
def allpost():
    page = request.args.get('page', 1, type=int)
    posts_pagination = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    # Добавляем счетчики лайков и дизлайков для каждого поста
    posts_with_likes = []
    for post in posts_pagination.items:
        likes_count = Like.query.filter_by(post_id=post.id, value=True).count()
        dislikes_count = Like.query.filter_by(post_id=post.id, value=False).count()
        posts_with_likes.append({
            'post': post,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count
        })

    like_form = LikeForm()

    if like_form.validate_on_submit():
        post_id = request.form.get('post_id')
        post = Post.query.get_or_404(post_id)

        # Обработка лайка
        if 'like' in request.form:
            like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
            if like:
                if like.value == True:
                    db.session.delete(like)
                    db.session.commit()
                    flash('Лайк удален!', 'info')
                else:
                    like.value = True
                    db.session.commit()
                    flash('Лайк обновлен!', 'success')
            else:
                new_like = Like(user_id=current_user.id, post_id=post_id, value=True)
                db.session.add(new_like)
                db.session.commit()
                flash('Лайк поставлен!', 'success')

        # Обработка дизлайка
        if 'dislike' in request.form:
            like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
            if like:
                if like.value == False:
                    db.session.delete(like)
                    db.session.commit()
                    flash('Дизлайк удален!', 'info')
                else:
                    like.value = False
                    db.session.commit()
                    flash('Дизлайк обновлен!', 'success')
            else:
                new_dislike = Like(user_id=current_user.id, post_id=post_id, value=False)
                db.session.add(new_dislike)
                db.session.commit()
                flash('Дизлайк поставлен!', 'success')

        return redirect(url_for('posts.allpost', page=page))

    return render_template('allpost.html', posts_with_likes=posts_with_likes, pagination=posts_pagination, like_form=like_form)




@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    picture_name = None
    if form.validate_on_submit():
        if form.picture.data:
            picture_name = save_picture(form.picture.data)
        post =Post(title=form.title.data, content=form.content.data, author=current_user, image_file=picture_name)
        db.session.add(post)
        db.session.commit()
        flash("Ваш пост создан!", 'success')
        return redirect(url_for('posts.allpost'))
    return render_template('create_post.html', title='New post', form=form, image_file=picture_name, legend='New post')


@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    
    form = CommentForm()
    like_form = LikeForm()

    # Подсчет лайков и дизлайков
    likes_count = Like.query.filter_by(post_id=post_id, value=True).count()
    dislikes_count = Like.query.filter_by(post_id=post_id, value=False).count()

    if form.validate_on_submit() and 'submit' in request.form:
        comment = Comment(body=form.comment.data, post_id=post_id, username=current_user.username)
        db.session.add(comment)
        db.session.commit()
        flash('Ваш комментарий был добавлен!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))

    if like_form.validate_on_submit():
        # Обработка лайка
        if 'like' in request.form:
            like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

            if like:
                if like.value == True:
                    db.session.delete(like)
                    db.session.commit()
                    flash('Лайк удален!', 'info')
                else:
                    like.value = True
                    db.session.commit()
                    flash('Лайк обновлен!', 'success')
            else:
                new_like = Like(user_id=current_user.id, post_id=post_id, value=True)
                db.session.add(new_like)
                db.session.commit()
                flash('Лайк поставлен!', 'success')

        # Обработка дизлайка
        if 'dislike' in request.form:
            like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

            if like:
                if like.value == False:
                    db.session.delete(like)
                    db.session.commit()
                    flash('Дизлайк удален!', 'info')
                else:
                    like.value = False
                    db.session.commit()
                    flash('Дизлайк обновлен!', 'success')
            else:
                new_dislike = Like(user_id=current_user.id, post_id=post_id, value=False)
                db.session.add(new_dislike)
                db.session.commit()
                flash('Дизлайк поставлен!', 'success')

        return redirect(url_for('posts.post', post_id=post_id))

    return render_template('post.html', title=post.title, post=post, form=form, like_form=like_form, likes_count=likes_count, dislikes_count=dislikes_count)



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
            picture_file = save_picture(form.picture.data)
            post.image_file = picture_file
        db.session.commit()
        flash('Ваш пост был обновлен', 'success')
        return redirect(url_for('posts.post', post_id = post.id))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

        image_file = url_for('static', filename='posts_pics/'+post.image_file)

    return render_template('create_post.html', title='Update post', image_file=image_file, form=form, legend='Update post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Ваш пост был удален!', 'success')
    return redirect(url_for('posts.allpost'))


@posts.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.username != current_user.username:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Ваш комметарий был удален!', 'success')
    return redirect(url_for('posts.post', post_id=comment.post_id))
