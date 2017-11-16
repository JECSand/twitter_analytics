import os
import json
import random
import pip
import webbrowser
import config


# Package installer function to handle missing packages
def install(package):
    print(package + ' package for Python not found, pip installing now....')
    pip.main(['install', package])
    print(package + ' package has been successfully installed for Python\n Continuing Process...')


try:
    from geopy.geocoders import Nominatim
except:
    install('geopy')
    from geopy.geocoders import Nominatim

geolocator = Nominatim()
cwd = os.getcwd()
os_system = os.name
if os_system == 'nt':
    raw_tweet_file_dir = cwd + '\\batch_extracts\\complete\\'
    browser_map_dir = cwd + '\\browser_map\\'
    geo_json_dir = browser_map_dir + '\\geojson\\'
else:
    raw_tweet_file_dir = cwd + '/batch_extracts/complete/'
    browser_map_dir = cwd + '/browser_map/'
    geo_json_dir = browser_map_dir + '/geojson/'


# Function to get data from twitter batch files
def get_twitter_batch():
    raw_tweets_list = []
    for root, dirnames, filenames in os.walk(raw_tweet_file_dir):
        for filename in filenames:
            with open(os.path.join(root, filename), 'r') as raw_tweet_file:
                for raw_tweet_json in raw_tweet_file:
                    raw_tweet = json.loads(raw_tweet_json)
                    raw_tweets_list.append(raw_tweet)
            raw_tweet_file.close()
    return raw_tweets_list


# Function to construct geojson feature
def get_geojson_feature(coordinates, text, created_at):
    geo_json_feature = {
        "type": "Feature",
        "geometry": coordinates,
        "properties": {
            "text": text,
            "created_at": created_at
        }
    }
    return geo_json_feature


# Tweets are stored in "fname"
geo_data = {
    "type": "FeatureCollection",
    "features": []
}

print('Building geojson file\nThis may take a moment....')
for tweet in get_twitter_batch():
    if tweet['lang'] == 'en':
        if tweet['coordinates']:
            geo_json_feature = get_geojson_feature(tweet['coordinates'], tweet['text'], tweet['created_at'])
            geo_data['features'].append(geo_json_feature)
        else:
            if tweet['user']['location'] is not None:
                if ',' in tweet['user']['location']:
                    geo_location = geolocator.geocode(tweet['user']['location'], timeout=None)
                    if geo_location is not None:
                        geo_shif_val = random.randint(1, 9) / 1000000
                        tweet_coords = [geo_location.longitude - geo_shif_val, geo_location.latitude - geo_shif_val]
                        coords_objt = {"type": "Point", "coordinates": tweet_coords}
                        geo_json_feature = get_geojson_feature(coords_objt, tweet['text'], tweet['created_at'])
                        geo_data['features'].append(geo_json_feature)

# Save geo data
with open(geo_json_dir + 'geo_data.json', 'w') as fout:
    fout.write(json.dumps(geo_data, indent=4))
    fout.close()
print('Geojson file has been built! Opening browser to view map and exiting...')

# Open geomap html file in user's default webbrowser
local_url = browser_map_dir + 'twitter_geomap.html'
webbrowser.open('file://' + local_url, new=2)
