from flask import session
from datetime import datetime
from . import db, Mood

def calculate_average_confidence(mood, thisCondidence):
    moodDuration = (mood.endTime - mood.startTime).total_seconds()
    thisDuration = (datetime.now() - mood.endTime).total_seconds()
    
    # Weight the average by the duration of mood duration & added duration
    if mood.average_accuracy is None:
        return thisCondidence
    return (mood.average_accuracy * moodDuration + thisCondidence * thisDuration) / (moodDuration + thisDuration)    

def update_moods(mood, confidence):
    # Update last record saved at
    session["last_saved_at"] = datetime.now()
    
    # Save the mood to the database
    # First, check what the most recent mood was
    lastMood = db.session.query(Mood).order_by(Mood.endTime.desc()).first()
    
    if (lastMood is None) or (lastMood.type != mood):
        # Save the mood if it's different from the last mood
        print("Saving new mood")
        db.session.add(
            Mood(type=mood, 
                 startTime=session["last_saved_at"], 
                 endTime=datetime.now(),
                 average_accuracy=confidence
            ))
    else:
        # Update the end time of the last mood
        print("Updating last mood")
        db.session.query(Mood).filter(Mood.id == lastMood.id).update({
            Mood.endTime: datetime.now(),
            Mood.average_accuracy: calculate_average_confidence(lastMood, confidence)
            })
    
    db.session.commit()