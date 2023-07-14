from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class Register(FlaskForm):
    name = StringField(label="your name", validators=[DataRequired()])
    email = StringField(label="your email",validators=[DataRequired()])
    password = PasswordField(label="your password",validators=[DataRequired()])
    submit = SubmitField(label="register")

class Login(FlaskForm):
    email = StringField(label="your email",validators=[DataRequired()])
    password = PasswordField(label="your password",validators=[DataRequired()])
    submit = SubmitField(label="register")

class CommentForm(FlaskForm):
    comment = CKEditorField("comment", validators=[DataRequired()])
    submit = SubmitField(label="send comment")