from flask import request , render_template ,flash
from . import users
from .forms import Registerform
from .model import User
from app import db


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
        db.session.add(new_user)
        db.session.commit()
        flash('Your account created successfully','success')
    return render_template('/users/register.html',form = form)