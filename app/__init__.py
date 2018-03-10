import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
frmtr = logging.Formatter('%(asctime)s > %(name)s::%(levelname)s - %(message)s')
sh.setFormatter(frmtr)
sh.setLevel(logging.INFO)
logger.addHandler(sh)

from flask import Flask
app = Flask(__name__)

import os, random, string
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "".join(random.choice(string.ascii_letters) for _ in range(10))
app.config['SECURITY_PASSWORD_SALT'] = "MWfYKxtEqdjsPgIntk9TFMc"
from app.views import core_views
from app.database import models
