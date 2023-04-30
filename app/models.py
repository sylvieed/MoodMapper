import app

class Mood(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    type = app.db.Column(app.db.String(64))
    startTime = app.db.Column(app.db.DateTime)
    endTime = app.db.Column(app.db.DateTime)
    average_accuracy = app.db.Column(app.db.Float)
    
class Website(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String(256))
    startTime = app.db.Column(app.db.DateTime)
    endTime = app.db.Column(app.db.DateTime)
