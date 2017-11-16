# twitter_analytics
A collections of python scripts used to analyze Tweet Data
Built and Tested in Python3.x

# Installation
```R
git clone https://github.com/JECSand/twitter_analytics.git
```

## How to use
* Update the config.py file with your twitter credentials and dictionary of companies/products/etc and keywords you wish to collect tweets for.

1) Live Map
* Simple Run the following command
```R
python3 twitter_live_geomap.py
```
Enter control+c to end process

2) Batch Map
* Run Batch Extractor script first
```R
python3 twitter_extraction_batcher.py
```
* Then execute the batch map, which will push you to a map on your web broswer containing all of the pulled tweets that contained geodata.
```R
python3 twitter_batched_geomap.py
```

## Coming Soon!!
* Updated Readme with screen screen-shots
* Sentiment Analysis Script
