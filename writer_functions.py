import string
import datetime
import calendar
import random

# Converts an int to AP Style number and returns a tuple with converted value and a boolean for whether or not number is in word form
def news_num_convert(num):
    is_word = False
    num_dict = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'}
    if 9 > num > 0:
        num = str(num)
        num = num_dict[num]
        is_word = True
    else: 
        num = str(num)
    return num, is_word

# Converts location to style format 
def location_convert(location):

    if 'MM' in location:
        location = string.capwords(location)
        location = location.split(' ')
        mm_index = location.index('Mm')

        mile_marker = location[mm_index-1]

        location[mm_index-1], location[mm_index] = 'near', 'mile marker'
        location.append(mile_marker)

        location = ' '.join(location)

    else: 

        location = string.capwords(location)

    return location

# Converts sex to style format
def sex_convert(sex): 
    pronoun = 'he'
    if sex == 'M':
        sex = 'man'
    elif sex == "F":
        sex = 'woman'
        pronoun = 'she'
    return sex, pronoun

# Get appropriate jursidicition 
def get_jurisdiction(city, county):
    return string.capwords(county) + " County"


# Generate lede for message 
def gen_lede (fatal_dict):

    # Var to hold lede
    lede = ""

    # Get the number of people who died in the accident 
    num_deceased = len(fatal_dict['deceased'])

    # Get and process the number of vehicles involved in the crash
    num_vehicles = news_num_convert(len(fatal_dict['vehicles']))

    # Get and process location
    location = location_convert(fatal_dict['location'])

    # Get and process county 
    county = string.capwords(fatal_dict['county']) + ' County'
    jursidiction = get_jurisdiction(fatal_dict['city'], fatal_dict['county'])

    # Names of the deceased 
    deceased = list(fatal_dict['deceased'].keys())

    # Get day of week of crash 
    str_date = fatal_dict['date']
    date_format = '%m/%d/%Y'
    date = datetime.datetime.strptime(str_date, date_format).date()
    week_day = calendar.day_name[date.weekday()]
 
    # If one person died in the accident, lead with details about the victim
    if num_deceased == 1:

        # Get details of the single deceased person 
        deceased_dict = fatal_dict['deceased'][deceased[0]]
        residence = string.capwords(deceased_dict['RESIDENCE'])
        sex = sex_convert(deceased_dict['M/F'])[0]

        lede = "A " + residence + " " + sex + " died in a " + num_vehicles[0] + "-vehicle accident " +  week_day +  " on " + location  + " in " + jursidiction + ".\n"

    # If more than one person died in the accident, lead with the number dead
    else: 
        num_deceased = news_num_convert(num_deceased)

        # If the number of people dead is in word format
        if num_deceased[1]: 
            lede = num_deceased[0].capitalize() + " people died in an accident " + week_day + " involving " + num_vehicles[0] + " vehicles on " + location  + ' in ' + jursidiction + ".\n"
        else: 
            lede = "A " + num_vehicles[0] + " vehicle accident claimed the lives of " + num_deceased[0] + " on " + location + ' in ' + jursidiction +  " " + week_day + ".\n"

    return lede

# Generate narrative of the crash
def gen_narrative(fatal_dict):

    # Get time 
    time  = fatal_dict['time']

    # Var for holding the narrative
    narrative = "The accident occurred around " + time + ". "

    names = list(fatal_dict['deceased'].keys())

    counter = 0

    for name in names: 
        deceased_dict = fatal_dict['deceased'][name]
        age = deceased_dict['AGE']
        sex = deceased_dict['M/F']
        role = deceased_dict['ROLE']

        if role == 'PEDESTRIAN':
            narrative = narrative +  string.capwords(name) + ", " + age + "was listed as a pedestrian in a report from Arkansas State Police. "
        else: 
            vehicle_num = deceased_dict['VEHICLE']
            vehicle_details = fatal_dict['vehicles'][vehicle_num]

            if role == 'DRIVER':
                narrative = narrative + string.capwords(name) + ", " + age + ", was driving " + vehicle_details['DIRECTION'].lower() + " in a " + vehicle_details['VEHICLE'].lower() + ". "
            else: 
                narrative = narrative + string.capwords(name) + ", " + age + ", was riding in a " + vehicle_details['VEHICLE'].lower() + " headed " + vehicle_details['DIRECTION'].lower() + ". "
    narrative = narrative + "\n"

    return narrative


# Generate sentences about how many people were injured and where they were transported
def gen_injuries(injured, hospital):
    # Var to hold blurb about injuries 
    blurb = ""

    # Get the number of people who died in the accident 
    num_injured = len(injured)

    hospital = string.capwords(hospital)

    # More than one person was injuried, just list how many people were injured
    if num_injured > 1 : 
        blurb = "There were " + news_num_convert(num_injured)[0] + " other people injuried in the crash. Those injured were taken to " + hospital + ".\n"

    # If there were no other injuries 
    elif num_injured == 0 : 
        blurb = "No other injuries or deaths were reported from the crash.\n"

    # If there was only one other injury 
    else: 
        injured_name = list(injured.keys())[0]
        injured_age = injured[injured_name]['AGE']
        injured_residence = injured[injured_name]['RESIDENCE']
        injured_sex = injured[injured_name]['M/F']

        blurb = string.capwords(injured_name) + "," + injured_age + ", of " + string.capwords(injured_residence) + " was injured in the accident. "
        
        blurb = blurb + sex_convert(injured_sex)[1].capitalize()

        blurb = blurb + " was transported to " + hospital + ".\n"

    return blurb

# Generate a sentence about weather/road conditions
def gen_conditions(weather, road):
    # Var to hold sentence about road/weather 
    sentence = ""

    if "rain" in weather or "snow" in weather:

        # Randomly pick version of sentence to include in the message
        version = random.randint(1, 2)

        match version:
            case 1: 
                sentence = "There was " + weather + " at the time of the accident and the road was " + road + ", according to the report.\n"
            case 2: 
                sentence = "Police reported there was " + weather + " at the time of the accident and the road was " + road + ".\n"
    else:

        # Randomly pick version of sentence to include in the message
        version = random.randint(1, 2)

        match version:
            case 1: 
                sentence = "The weather was " + weather + " and the road was " + road + ", according to the report."
            case 2: 
                sentence = "Police reported the weather was " + weather + " and the road was " + road + ".\n"

    return sentence

# Generate a message based on the info in the last fatal file 
def gen_msg (fatal_dict, driver):

    # Generate a lede for the message 
    message = gen_lede(fatal_dict)

    # Add narrative details about those killed
    message = message + gen_narrative(fatal_dict)

    # Add details about those injured
    message = message + gen_injuries(fatal_dict['injured'], fatal_dict['hospital'])

    # Mention weather/road conditions
    message = message + gen_conditions(fatal_dict['weather_conditions'].lower(), fatal_dict['road_conditions'].lower())

    # Include link to full report 
    message = message + "Read the full report here: " + driver.current_url 

    print(message)




