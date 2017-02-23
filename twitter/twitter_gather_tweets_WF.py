# Social Media Data Collection (Python)

import twitter  # work with Twitter APIs
import json  # methods for working with JSON data
import yaml  # import config for API keys
from pandas.io.json import json_normalize
import time # so we can add timestamps to files

q = "Wells Fargo"  # string to search
q_file = "WF"

t = time.localtime()
timestamp = time.strftime('%Y%m%d_%H%M%S', t)

# want to keep API keys out of code for security
# YAML file should have the following:
# twitter_api:
#    CONSUMER_KEY: xxxx
#    CONSUMER_SECRET: xxxx
#    OAUTH_TOKEN: xxxx
#    OAUTH_TOKEN_SECRET: xxxx

# load the YAML file with the twitter API details
with open("../../Secrets/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

windows_system = False  # set to True if this is a Windows computer
if windows_system:
    line_termination = '\r\n'  # Windows line termination
else:
    line_termination = '\n'  # Unix/Linus/Mac line termination

# name used for JSON file storage        
json_filename = '../../Output-' + q_file + '/tweet_file-' + timestamp + '.json'

# name used for CSV file storage
# CSV useful for analysis with ConText
csv_filename = '../../Output-' + q_file + '/tweet_file-' + timestamp + '.csv'

# name for text file for review of results
full_text_filename = '../../Output-' + q_file + '/tweet_full_text_file-' + timestamp + '.txt'

# name for text from tweets
partial_text_filename = '../../Output-' + q_file + '/tweet_partial_text_file-' + timestamp + '.txt'


# See Russell (2014) and Twitter site for documentation
# https://dev.twitter.com/rest/public
# Go to http://twitter.com/apps/new to provide an application name
# to Twitter and to obtain OAuth credentials to obtain API data

# -------------------------------------
# Twitter authorization a la Russell (2014) section 9.1
# Insert credentials in place of the "blah blah blah" strings 
# Sample usage of oauth() function
# twitter_api = oauth_login()    
def oauth_login():
    CONSUMER_KEY = cfg['twitter_api']['CONSUMER_KEY']
    CONSUMER_SECRET = cfg['twitter_api']['CONSUMER_SECRET']
    OAUTH_TOKEN = cfg['twitter_api']['OAUTH_TOKEN']
    OAUTH_TOKEN_SECRET = cfg['twitter_api']['OAUTH_TOKEN_SECRET']

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


# -------------------------------------
# searching the REST API a la Russell (2014) section 9.4
def twitter_search(twitter_api, q, max_results=200, **kw):
    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets and 
    # https://dev.twitter.com/docs/using-search for details on advanced 
    # search criteria that may be useful for keyword arguments

    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets    
    search_results = twitter_api.search.tweets(q=q, count=100, **kw)

    statuses = search_results['statuses']

    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. See
    # https://dev.twitter.com/docs/rate-limiting/1.1/limits
    # for details. A reasonable number of results is ~1000, although
    # that number of results may not exist for all queries.

    # Enforce a reasonable limit
    max_results = min(1000, max_results)

    for _ in range(10):  # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError as e:  # No more results when next_results doesn't exist
            break

        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([kv.split('=')
                       for kv in next_results[1:].split("&")])

        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']

        if len(statuses) > max_results:
            break

    return statuses


# -------------------------------------
# use the predefined functions from Russell to conduct the search
# this is the Ford Is Quality Job One example

twitter_api = oauth_login()
print(twitter_api)  # verify the connection

results = twitter_search(twitter_api, q, max_results=200)  # limit to 200 tweets

# examping the results object... should be list of dictionary objects
print('\n\ntype of results:', type(results))
print('\nnumber of results:', len(results))
print('\ntype of results elements:', type(results[0]))

# -------------------------------------
# working with JSON files composed of multiple JSON objects
# results is a list of dictionary items obtained from twitter
# these functions assume that each dictionary item
# is written as a JSON object on a separate line
item_count = 0  # initialize count of objects dumped to file
with open(json_filename, 'w') as outfile:
    for dict_item in results:
        json.dumps(dict_item, outfile).encode('utf-8')
        item_count += 1
        if item_count < len(results):
            outfile.write(line_termination)  # new line between items

# -------------------------------------
# working with text file for reviewing multiple JSON objects
# this text file will show the full contents of each tweet
# results is a list of dictionary items obtained from twitter
# these functions assume that each dictionary item
# is written as group of lines printed with indentation
item_count = 0  # initialize count of objects dumped to file
with open(full_text_filename, 'w') as outfile:
    for dict_item in results:
        outfile.write('Item index: ' + str(item_count) +
                      ' -----------------------------------------' +
                      line_termination)
        # indent for pretty printing
        outfile.write(json.dumps(dict_item, indent=4))
        item_count += 1
        if item_count < len(results):
            outfile.write(line_termination)  # new line between items

# -------------------------------------
# working with text file for reviewing text from multiple JSON objects
# this text file will show only the text from each tweet
# results is a list of dictionary items obtained from twitter
# these functions assume that the text of each tweet 
# is written to a separate line in the output text file
item_count = 0  # initialize count of objects dumped to file
with open(partial_text_filename, 'w') as outfile:
    for dict_item in results:
        outfile.write(json.dumps(dict_item['text']))
        item_count += 1
        if item_count < len(results):
            outfile.write(line_termination)  # new line between text items

# use json_normalize to get results into a pandas DataFrame
df = json_normalize(results)
df.to_csv(csv_filename)