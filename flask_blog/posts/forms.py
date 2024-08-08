from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
    picture = FileField('Attach a photo to the post', validators=[FileAllowed(['jpg', 'png'])])


class CommentForm(FlaskForm):
    comment = StringField('Comment', validators=[DataRequired()])


class LikeForm(FlaskForm):
    submit = SubmitField('Like')
    dislike = SubmitField('Dislike')
