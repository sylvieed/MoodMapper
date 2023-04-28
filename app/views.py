import json
from flask import render_template, request

from . import app
from .helpers import update_moods

@app.route("/")
def home():
    return render_template('index.html')
    
@app.route("/save_mood", methods=["POST"])
def save_mood():
    # Get the expression data from the request
    expressions = json.loads(request.form['expressions'])
    
    # look for the mood in the expressions with the highest confidence
    mood = max(expressions, key=lambda x: expressions[x])
    
    # Avoid having neutral as the mood
    if mood == "neutral":
        nonNeutralExpressions = {key: expressions[key] for key in expressions.keys() if key != "neutral"}
        secondMood = max(nonNeutralExpressions, key=lambda x: nonNeutralExpressions[x])
        if expressions[secondMood] > 0.3 and secondMood != "sad":
            print("Avoiding neutral mood")
            mood = secondMood
    
    print(mood, expressions[mood])
    update_moods(mood, expressions[mood])
    
    return "Success"