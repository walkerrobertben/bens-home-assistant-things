import os 

script_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(script_dir, '.env')

def load_env():
    env = {}
    with open(env_file, 'r') as content:
        for line in content:
            if line.startswith('#'):
                continue
            key, value = line.strip().split('=')
            env[key] = value
    return env

env = load_env()

HOSTAWAY_ACCOUNT = env.get('HOSTAWAY_ACCOUNT')
HOSTAWAY_API_KEY = env.get('HOSTAWAY_API_KEY')

if HOSTAWAY_ACCOUNT is None or HOSTAWAY_API_KEY is None:
    raise Exception('HOSTAWAY_ACCOUNT and HOSTAWAY_API_KEY are required')

print(HOSTAWAY_ACCOUNT)
print(HOSTAWAY_API_KEY)
