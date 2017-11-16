import os
import datetime
import json
import pip
import sys
import random
import config


# Package installer function to handle missing packages
def install(package):
    print(package + ' package for Python not found, pip installing now....')
    pip.main(['install', package])
    print(package + ' package has been successfully installed for Python\n Continuing Process...')


try:
    import tweepy
    from tweepy import Stream
    from tweepy.streaming import StreamListener
    from tweepy import OAuthHandler
except:
    install('tweepy')
    import tweepy
    from tweepy import Stream
    from tweepy.streaming import StreamListener
    from tweepy import OAuthHandler
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except:
    install('matplotlib')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
try:
    from geopy.geocoders import Nominatim
except:
    install('geopy')
    from geopy.geocoders import Nominatim
try:
    from mpl_toolkits.basemap import Basemap
except:
    install('mpl_toolkits')
    from mpl_toolkits.basemap import Basemap


# Authenticate to Twitter API and Geo-locator
geolocator = Nominatim()
auth = OAuthHandler(config.consumer_key, config.consumer_secret)
auth.set_access_token(config.access_token, config.access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=5,
                 retry_errors=5)


# Function to create the tweet tracker hash list from the configuration file's hash object
def hash_list():
    hash_list = []
    for hash_key in list(config.hash_obj.keys()):
        for hash_val in config.hash_obj[hash_key]:
            hash_list.append(hash_val)
    return hash_list


# Function to create color dict for map plotting colors
def generate_plot_colors():
    color_dict = {}
    config_obj = config.hash_obj
    key_list = list(config_obj.keys())
    created_colors = ['#cc9955']
    for key in key_list:
        r = lambda: random.randint(128, 255)
        while True:
            hex_color = '#%02X%02X%02X' % (r(), r(), r())
            if hex_color not in created_colors:
                created_colors.append(hex_color)
                color_dict.update({key: {'map_color': hex_color, 'key_words': config_obj[key]}})
                break
    return color_dict


# Get Plot Color for Current Map Plot
def get_plot_color(color_ob, tweet_text):
    color_ob_keys = list(color_ob.keys())
    for key in color_ob_keys:
        for key_word in color_ob[key]['key_words']:
            if key_word in tweet_text.lower():
                tweet_color = color_ob[key]['map_color']
                return tweet_color


# Create color legend
color_obj = generate_plot_colors()
labels = []
colors = []
for key in list(color_obj.keys()):
    key_color = color_obj[key]['map_color']
    labels.append(key.capitalize())
    colors.append(key_color)
recs = []
for i in range(0, len(colors)):
    recs.append(mpatches.Rectangle((0, 0), 1, 1, fc=colors[i]))

# Map SIze
fig = plt.figure(figsize=(10, 4), dpi=200)

# Construct Map Axis
plt.subplots_adjust(left=0.05,right=0.95,top=0.90,bottom=0.05,wspace=0.15,hspace=0.05)
axs = plt.subplot(111)

# Declare map projection, size and resolution based on script parameters
if sys.argv[1] == 'world':
    plt.title("Live Tweet's World-wide")
    m = Basemap(projection='merc',
                llcrnrlat=-80,
                urcrnrlat=80,
                llcrnrlon=-180,
                urcrnrlon=180,
                lat_ts=20,
                resolution='l',
                ax=axs)
    plt.legend(recs, labels, loc=4)
else:
    plt.title("Live Tweet's in Continental US")
    m = Basemap(llcrnrlon=-119,
                llcrnrlat=19,
                urcrnrlon=-64,
                urcrnrlat=49,
                projection='lcc',
                lat_1=33,
                lat_2=45,
                lon_0=-95,
                resolution='h',
                area_thresh=10000)
    plt.legend(recs, labels)
    m.drawstates(linewidth=0.5, zorder=0.5)

m.drawcoastlines(linewidth=0.5, zorder=0)
m.drawmapboundary(fill_color='aqua')
m.fillcontinents(color='#cc9955', lake_color='aqua', zorder=0)
m.drawcountries(linewidth=0.5, zorder=0.5)
plt.ion()
plt.show()

x_list = []
y_list = []
z_list = []


# Live Stream Twitter Listener
class LiveListener(StreamListener):
    def on_data(self, raw_tweet):
        try:
            tweet = json.loads(raw_tweet)
            tweet_text = tweet['text']
            plot_color = get_plot_color(color_obj, tweet_text)
            if plot_color is not None and tweet['lang'] == 'en':
                if tweet['coordinates'] is not None:
                    x_list.append(tweet['coordinates']['coordinates'][0])
                    y_list.append(tweet['coordinates']['coordinates'][1])
                    z_list.append(plot_color)
                    x, y = m(x_list, y_list)
                    axs.scatter(x, y, marker='.', c=z_list)
                    plt.draw()
                    fig.canvas.draw()
                    return True
                else:
                    if tweet['user']['location'] is not None:
                        if ',' in tweet['user']['location']:
                            geo_location = geolocator.geocode(tweet['user']['location'])
                            if geo_location is not None:
                                geo_shif_val = random.randint(1, 9) / 1000000
                                x_list.append(geo_location.longitude - geo_shif_val)
                                y_list.append(geo_location.latitude - geo_shif_val)
                                z_list.append(plot_color)
                                x, y = m(x_list, y_list)
                                axs.scatter(x, y, marker='.', c=z_list)
                                plt.draw()
                                fig.canvas.draw()
                                return True
        except KeyboardInterrupt:
            print('Exiting Script on User Request...')
            sys.exit(1)

    def on_error(self, status):
        print(status)
        return True


print('Twitter Live Stream Process Running...\n Press control+c at anytime to end the process:')
tweet_live_stream = Stream(auth, LiveListener())
tweet_live_stream.filter(track=hash_list())