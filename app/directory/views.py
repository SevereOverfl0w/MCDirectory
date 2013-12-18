from flask import Blueprint, url_for, redirect, abort, request, render_template, jsonify
from ..user.models import User, Vote
from .models import Payment
from .forms import SearchForm
import paypalrestsdk
from app import db
from flask.ext.login import current_user

directory = Blueprint('directory', __name__)

paypalrestsdk.configure({
      "mode": "sandbox", # sandbox or live
      "client_id": "fillmein",
      "client_secret": "fillmein" })

from datetime import datetime

@directory.route('/search')
def search():
    prof = request.args.get('id')
    if prof == '0':
        prof = None
    text = request.args.get('q')
    p = int(request.args.get('p', 1))
    form = SearchForm(id=prof, q=text)
    users = None

    if text and prof:
        users = User.query.whoosh_search(text).filter_by(profession_id=prof)
    elif prof:
        users = User.query.filter_by(profession_id=prof)
    elif text:
        users = User.query.whoosh_search(text)
    else:
        users = User.query
    users = users.filter_by(is_listed=True).order_by(User.confidence.desc()).paginate(p, 10)
    #users = users.filter(User.premium_until > datetime.utcnow())

    return render_template('directory/list.html', users=users, form=form)

#@directory.route('/membership')
#def membership():
#
#    if form.validate_on_submit():
#        cost = str(form.months.data*30.00)
#        payment = paypalrestsdk.Payment({
#                                    "intent": "sale",
#                                    "payer": {
#                                        "payment_method": "paypal" },
#                                    "redirect_urls": {
#                                        "return_url": url_for('directory.membership_callback', external=True),
#                                        "cancel_url": url_for('frontend.index', external=True),
#                                    },
#                                    "transactions": [ {
#                                        "amount": {
#                                            "total": cost,
#                                            "currency": "USD" },
#                                        "description": "MCDirectory Premium",
#                                    }]})
#        if payment.create():
#            p = Payment()
#            p.payment_id = payment.id
#            package_id = id
#            user_id = current_user.id
#            db.session.add(p)
#            db.session.commit()
#            for link in payment.links:
#                if link.method == "REDIRECT":
#                    return redirect(link.href)
#
#        flash("Something went wrong with paypal", "alert")
#
#    return render_template('directory/membership.html', package_list = PACKAGES)
#
#@directory.route('/membership/callback')
#def membership_callback():
#    payment_id = request.args.get('PayerID')
#    if payment_id:
#        p = Payment.filter(and_(Payment.payment_id==payment_id, Payment.paid==False))
#        if p:
#            p.user.add_standard_months(p.months)
#            flash("Welcome to the club", 'success')
#            return redirect(url_for('frontend.index'))
#        else:
#            abort(403)
#    abort(404)


@directory.route('/_<action>vote')
def vote(action):
    id = request.args.get('id')
    user = User.by_id(id)

    if not current_user.is_authenticated():
        return jsonify(result='login')
    if user:
        vote = current_user.votes_made.filter_by(user_id=id).first()
        if action == 'up':
            if vote is None:
                user.ups += 1
                vote = Vote(up=True, voter_id=current_user.id, user_id=id)
                db.session.add(vote)
            elif vote.up:
                user.ups -= 1
                db.session.delete(vote)
                vote = None
            elif vote.down:
                user.ups += 1
                user.downs -= 1
                vote.up = True
                db.session.add(vote)
        elif action == 'down':
            if vote is None:
                user.downs += 1
                vote = Vote(down=True, voter_id=current_user.id, user_id=id)
                db.session.add(vote)
            elif vote.down:
                user.downs -= 1
                db.session.delete(vote)
                vote = None
            elif vote.up:
                user.downs += 1
                user.ups -= 1
                vote.down = True
                db.session.add(vote)
        else:
            abort(404)

        db.session.add(user)
        db.session.commit()
        if vote:
            voted = True
        else:
            voted = False
        return jsonify(result='success', value=user.ups-user.downs, has_voted=voted)

    return jsonify(result='error')
