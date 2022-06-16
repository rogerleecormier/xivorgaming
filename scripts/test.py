from gw2api import GuildWars2Client
import requests
from ratelimit import limits, RateLimitException, sleep_and_retry
from concurrent.futures import ThreadPoolExecutor as PoolExecutor

gw2 = GuildWars2Client()
ONE_MINUTE = 60
MAX_CALLS_PER_MINUTE = 30
search_term = "traits"
traits = []

print("Pulling data from the GW2 API...")
for i in gw2.traits.get():
    traits.append(i)

print("Calculating total data pieces...")
cntTraits = len(traits)
        
@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
def access_rate_limited_api(count):
    for i in range(0, cntTraits):
        i=int(i)
        resp = gw2.traits.get(id=i)
        print(f"{count}.{resp}")    
        

with PoolExecutor(max_workers=3) as executor:
    for _ in executor.map(access_rate_limited_api, range(60)):
        pass 
