from datetime import datetime, timedelta
from . import db, Mood, Website

def calculate_average_confidence(mood, thisCondidence):
    moodDuration = (mood.endTime - mood.startTime).total_seconds()
    thisDuration = (datetime.now() - mood.endTime).total_seconds()
    
    # Weight the average by the duration of mood duration & added duration
    if mood.average_accuracy is None:
        return thisCondidence
    return (mood.average_accuracy * moodDuration + thisCondidence * thisDuration) / (moodDuration + thisDuration)    

def update_moods(mood, confidence):    
    # Save the mood to the database
    # First, check what the most recent mood was
    lastMood = db.session.query(Mood).order_by(Mood.endTime.desc()).first()
    
    if (lastMood is None) or (lastMood.type != mood) or (lastMood.endTime < datetime.now() - timedelta(seconds=3)):
        # Save the mood if it's different from the last mood or the last mood was more than 3 seconds ago
        print("Saving new mood")
        db.session.add(
            Mood(type=mood, 
                 startTime=datetime.now() - timedelta(seconds=1), 
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
    
def percent_moods_in_timeframe(start_time, end_time):
    moodDurations = moods_in_timeframe(start_time, end_time)
    totalDuration = sum(moodDurations.values())
    for mood in moodDurations:
        moodDurations[mood] = moodDurations[mood] / totalDuration
    return moodDurations

def moods_in_timeframe(start_time, end_time):
    moods = db.session.query(Mood).filter(Mood.endTime >= start_time, Mood.startTime <= end_time).all()
    moodDurations = {}
    for mood in moods:
        duration = (min(mood.endTime, end_time) - max(mood.startTime, start_time)).total_seconds()
        if mood.type not in moodDurations:
            moodDurations[mood.type] = 0
        moodDurations[mood.type] += duration
    return moodDurations

def getDomain(url):
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):
        url = url[8:]
    if url.startswith("www."):
        url = url[4:]
    # Remove everything after domain name
    url = url.split("/")[0]
    return url

# Checks if domain from url is same as given domain
def sameDomain(url, domain):
    return getDomain(url) == domain

def moods_in_timeframe_for_domain(domain, start_time, end_time):
    allWebsites = db.session.query(Website).filter(Website.endTime >= start_time, Website.startTime <= end_time).all()
    websites = []
    for website in allWebsites:
        if sameDomain(website.name, domain):
            websites.append(website)
            
    # Combine mood breakdowns for each time using the website
    moodDurations = {}
    for website in websites:
        moods = moods_in_timeframe(website.startTime, website.endTime)
        for mood in moods:
            if mood in moodDurations:
                moodDurations[mood] += moods[mood]
            else:
                moodDurations[mood] = moods[mood]
    return moodDurations

def get_all_domains_pretty(start_time, end_time):
    domains = get_all_domains(start_time, end_time)
    for domain in domains:
        domains[domain] = pretty_duration(timedelta(seconds=domains[domain]))
    return domains

def get_all_domains(start_time, end_time):
    domains = {}
    websites = db.session.query(Website).filter(Website.endTime >= start_time, Website.startTime <= end_time).all()
    for website in websites:
        domain = getDomain(website.name)
        if domain not in domains:
            domains[domain] = (website.endTime - website.startTime).total_seconds()
        else:
            domains[domain] += (website.endTime - website.startTime).total_seconds()        
    return domains

def total_time(start_time, end_time):
    moods = db.session.query(Mood).filter(Mood.endTime >= start_time, Mood.startTime <= end_time).all()
    totalDuration = 0
    for mood in moods:
        duration = (min(mood.endTime, end_time) - max(mood.startTime, start_time)).total_seconds()
        totalDuration += duration
    return timedelta(seconds=totalDuration)

def pretty_duration(duration):
    if duration.seconds >= 60 * 60:
        return str(duration.seconds // (60 * 60)) + " hour" + ("s" if duration.seconds // (60 * 60) > 1 else "")
    if duration.seconds >= 60:
        return str(duration.seconds // 60) + " minute" + ("s" if duration.seconds // 60 > 1 else "")
    else:
        return str(duration.seconds) + " second" + ("s" if duration.seconds > 1 else "")

def pretty_total_time(start_time, end_time):
    return pretty_duration(total_time(start_time, end_time))
    
def get_first_mood_time():
    firstMood = db.session.query(Mood).order_by(Mood.startTime).first()
    if firstMood is None:
        return datetime.now()
    return firstMood.startTime

def receive_site_usuage_data(data):
    # Save to database, combining timestamps into start and end times
    lastSite = db.session.query(Website).order_by(Website.endTime.desc()).first()
    lastTime = None
    for site in data:
        time = datetime.fromtimestamp((int(data[site])//1000))
        if lastSite is not None and lastSite.name == site and lastSite.endTime > time - timedelta(minutes=1):
            # Update the end time of the last site
            db.session.query(Website).filter(Website.id == lastSite.id).update({
                Website.endTime: time
                })
        else:
            # Save the site if it's different from the last site or the last site was more than 1 minute ago            
            startTime = lastTime if lastTime is not None else time - timedelta(minutes=1)
            db.session.add(
                Website(name=site, 
                        startTime=startTime, 
                        endTime=time
                ))
        lastTime = time
    db.session.commit()