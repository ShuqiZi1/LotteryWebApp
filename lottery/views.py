# IMPORTS
import logging
import copy
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user

from app import db, requires_roles
from models import Draw, User

# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# temporary code to get the test user's key
# user = User.query.first()
# draw_key = user.draw_key


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
@login_required
@requires_roles('user')
def lottery():
    return render_template('lottery.html')


@lottery_blueprint.route('/add_draw', methods=['POST'])
@login_required
@requires_roles('user')
def add_draw():
    submitted_draw = ''
    for i in range(6):
        submitted_draw += request.form.get('no' + str(i + 1)) + ' '
    submitted_draw.strip()

    # create a new draw with the form data.
    # new_draw = Draw(user_id=1, draw=submitted_draw, win=False, round=0, draw_key=draw_key)
    new_draw = Draw(user_id=current_user.id, draw=submitted_draw, win=False,
                    round=0, draw_key=current_user.draw_key)  # TODO: update user_id [user_id=1 is a placeholder]

    # add the new draw to the database
    db.session.add(new_draw)
    db.session.commit()

    # re-render lottery.page
    flash('Draw %s submitted.' % submitted_draw)
    return lottery()


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
@login_required
@requires_roles('user')
def view_draws():
    # get all draws that have not been played [played=0]
    playable_draws = Draw.query.filter_by(user_id=current_user.id).filter_by(
        played=False).all()  # TODO: filter playable draws for current user

    # if playable draws exist
    if len(playable_draws) != 0:
        # creates a list of copied playable draws objects which are independent of database.
        playable_draws_copies = list(map(lambda x: copy.deepcopy(x), playable_draws))

        # empty list for decrypted copied draws objects
        decrypted_playable_draws = []

        # decrypt each copied draw object and add it to decrypted_playaber_draws array.
        for p in playable_draws_copies:
            p.view_draw(current_user.draw_key)
            decrypted_playable_draws.append(p)

        # re-render lottery page with playable draws
        return render_template('lottery.html', playable_draws=decrypted_playable_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
@login_required
@requires_roles('user')
def check_draws():
    # get played draws
    played_draws = Draw.query.filter_by(user_id=current_user.id).filter_by(
        played=True).all()  # TODO: filter played draws for current user

    # if played draws exist
    if len(played_draws) != 0:
        # creates a list of copied played draws objects which are independent of database.
        played_draws_copies = list(map(lambda x: copy.deepcopy(x), played_draws))

        # empty list for decrypted copied draws objects
        decrypted_played_draws = []

        # decrypt each copied draw object and add it to decrypted_played_draws array.
        for p in played_draws_copies:
            p.view_draw(current_user.draw_key)
            decrypted_played_draws.append(p)

        return render_template('lottery.html', results=decrypted_played_draws, played=True)

    # if no played draws exist, all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
@login_required
@requires_roles('user')
def play_again():
    # delete played draws for current user only
    delete_played = Draw.__table__.delete().where(
        Draw.user_id == current_user.id).where(Draw.played)  # TODO: delete played draws for current user only
    db.session.execute(delete_played)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()
