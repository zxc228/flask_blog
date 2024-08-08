from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_blog import db, bcrypt
from flask_blog.models import User, Post, Like
from flask_blog.users.forms import RegistrationForm, LoginForm, \
    UpdateAccountForm, \
    RequestResetForm, ResetPasswordForm , ResendConfirmationForm
from flask_blog.users.utils import save_profile_picture, send_reset_email, send_confirmation_email
from flask_blog.posts.forms import LikeForm

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # Отправка письма с подтверждением почты
        send_confirmation_email(user)
        
        flash('Ваша учетная запись была создана! Пожалуйста, подтвердите вашу электронную почту.', 'info')
        return redirect(url_for('main.home'))
    return render_template('register.html', title='Register', form=form)



@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.email_confirmed:
                flash('Ваша электронная почта не подтверждена. Пожалуйста, подтвердите её перед входом.', 'warning')
                return redirect(url_for('users.login'))
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Вход не выполнен. Проверьте email и пароль.', 'danger')
    return render_template('login.html', title='Login', form=form)



@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data, current_user.username)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Ваш аккаунт был обновлен!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        page = request.args.get('page', 1, type=int)
        user = User.query.filter_by(username=form.username.data).first_or_404()
        posts = Post.query.filter_by(author=user) \
            .order_by(Post.date_posted.desc()) \
            .paginate(page=page, per_page=5)
    image_file = url_for('static', filename='profile_pics/' +
                                            current_user.image_file)
    return render_template('account.html', title='Аккаунт',
                           image_file=image_file, form=form, posts=posts,
                           user=user)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route('/user/<string:username>', methods=['GET', 'POST'])
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    # Создаем форму для лайков
    like_form = LikeForm()

    if like_form.validate_on_submit():
        post_id = request.form.get('post_id')
        post = Post.query.get_or_404(post_id)

        # Проверяем, существует ли уже лайк или дизлайк от текущего пользователя
        existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

        if 'like' in request.form:
            if existing_like:
                if existing_like.value:
                    # Удалить лайк
                    db.session.delete(existing_like)
                else:
                    # Изменить дизлайк на лайк
                    existing_like.value = True
            else:
                # Добавить новый лайк
                new_like = Like(user_id=current_user.id, post_id=post_id, value=True)
                db.session.add(new_like)
        elif 'dislike' in request.form:
            if existing_like:
                if not existing_like.value:
                    # Удалить дизлайк
                    db.session.delete(existing_like)
                else:
                    # Изменить лайк на дизлайк
                    existing_like.value = False
            else:
                # Добавить новый дизлайк
                new_dislike = Like(user_id=current_user.id, post_id=post_id, value=False)
                db.session.add(new_dislike)

        db.session.commit()
        return redirect(url_for('users.user_posts', username=username, page=page))

    # Подготавливаем посты с лайками и дизлайками
    posts_with_likes = []
    for post in posts.items:
        likes_count = Like.query.filter_by(post_id=post.id, value=True).count()
        dislikes_count = Like.query.filter_by(post_id=post.id, value=False).count()
        posts_with_likes.append({
            'post': post,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count,
             'date_posted_utc': post.date_posted.isoformat() + "Z"
        })

    return render_template('user_posts.html', posts=posts_with_likes, user=user, pagination=posts, like_form=like_form)



@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('posts.allpost'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("На вашу почту было отправлено письмо с инструкциями по сброс паролей", 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Сброс пароля', form=form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('posts.allpost'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Это недействительный или просроченный токен', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Ваш пароль был обновлен!. Теперь вы можете авторизоваться.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form)



@users.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    user = User.verify_email_confirmation_token(token)
    if user is None:
        flash('Это недействительный или просроченный токен', 'warning')
        return redirect(url_for('users.register'))

    if user.email_confirmed:
        flash('Эта почта уже подтверждена.', 'success')
    else:
        user.email_confirmed = True
        db.session.commit()
        flash('Ваша почта была успешно подтверждена!', 'success')

    return redirect(url_for('users.login'))





@users.route("/resend_confirmation", methods=['GET', 'POST'])
def resend_confirmation():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = ResendConfirmationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and not user.email_confirmed:
            send_confirmation_email(user)
            flash('Новый токен подтверждения был отправлен на вашу почту.', 'info')
        else:
            flash('Пользователь с таким email не найден или уже подтвержден.', 'danger')
        return redirect(url_for('users.login'))
    return render_template('resend_confirmation.html', title='Повторная отправка подтверждения', form=form)
