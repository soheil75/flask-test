from flask import session, render_template, request, abort, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from app import db
from model_blog.forms import PostForm, CategoryForm
from model_blog.models import Post, Category
from model_users.forms import LoginForm, Registerform
from model_users.model import User
from model_uploads.forms import FileUploadForm
from model_uploads.models import File
from werkzeug.utils import secure_filename
import uuid
from . import admin
from .utils import admin_only_view


@admin.route('/')
@admin_only_view
def index():
    return render_template('admin/index.html')


@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            abort(400)
        user = User.query.filter(
            User.email.ilike(f'{form.email.data}')).first()
        if not user:
            flash('loggin Error', category='danger')
            return render_template('admin/login.html', form=form)
        if not user.check_password(form.password.data):
            flash('loggin Error', category='danger')
            return render_template('admin/login.html', form=form)
        if not user.is_admin():
            flash('you are not admin', category='danger')
            return render_template('admin/login.html', form=form)
        session['email'] = user.email
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(url_for('admin.index'))
    if session.get('role') == 1:
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html', form=form)


@admin.route('/users', methods=['GET'])
@admin_only_view
def list_user():
    users = User.query.all()
    return render_template('/admin/list_user.html', users=users)


@admin.route('/users/new', methods=['GET'])
@admin_only_view
def get_create_user():
    form = Registerform()
    return render_template('/admin/create_user.html', form=form)


@admin.route('/users/new', methods=['POST'])
@admin_only_view
def post_create_user():
    form = Registerform(request.form)
    if not form.validate_on_submit():
        return render_template('/admin/create_user.html', form=form)
    if not form.password.data == form.confirm_password.data:
        error_msg = 'Password and Confirm Password does not match.'
        form.password.errors.append(error_msg)
        form.confirm_password.errors.append(error_msg)
        return render_template('/admin/create_user.html', form=form)
    new_user = User()
    new_user.full_name = form.fullname.data
    new_user.email = form.email.data
    new_user.set_password(form.password.data)
    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Your account created successfully', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('This Email Be Used', 'danger')
    return render_template('/admin/create_user.html', form=form)

###################################################################


@admin.route('/posts/new/', methods=['GET', 'POST'])
@admin_only_view
def create_post():
    form = PostForm(request.form)
    categories = Category.query.order_by(Category.id.asc()).all()
    form.categories.choices = [(category.id, category.name)
                               for category in categories]
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('ّForm Validation Error!', 'danger')
            return redirect(url_for('admin.index'))
        new_post = Post()
        new_post.title = form.title.data
        new_post.summary = form.summary.data
        new_post.content = form.content.data
        new_post.slug = form.slug.data
        # new_post.categoriesدر اینجا چون
        # توقع دارد که یک لیست دریافت کند نمیتوان مثل پارامتر های دیگر مقدار دهی کرد چون طرف دیگر تساوی فقط عدد است
        # پس به این صورت یک لیست درست کرده و اعداد گرفته شده را در قالب حلقه یک لیست میکنیم
        # با عدد گرفته شده درون دیتابیس گشتیم وکتگوری مورد نظر را یافت کردیم
        new_post.categories = [Category.query.get(
            category_id) for category_id in form.categories.data]
        try:
            db.session.add(new_post)
            db.session.commit()
            flash('Your New Post Created Successfully', 'success')
            return redirect(url_for('admin.index'))
        except IntegrityError:
            db.session.rollback()
            flash('This Post Before Uploaded', 'danger')
    return render_template('/admin/create_post.html', form=form)


@admin.route('/posts/', methods=['GET'])
@admin_only_view
def list_post():
    posts = Post.query.all()
    return render_template('/admin/list_post.html', posts=posts)


@admin.route('/posts/delete/<int:post_id>/')
@admin_only_view
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post Deleted Successfully', 'success')
    return redirect(url_for('admin.list_post'))


@admin.route('/posts/modify/<int:post_id>', methods=['GET', 'POST'])
@admin_only_view
def modify_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    categories = Category.query.order_by(Category.id.asc()).all()
    form.categories.choices = [(category.id, category.name)
                               for category in categories]
    if request.method != 'POST':
        form.categories.data = [category.id for category in post.categories]
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('/admin/modify_post.html', post=post, form=form)
        post.title = form.title.data
        post.summary = form.summary.data
        post.content = form.content.data
        post.slug = form.slug.data
        post.categories = [Category.query.get(
            category_id) for category_id in form.categories.data]
        try:
            db.session.commit()
            flash('Post Updated Successfully', 'success')
            return redirect(url_for('admin.list_post'))
        except IntegrityError:
            db.session.rollback()
            flash('Something Is Wrong', 'danger')
    return render_template('/admin/modify_post.html', post=post, form=form)


@admin.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('you logged out successfully', 'success')
    return redirect(url_for('admin.login'))


##########################################################
@admin.route('/categories/new/', methods=['GET', 'POST'])
@admin_only_view
def create_category():
    form = CategoryForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return '1'
        new_category = Category()
        new_category.name = form.name.data
        new_category.description = form.description.data
        new_category.slug = form.slug.data
        try:
            db.session.add(new_category)
            db.session.commit()
            flash('Your New Category Created Successfully', 'success')
            return redirect(url_for('admin.index'))
        except IntegrityError:
            db.session.rollback()
            flash('This Category Before Uploaded', 'danger')
    return render_template('/admin/create_category.html', form=form)


@admin.route('/categories/', methods=['GET'])
@admin_only_view
def list_categories():
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('/admin/list_categories.html', categories=categories)


@admin.route('/categories/delete/<int:category_id>/')
@admin_only_view
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category Deleted Successfully', 'success')
    return redirect(url_for('admin.list_categories'))


@admin.route('/categories/modify/<int:category_id>', methods=['GET', 'POST'])
@admin_only_view
def modify_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('/admin/modify_category.html', form=form, category=category)
        category.name = form.name.data
        category.description = form.description.data
        category.slug = form.slug.data
        try:
            db.session.commit()
            flash('Category Updated Successfully', 'success')
            return redirect(url_for('admin.list_categories'))
        except IntegrityError:
            db.session.rollback()
            flash('Something Is Wrong', 'danger')
    return render_template('/admin/modify_category.html', form=form, category=category)


##########################################################################################

@admin.route('/library/uploads',methods=['GET','POST'])
@admin_only_view
def upload_file():
    form = FileUploadForm()
    if request.method == 'POST':
        if not form.validate_on_submit:
            return '1'
        filename = f'{uuid.uuid1()}_{secure_filename(form.file.data.filename)}'  
        new_file = File()
        new_file.filename = filename
        try : 
            db.session.add(new_file)
            db.session.commit()
            form.file.data.save(f'static/uploads/{filename}')
            flash(f'File Uploaded on :{url_for("static",filename="uploads/"+filename,_external=True)}', 'success')
        except IndentationError:
            db.session.rollback()
            flash('File Uploaded Failed', 'danger')
    return render_template('/admin/upload_file.html', form=form)