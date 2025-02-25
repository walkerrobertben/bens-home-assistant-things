# This script is a 'template' which gets generated by fetch_bookings placed into
# the home assistant python_scripts directory When home assistant runs this within
# the sandbox, it will have access to 'hass' object and can update the attribute.

### BOOKINGS_DATA (Set by fetch_bookings.py)
bookings = []
####

logger.debug('Storing', len(bookings), 'bookings...')

# get the entity
entity_id = "input_button.bookings_data"
entity = hass.states.get(entity_id)

# dict() is undefined, so build new dict manually
attributes = {}
for attr in entity.attributes:
    attributes[attr] = entity.attributes.get(attr)

# Update the bookings attribute
attributes["bookings"] = bookings

# Set the new state with updated attributes
hass.states.set(entity_id, entity.state, attributes)

# Log the update
logger.debug('Bookings attribute updated')
output["bookings"] = "Stored " + str(len(bookings)) + " bookings"
