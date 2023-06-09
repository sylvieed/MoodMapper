import json
from flask import redirect, render_template, request, url_for
from datetime import datetime, time

from . import app
from .helpers import *

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/dashboard', defaults={'timeframe': None})
@app.route("/dashboard/<timeframe>")
def dashboard(timeframe):
    # Define Plot Data
    # today = datetime.combine(datetime.now(), time.min)
    if timeframe is None or timeframe is 'all':
        start = get_first_mood_time()
    elif timeframe == 'today':
        start = datetime.combine(datetime.now(), time.min)
    elif timeframe == 'week':
        start = datetime.now() - timedelta(days=7)
    elif timeframe == '60':
        start = datetime.now() - timedelta(minutes=60)
    elif timeframe == '10':
        start = datetime.now() - timedelta(minutes=10)
    elif timeframe == '5':
        start = datetime.now() - timedelta(minutes=5)        
        
    moods = percent_moods_in_timeframe(start, datetime.now())
    
    # Combine small moods into "other"
    moods["other"] = 0
    for mood in moods:
        if moods[mood] < 0.01:
            moods["other"] += moods[mood]
    
    # Remove any moods too small to be displayed
    moods = {key: moods[key] for key in moods.keys() if moods[key] > 0.01}
    print(moods)
    
    labels = list(moods.keys())
    # Round each value in moods to two decimal places
    data = [round(confidence, 2) for confidence in moods.values()]
    
    time_used = pretty_total_time(start, datetime.now())
    print(time_used)
    
    domains = get_all_domains(start, datetime.now())
    print(domains)

    return render_template('dashboard.html', data=data, labels=labels, time_used=time_used, domains=domains)

@app.route("/filter", methods=["POST"])
def filter():
    value = request.form.get('time-filter')
    return redirect(url_for('dashboard', timeframe=value))
    

@app.route("/websites")
def websites():
    data = {}
    domains = get_all_domains(get_first_mood_time(), datetime.now())
    for domain in domains:
        data[domain] = moods_in_timeframe_for_domain(domain, get_first_mood_time(), datetime.now())
        
    times = get_all_domains_pretty(get_first_mood_time(), datetime.now())
        
    # Remove empty domains
    domains = {key: domains[key] for key in domains.keys() if len(data[key]) > 0}
    data = {key: data[key] for key in data.keys() if len(data[key]) > 0}
    
    labels = {}
    for domain in data:
        labels[domain] = list(data[domain].keys())
    values = {}
    for domain in data:
        values[domain] = list(data[domain].values())
    
    return render_template('websites.html', labels=labels, data=values, domains=list(domains.keys()), times=times)

@app.route("/tutorial")
def tutorial():
    return render_template('tutorial.html')

@app.route("/faq")
def faq():
    return render_template('faq.html')

@app.route("/privacy")
def privacy():
    return render_template('privacy.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')
    
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

@app.route("/get_websites", methods=["POST"])
def get_websites():
    receive_site_usuage_data(request.form)
    return redirect(url_for('home'))
