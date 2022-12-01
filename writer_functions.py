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

    location = spec_capwords(location)
    location = location.split(' ')
    
    if '@' in location: 
        location[location.index('@')] = 'at'

    if 'Mm' in location:
        mm_index = location.index('Mm')

        location[mm_index] = 'mile marker'
        location.append(mile_marker)

    location = ' '.join(location)

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

# Process county name
def county_process(county):
    return spec_capwords(county) + " County"

# Process city name
def city_process(city):
    city = city.split(' ')

    if len(city) > 1 and len(city[-1]) == 2:
        # If the city is a city in Arkansas, remove AR
        if city[-1] == "AR":
            city = city[:-1]
            city = spec_capwords(' '.join(i for i in city))

        # Can assume that the last word in city is a state abreviation
        else : 
            state = city[-1]
            city = spec_capwords(' '.join(i for i in city[:-1]))
            city = city + state
    else: 
        city = spec_capwords(' '.join(i for i in city))

    return city

# Specialized capwords function 
def spec_capwords(words):

    words = words.upper()

    # words in which no letters should be capitalized 
    not_cap = ['OF', 'ON', 'A', 'THE', 'IN', 'AT', 'MILE', 'AND', 'MARKER', 'MILE-MARKER', 'UNSPECIFIED', 'VEHICLE']

    # words in which all letters should be capitalized
    all_cap = ['GMC', 'US', 'U.S','U.S.', 'AR', 'NW', 'I', 'II', 'III', 'IV', 'V', 'UAMS', 'KIA']

    # cardinal directions are capitalized when part of a proper noun
    directions = ['NORTH', 'SOUTH', 'EAST', 'WEST']

    # words that should be replaced with other words
    to_replace = {'MC': 'motorcycle'}
    keys_to_replace = list(to_replace.keys())

    words = words.split(' ')

    # iterate through words determining which should be capitialized
    for i in range(len(words)): 
        if words[i] in not_cap:
            words[i] = words[i].lower()
        elif words[i] in all_cap:
            words[i] = words[i].upper()
        elif words[i] in directions:
            try: 
                following_word = words[i+1]
                # lowercase cardinal direction if indicates a direction
                if following_word in ['OF', 'ON', 'IN', 'WAS']:
                    words[i] = words[i].lower()
                else: 
                    words[i] = words[i].capitalize()
            except:
                words[i] = words[i].lower()
        elif words[i] in keys_to_replace:
            words[i] = to_replace[words[i]]
        else: 
            words[i] = words[i].capitalize()

    words = ' '.join(word for word in words)

    return words

# Convert directions into cardinal directions 
def direction_convert(direction):
    direction = direction.lower()
    match direction:
        case 'sb':
            direction = 'south'
        case 'nb':
            direction = 'north'
        case 'eb':
            direction = 'east'
        case 'wb':
            direction = 'west'
    return(direction)

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
    county = county_process(fatal_dict['county'])

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
        name = deceased[0]
        deceased_dict = fatal_dict['deceased'][name]
        residence = city_process(deceased_dict['RESIDENCE'])
        sex = sex_convert(deceased_dict['M/F'])[0]

        # If there was only one vehicle involved, change "one" to "single"
        num_vehicles = num_vehicles[0] if not num_vehicles[0] == "one" else "single"

        # Make sure the deceased person has a residence 
        if residence: 

            # Determine lead article
            article = "A"

            if residence[0] == "A":
                article = "An"

            lede = article + " " + residence + " " + sex + " died in a " + num_vehicles + "-vehicle accident " +  week_day +  " on " + location  + " in " + county + ".\n"

        # If no residence listed for deceased person, try to lead with their sex 
        elif sex:
            lede = "A " + sex + " died in a " + num_vehicles + "-vehicle accident " +  week_day +  " on " + location  + " in " + county + ".\n" 

        # If no sex is listed, the person is not a juvenile, lead with person
        elif name == 'JUVENILE':
            lede = "A juvenile died in a " + num_vehicles + "-vehicle accident " +  week_day +  " on " + location  + " in " + county + ".\n" 
        else: 
            lede = "A person died in a " + num_vehicles + "-vehicle accident " +  week_day +  " on " + location  + " in " + county + ".\n" 

    # If more than one person died in the accident, lead with the number dead
    else: 
        num_deceased = news_num_convert(num_deceased)

        # If the number of people dead is in word format
        if num_deceased[1]: 
            lede = num_deceased[0].capitalize() + " people died in an accident " + week_day + " involving " + num_vehicles[0] + " vehicles on " + location  + ' in ' + county + ".\n"
        else: 
            # If there was only one vehicle involved, change "one" to "single"
            num_vehicles = num_vehicles[0] if not num_vehicles[0] == "one" else "single"

            # Determine lead article
            article = "A"

            if num_vehicles[0] == "A":
                article = "An"

            lede = article + num_vehicles + "-vehicle accident claimed the lives of " + num_deceased[0] + " on " + location + ' in ' + county +  " " + week_day + ".\n"

    return lede

# Gets the vehicle type and heading 
def get_vehicle_details(vehicle_dict, vehicle_num):
    # Ensure direction and vehicle type included 
    try: 
        vehicle_details = vehicle_dict[vehicle_num]
    except:
        direction = "in an unspecified direction"
        vehicle = "unspecified vehicle"
        return vehicle, direction

    try:
        direction = vehicle_details['DIRECTION']
    except:
        direction = "in an unspecified direction"
    try:
        vehicle = vehicle_details['VEHICLE']
    except:
        vehicle = "unspecified vehicle"

    return spec_capwords(vehicle), spec_capwords(direction)


# Generate narrative of the crash
def gen_narrative(fatal_dict):

    # Get time 
    time  = fatal_dict['time']

    # Var for holding the narrative
    narrative = "The accident occurred around " + time + ". "

    names = list(fatal_dict['deceased'].keys())

    counter = 0

    # Add details about each deceased person
    for name in names: 
        # Get details 
        deceased_dict = fatal_dict['deceased'][name]
        age = deceased_dict['AGE']
        sex = deceased_dict['M/F']
        role = deceased_dict['ROLE']

        # Variable for the vehicles the deceased people were in
        deceased_vehicles = []

        if age.lower() == "unknown":
            age = "of unknown age"

        if role == 'PEDESTRIAN':
            narrative = narrative +  spec_capwords(name) + ", " + age + ", was listed as a pedestrian in a report from Arkansas State Police. "
        else: 
            vehicle_num = deceased_dict['VEHICLE']
            deceased_vehicles.append(vehicle_num)

            vehicle, direction = get_vehicle_details(fatal_dict['vehicles'], vehicle_num)

            if role == 'DRIVER':
                narrative = narrative + spec_capwords(name) + ", " + age + ", was driving " + direction_convert(direction) + " in a " + spec_capwords(vehicle) +". "
            else: 
                narrative = narrative + spec_capwords(name) + ", " + age + ", was riding in a " + spec_capwords(vehicle) + " headed " + direction_convert(direction) + ". "

    vehicle_nums = list(fatal_dict['vehicles'].keys())

    # Include details about other vehicles in the accident 
    for vehicle_num in vehicle_nums:
        if vehicle_num not in deceased_vehicles:

            vehicle, direction = get_vehicle_details(fatal_dict['vehicles'], vehicle_num)

            # Determine lead article
            article = "A"

            if vehicle[0] == "A":
                article = "An"
            narrative = narrative + article + " " + spec_capwords(vehicle)+ " headed " + spec_capwords(direction) + " was also involved in the accident. "

    narrative = narrative + "\n"

    return narrative


# Generate sentences about how many people were injured and where they were transported
def gen_injuries(fatal_dict):

    injured = fatal_dict['injured']
    hospital = spec_capwords(fatal_dict['hospital'])

    # Var to hold blurb about injuries 
    blurb = ""

    # Get the number of people who died in the accident 
    num_injured = len(injured)

    # More than one person was injuried, just list how many people were injured
    if num_injured > 1 : 
        blurb = "There were " + news_num_convert(num_injured)[0] + " other people injuried. Those injured were taken to " + hospital + ".\n"

    # If there were no other injuries 
    elif num_injured == 0 : 
        blurb = "No other injuries or deaths were reported.\n"

    # If there was only one other injury 
    else: 
        injured_name = list(injured.keys())[0]
        injured_age = injured[injured_name]['AGE']
        injured_residence = injured[injured_name]['RESIDENCE']
        injured_sex = injured[injured_name]['M/F']
        role = injured[injured_name]['ROLE']

        pronoun = sex_convert(injured_sex)[1].capitalize()

        if role == 'PEDESTRIAN':
            blurb = spec_capwords(injured_name) + ", " + injured_age + ", of " + city_process(injured_residence) + " was injured in the accident. " 
            blurb = blurb + pronoun + " was listed as a pedestrian in the report and was transported to " + hospital + ".\n"
        
        elif role == 'DRIVER': 
            vehicle_num = injured[injured_name]['VEHICLE']
            vehicle, direction = get_vehicle_details(fatal_dict['vehicles'], vehicle_num)
            blurb = spec_capwords(injured_name) + ", " + injured_age + ", of " + city_process(injured_residence) + " was injured in the accident. " 
            blurb = blurb + pronoun + " was driving the " + vehicle + " and was transported to " + hospital + ".\n"
        elif role == 'PASSENGER':
            vehicle_num = injured[injured_name]['VEHICLE']
            vehicle, direction = get_vehicle_details(fatal_dict['vehicles'], vehicle_num)
            blurb = spec_capwords(injured_name) + ", " + injured_age + ", of " + city_process(injured_residence) + " was injured in the accident. " 
            blurb = blurb + pronoun + " was riding in the " + vehicle + " and was transported to " + hospital + ".\n"

        else: 
            blurb = spec_capwords(injured_name) + ", " + injured_age + ", of " + city_process(injured_residence) + " was injured in the accident. " 
            blurb = blurb + pronoun + " was transported to " + hospital + ".\n"

    return blurb

# Generate a sentence about weather/road conditions
def gen_conditions(weather, road):
    # Var to hold sentence about road/weather 
    sentence = ""

    if "rain" in weather or "snow" in weather or "fog" in weather:

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
                sentence = "The weather was " + weather + " and the road was " + road + ", according to the report.\n"
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
    message = message + gen_injuries(fatal_dict)

    # Mention weather/road conditions
    message = message + gen_conditions(fatal_dict['weather_conditions'].lower(), fatal_dict['road_conditions'].lower())

    # Include link to full report 
    message = message + "Read the full report here: " + driver.current_url 

    print(message)