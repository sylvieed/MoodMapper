from app import db

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64))
    startTime = db.Column(db.DateTime)
    endTime = db.Column(db.DateTime)
    average_accuracy = db.Column(db.Float)
    