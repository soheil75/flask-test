from flask import request , render_template ,flash
from sqlalchemy.exc import IntegrityError
from . import users
from .forms import Registerform
from .model import User
from app import db
from .utils import add_to_redis, send_signup_message, get_from_redis, delete_from_redis


@users.route('/register',methods=['GET','POST'])
def register():
    form = Registerform(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('/users/register.html',form = form)
        if not form.password.data == form.confirm_password.data:
            error_msg = 'Password and Confirm Password does not match.'
            form.password.errors.append(error_msg)
            form.confirm_password.errors.append(error_msg)
            return render_template('/users/register.html',form = form)
        new_user = User()
        new_user.full_name = form.fullname.data
        new_user.email = form.email.data
        new_user.set_password(form.password.data)
        try:
            db.session.add(new_user)
            db.session.commit()
            token = add_to_redis(new_user,'register')
            send_signup_message(new_user,token)
            flash('Your account created successfully','success')
        except IntegrityError:
            db.session.rollback()
            flash('This Email Be Used','danger')
    return render_template('/users/register.html',form = form)


@users.route('/confirm/')
def confirm_registeration():
    email = request.args.get('email')
    token = request.args.get('token')
    print(email, token)

    user = User.query.filter(User.email.ilike(email)).first()
    if not user:
        return "User not found!"
    if user.active:
        return "User already activated!"
    
    token_from_redis = get_from_redis(user, 'register')
    print(token_from_redis)
    if not token_from_redis:
        return "Wrong/Expired Token!1"
    if token != token_from_redis.decode('UTF-8'):
        return "Wrong/Expired Token!"

    user.active = True
    db.session.commit()
    delete_from_redis(user, 'register')

    return "1"