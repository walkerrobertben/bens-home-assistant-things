import os, http.client, urllib.parse, json, datetime

# directories
script_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = '/config/python_scripts'

# file names
script_template = 'update_template.py'
script_target = 'set_hostaway_bookings.py'

# environment
def load_env():
    env = {}
    with open(os.path.join(script_dir, '.env'), 'r') as content:
        for line in content:
            if line.startswith('#'):
                continue
            key, value = line.strip().split('=')
            env[key] = value
    return env

env = load_env()

IS_PROD = env.get('ENV') == 'prod'
HOSTAWAY_ACCOUNT = env.get('HOSTAWAY_ACCOUNT')
HOSTAWAY_API_KEY = env.get('HOSTAWAY_API_KEY')

if HOSTAWAY_ACCOUNT is None or HOSTAWAY_API_KEY is None:
    raise Exception('HOSTAWAY_ACCOUNT and HOSTAWAY_API_KEY are required')

# -----------------------------------------------------------------------
# when running on dev just put the generated script in the same directory
if not IS_PROD: target_dir = script_dir
# -----------------------------------------------------------------------

# hostaway api
def get_access_token():
    connection = http.client.HTTPSConnection("api.hostaway.com")

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }

    payload = {
        'grant_type': 'client_credentials',
        'client_id': HOSTAWAY_ACCOUNT,
        'client_secret': HOSTAWAY_API_KEY,
        'scope': 'general'
    }

    connection.request("POST", "/v1/accessTokens", urllib.parse.urlencode(payload), headers)
    response = connection.getresponse()
    response_data = json.loads(response.read().decode('utf-8'))

    return response_data.get('access_token')

# revoke endpoint is document here but seems to not be working
# https://api.hostaway.com/documentation?python#revoke-authentication-token

# def revoke_token(token):
#     connection = http.client.HTTPSConnection("api.hostaway.com")

#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Cache-Control': 'no-cache'
#     }

#     payload = {
#         'token': token,
#     }

#     connection.request("DELETE", "/v1/accessTokens", urllib.parse.urlencode(payload), headers)
#     response = connection.getresponse()
#     response_data = json.loads(response.read().decode('utf-8'))

def get_reservations_page(
    bearer_token,
    limit=100,
    offset=0,
    check_out_after=None,
):
    connection = http.client.HTTPSConnection("api.hostaway.com")

    headers = {
        'Authorization': 'Bearer ' + bearer_token,
        'Cache-Control': 'no-cache'
    }

    query = {
        'limit': limit,
        'offset': offset,
    }

    if check_out_after:
        query['departureStartDate'] = datetime.datetime.strftime(check_out_after, "%Y-%m-%d")

    connection.request("GET", "/v1/reservations?" + urllib.parse.urlencode(query), None, headers)
    response = connection.getresponse()
    response_data = json.loads(response.read().decode('utf-8'))

    return response_data.get('result')

def get_reservations(bearer_token):
    check_out_after = datetime.datetime.now() - datetime.timedelta(days=1)
    reservations = []
    offset = 0

    while True:
        page = get_reservations_page(
            bearer_token=bearer_token,
            limit=100,
            offset=offset,
            check_out_after=check_out_after
        )

        if page is None:
            raise Exception('No reservation page in response')
        
        if len(page) == 0:
            break # no more reservations

        reservations.extend(page)
        offset += len(page)

    return reservations

# hostaway reservation object is huge. we only need to store a few fields
def get_booking_object(reservation):
    id = reservation.get('id')
    listing_id = reservation.get('listingMapId')
    listing_name = reservation.get('listingName')
    arrivalDate = reservation.get('arrivalDate')
    departureDate = reservation.get('departureDate')
    checkInTime = float(reservation.get('checkInTime'))
    checkOutTime = float(reservation.get('checkOutTime'))

    checkInHour = int(checkInTime)
    checkOutHour = int(checkOutTime)
    checkInMinute = int((checkInTime - checkInHour) * 60)
    checkOutMinute = int((checkOutTime - checkOutHour) * 60)

    checkIn = f"{arrivalDate} {checkInHour:02d}:{checkInMinute:02d}:00"
    checkOut = f"{departureDate} {checkOutHour:02d}:{checkOutMinute:02d}:00"

    return {
        'id': id,
        'listing_id': listing_id,
        'listing_name': listing_name,
        'check_in_local': checkIn,
        'check_out_local': checkOut,
    }

# generate the script
def generate_bookings_script(reservations):
    bookings = [get_booking_object(reservation) for reservation in reservations]
    
    with open(os.path.join(script_dir, script_template), 'r') as template:

        template_lines = template.readlines()

        for i, line in enumerate(template_lines):
            if line.startswith('### BOOKINGS_DATA'):
                template_lines[i+1] = f"""bookings = {
                    json.dumps(bookings, indent=4)
                }\n"""
                break

        with open(os.path.join(target_dir, script_target), 'w') as output_script:
            output_script.writelines(template_lines)

# -----------------------------------------------------------------------

print('Getting access token')
token = get_access_token()

print('Getting reservations from hostaway')
reservations = get_reservations(token)

print('Generating script with', len(reservations), 'bookings')
generate_bookings_script(reservations)

print('Done')
