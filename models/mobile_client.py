from db import db

class MobileClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(255), unique=True, nullable=False)
    connected_at = db.Column(db.DateTime, default=db.func.now())
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_session.id'), nullable=False)
