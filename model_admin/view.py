from flask import session , render_template , request ,abort,flash
from model_users.forms import LoginForm
from model_users.model import User
from . import admin
from .utils import admin_only_view


@admin.route('/')
@admin_only_view
def index():
    return 'hello admin'

@admin.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            abort(400)
        user = User.query.filter(User.email.ilike(f'{form.email.data}')).first()
        if not user:
            flash('loggin Error',category='error')
            return render_template('admin/login.html' , form = form)
        if not user.check_password(form.password.data):
            flash('loggin Error',category='error')
            return render_template('admin/login.html' , form = form)
        if not user.is_admin():
            flash('you are not admin',category='error')
            return render_template('admin/login.html' , form = form)
        session['email'] = user.email
        session['id'] = user.id
        session['role'] = user.role
        return 'login successfully'
    if session.get('role') == 1:
        return "You are already login"
    return render_template('admin/login.html' , form = form)