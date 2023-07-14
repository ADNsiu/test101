from flask import Flask, render_template, redirect, url_for, flash,request,abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, Register, Login,CommentForm
from flask_gravatar import Gravatar
from functools import wraps
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
gravatar = Gravatar(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(Users).filter_by(id=int(user_id))).scalars().first()
##CONFIGURE TABLES
class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=True, nullable=False)
    posts = relationship("BlogPost",back_populates="author")
    comments= relationship("Comments", back_populates="commenter")
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    author = relationship("Users",back_populates="posts")
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(4356), nullable=False)
    comments = relationship("Comments", back_populates="post")

class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text,nullable=False)
    commenter_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    commenter = relationship("Users", back_populates="comments")
    blog_id = db.Column(db.ForeignKey("blog_posts.id"))
    post = relationship("BlogPost",back_populates="comments")




with app.app_context():
    db.create_all()

def admin_only(f):
    @wraps(f)
    def decor(*args,**kwargs):
        if current_user.id != 1:
            return abort(403)
        else:
            return f(*args,**kwargs)
    return decor
@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, login= current_user.is_authenticated, user=current_user)


@app.route('/register',methods= ["GET","POST"])
def register():
    form = Register()
    if request.method == "GET":

        return render_template("register.html",form=form,login=current_user.is_authenticated)
    elif request.method == "POST" and form.validate_on_submit():
        if db.session.execute(db.select(Users).filter_by(email=request.form.get("email"))).scalars().first():
            flash("this user already exist")
            return redirect(url_for("login"))
        else:
            user = Users(
                name=request.form.get("name"),
                email=request.form.get("email"),
                password=generate_password_hash(password=request.form.get("password"), method="pbkdf2:sha256",salt_length=1)

            )

            db.session.add(user)
            db.session.commit()
            login_user(user)

            return redirect(url_for("get_all_posts"))




@app.route('/login',methods= ["GET","POST"])
def login():
    form = Login()
    email = request.form.get("email")
    user = db.session.execute(db.select(Users).filter_by(email=email)).scalars().first()
    if request.method == "POST":
        if form.validate_on_submit():
            if user and check_password_hash(pwhash=user.password, password=request.form.get("password")):

                login_user(user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("email or pasword are wrong")



    return render_template("login.html", form=form, login= current_user.is_authenticated)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))



@app.route("/post/<int:post_id>", methods=["POST","GET"])

def show_post(post_id):
    comment = CommentForm()

    requested_post = BlogPost.query.get(post_id)
    if request.method == "GET":
        return render_template("post.html", post=requested_post,login=current_user.is_authenticated,user=current_user,comment=comment)
    else:
        if not current_user.is_authenticated:
            flash("you must login to comment")
            return redirect(url_for("login"))
        else:
            if comment.validate_on_submit():
                comment = Comments(
                    text= request.form.get("comment"),
                    commenter= current_user,
                    commenter_id= current_user.id,
                    post= requested_post,
                    blog_id= post_id

                )
                db.session.add(comment)
                db.session.commit()
                return redirect(request.url)


@app.route("/about")
def about():
    return render_template("about.html",login=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html",login=current_user.is_authenticated)


@app.route("/new-post",methods= ["GET","POST"])
@login_required

def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author= current_user,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form,logi=current_user.is_authenticated)


@app.route("/edit-post/<int:post_id>")
@login_required
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form,login=current_user.is_authenticated)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
