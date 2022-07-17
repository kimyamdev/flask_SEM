from hashlib import md5
from datetime import datetime
from multiprocessing import AuthenticationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    asset_updates = db.relationship('Asset_Update', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(140), index=True, unique=True)
    asset_thesis = db.Column(db.String(1200), index=True, unique=True)
    asset_type = db.Column(db.String(140))
    asset_class = db.Column(db.String(140))
    # asset_updates = db.relationship('Asset_Update', backref='asset', lazy='dynamic')

    def __repr__(self):
        return '<Asset {}>'.format(self.asset_name)

class Asset_Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(140))
    asset_update_title = db.Column(db.String(140))
    asset_update_content = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Asset_Update {}>'.format(self.asset_update_title)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))