from flask import Blueprint, current_app, flash, redirect, render_template, abort, request, url_for
from app import mail, db, lm
from flask.ext.login import login_required, current_user, login_user, logout_user
from flask.ext.mail import Message
from uuid import uuid4
from .models import User, Comment
from .forms import *
from ..utils import send_async_email

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated():
        return redirect(url_for('frontend.index'))

    form = SignupForm()

    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.activation_key = str(uuid4())
        msg = Message("Signup", [user.email], url_for('user.activate', key=user.activation_key, _external=True))
        send_async_email(msg)
        db.session.add(user)
        db.session.commit()
        flash('Check your inbox for actvation!', 'success')
        return redirect(url_for('frontend.index'))

    return render_template('user/signup.html', form=form)

@user.route('/activate')
def activate():
    key = request.args.get('key')
    if not key:
        abort(404)
    user = User.query.filter_by(activation_key=key).first()
    if not user:
        abort(404)

    user._is_active = True
    user.activation_key = None
    db.session.add(user)
    db.session.commit()
    flash('Account activated. Wait to the club', 'success')
    return redirect(url_for('frontend.index'))

@user.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated():
        return redirect(url_for('frontend.index'))
    form = SigninForm()

    if form.validate_on_submit():
        user, authenticated = User.authenticate(form.email.data,
                                                form.password.data)

        if user and authenticated:
            remember = form.remember.data == 'y'
            if login_user(user, remember=remember):
                flash('Signed in successfully', 'success')
                return redirect(url_for('frontend.index'))

            flash('Something went wrong!', 'alert')
            return redirect(url_for('user.signin'))

        if not authenticated:
            flash('Not activated! Activate in your inbox', 'warning')

    return render_template('user/signin.html', form=form)

@user.route('/signout', methods=['GET'])
@login_required
def signout():
    logout_user()
    flash('Signed out', 'success')
    return redirect(url_for('frontend.index'))

@user.route('/recover', methods=['GET', 'POST'])
def recover():
    key = request.args.get('key')
    if key:
        form = SetPasswordForm()
        if form.validate_on_submit():
            user = user.query.filter_by(activation_key=key).first()
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('Password set. Please sign in', 'success')
            return redirect(url_for('user.signin'))
        return render_template('user/recover2.html', form=form)

    form = RecoverPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user.is_active():
            flash('Activate account first', 'success')
            return redirect(url_for('user.recover'))
        user.activation_key = str(uuid4())
        msg = Message("Recover", [form.email.data], url_for('user.recover', key=user.activation_key))
        send_async_email(msg)
        db.session.add(user)
        db.session.commit()
        flash('Email sent. Check your inbox', 'success')
        return redirect(url_for('frontend.index'))

    return render_template('user/recover.html', form=form)

@user.route('/change', methods=['GET', 'POST'])
@login_required
def change():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user)
        db.session.commit()
        flash('Password changed successfully', 'success')
        return redirect( url_for('user.change') )

    return render_template('user/change.html', form=form)

@user.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash('Updated profile', 'success')
        return redirect(url_for('user.profile', id=current_user.id))
    return render_template('user/edit_profile.html', form=form)

@user.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    user = User.by_id(id)
    form = CommentForm()
    if not user:
        abort(404)

    if form.validate_on_submit() and current_user.is_authenticated():
        comment = Comment()
        form.populate_obj(comment)
        comment.commenter_id = current_user.id
        comment.user_id = user.id
        db.session.add(comment)
        db.session.commit()
        flash(u'Thanks for taking a moment to comment!', 'success')
        return redirect( url_for('user.profile', id=id))

    return render_template('user/profile.html', user=user, form=form)

@lm.user_loader
def load_user(id):
    return User.by_id(int(id))


