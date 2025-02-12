import sys

db_schema = '/usr/src/homeassistant/homeassistant/components/recorder/db_schema.py'

def get_limits():
    MAX_STATE_ATTRS_BYTES = 0
    MAX_EVENT_DATA_BYTES = 0

    with open(db_schema, 'r') as file:
        for line in file:
            if line.startswith('MAX_STATE_ATTRS_BYTES = '):
                MAX_STATE_ATTRS_BYTES = int(line.split('=')[1].strip())
            if line.startswith('MAX_EVENT_DATA_BYTES = '):
                MAX_EVENT_DATA_BYTES = int(line.split('=')[1].strip())

    return {
        'MAX_STATE_ATTRS_BYTES': MAX_STATE_ATTRS_BYTES,
        'MAX_EVENT_DATA_BYTES': MAX_EVENT_DATA_BYTES
    }

def set_limit(key, value):
    with open(db_schema, "r") as file:
        lines = file.readlines()

    if not any(line.startswith(f"{key} = ") for line in lines):
        print("Cannot find line " + key + " in db_schema.py")
        return

    with open(db_schema, "w") as file:
        for line in lines:
            if line.startswith(f"{key} = "):
                file.write(f"{key} = {value}\n")
            else:
                file.write(line)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Getting limits...")
        print(get_limits())
    elif len(sys.argv) == 2:
        new_value = sys.argv[1]
        print("Patching limits to " + new_value)
        set_limit("MAX_STATE_ATTRS_BYTES", new_value)
        set_limit("MAX_EVENT_DATA_BYTES", new_value)
        print("Patched!")
        print(get_limits())
    else:
        print("Invalid usage. Run without arguments to view limits, or pass a single numeric value to update.")
