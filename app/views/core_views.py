import logging
logger = logging.getLogger(__name__)

from app import app, tools
from app.database.models import Settings, db
from flask import render_template, request, redirect
from flask_security import login_required, current_user

#THIS SHOULD REALLY BE /DASH and should @login_required to be safe
@app.route('/', methods=['GET'])
def index():
    try:
        settings_id = request.args.get('i');
        if current_user.is_authenticated and settings_id:
            settings = Settings.query.filter_by(id=str(settings_id), user_id=current_user.id).first()
            articles = tools.get_news(q=settings.q, sources=settings.sources)
        else:
            articles = tools.get_news()

        weather = tools.get_weather()
    except Exception as e:
        return str(e)

    return render_template('index.html',
                           articles=articles,
                           weather=weather,
                           settings_id=settings_id,
                           weather_city='Edinburgh') #This is to change according to user settings

@app.route('/settings')
@login_required
def settings():
    return render_template('user-settings.html')

@app.route('/settings-edit', methods=['POST'])
@login_required
def settingsEdit():
    try:
        sid = request.form.get('id')
        name = request.form.get('name')
        sources = request.form.get('sources')
        q = request.form.get('q')
        if sid:
            s = Settings.query.filter_by(id=int(sid)).first()
            s.name = name
            s.sources = sources
            s.q = q
            db.session.commit()
        else:
            s = Settings(sources=sources, q=q, name=name, user_id=current_user.id)
            db.session.add(s)
            db.session.commit()

    except Exception as e:
        return str(e)
    return redirect('/settings')

@app.route('/settings-delete', methods=['GET'])
@login_required
def settingsDelete():
    try:
        sid = request.args.get('i')
        Settings.query.filter_by(id=sid, user_id=current_user.id).delete()
        db.session.commit()
    except Exception as e:
        return str(e)
    return redirect('/settings')
