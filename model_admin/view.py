from flask import session , render_template , request , abort, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from app import db
from model_blog.forms import CreatePostForm
from model_blog.models import Post
from model_users.forms import LoginForm
from model_users.model import User
from . import admin
from .utils import admin_only_view


@admin.route('/')
@admin_only_view
def index():
    return render_template('admin/index.html')


@admin.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            abort(400)
        user = User.query.filter(User.email.ilike(f'{form.email.data}')).first()
        if not user:
            flash('loggin Error',category='danger')
            return render_template('admin/login.html' , form = form)
        if not user.check_password(form.password.data):
            flash('loggin Error',category='danger')
            return render_template('admin/login.html' , form = form)
        if not user.is_admin():
            flash('you are not admin',category='danger')
            return render_template('admin/login.html' , form = form)
        session['email'] = user.email
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('admin.index'))
    if session.get('role') == 1:
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html' , form = form)


@admin.route('/posts/new/',methods=['GET','POST'])
@admin_only_view
def create_post():
    form = CreatePostForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return '1'
        new_post = Post()
        new_post.title = form.title.data
        new_post.summary = form.summary.data
        new_post.content = form.content.data
        new_post.slug = form.slug.data
        try:
            db.session.add(new_post)
            db.session.commit()
            flash('Your New Post Created Successfully','success')
            return redirect(url_for('admin.index'))
        except IntegrityError:
            db.session.rollback()
            flash('This Post Before Uploaded','danger')
    return render_template('/admin/create_post.html',form = form)        


@admin.route('/logout',methods=['GET'])
def logout():
    session.clear()
    flash('you logged out successfully' , 'success')
    return redirect(url_for('admin.login'))