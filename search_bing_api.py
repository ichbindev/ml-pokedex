# import the necessary packages
from requests import exceptions
import argparse
import requests
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True,
                help="search query to search Bing Image API for")
ap.add_argument("-o", "--output", required=True,
                help="path to output directory of images")
args = vars(ap.parse_args())

# bing api key
API_KEY = os.getenv('API_KEY')

# number of results and page size
MAX_RESULTS = 400
GROUP_SIZE = 50

# set the endpoint API URL
URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

# exceptions that may be encountered
EXCEPTIONS = set([IOError, FileNotFoundError,
                  exceptions.RequestException, exceptions.HTTPError,
                  exceptions.ConnectionError, exceptions.Timeout])

# search for query in script param
term = args["query"]
headers = {"Ocp-Apim-Subscription-Key": API_KEY}
params = {"q": term, "offset": 0, "count": GROUP_SIZE}

# start the search
print("[INFO] searching Bing API for '{}'".format(term))
search = requests.get(URL, headers=headers, params=params)
search.raise_for_status()

# grab the results from the search, including the total number of
# estimated results returned by the Bing API
results = search.json()
estNumResults = min(results["totalEstimatedMatches"], MAX_RESULTS)
print("[INFO] {} total results for '{}'".format(estNumResults, term))

# number of images downloaded
total = 0

# loop over the estimated number of results in `GROUP_SIZE` pages
for offset in range(0, estNumResults, GROUP_SIZE):
    # update the search parameters using the current offset, then
    # make the request to fetch the results
    print("[INFO] making request for group {}-{} of {}...".format(
        offset, offset + GROUP_SIZE, estNumResults))
    params["offset"] = offset
    search = requests.get(URL, headers=headers, params=params)
    search.raise_for_status()
    results = search.json()
    print("[INFO] saving images for group {}-{} of {}...".format(
        offset, offset + GROUP_SIZE, estNumResults))

# loop over the results
for v in results["value"]:
    # try to download the image
    try:
        # make a request to download the image
        print("[INFO] fetching: {}".format(v["contentUrl"]))
        r = requests.get(v["contentUrl"], timeout=30)
        # build the path to the output image
        ext = v["contentUrl"][v["contentUrl"].rfind("."):]
        p = os.path.sep.join([args["output"], "{}{}".format(
            str(total).zfill(8), ext)])
        # write the image to disk
        f = open(p, "wb")
        f.write(r.content)
        f.close()
    # catch any errors
    except Exception as e:
        # continue if it's an expected exception
        if type(e) in EXCEPTIONS:
            print("[INFO] skipping: {}".format(v["contentUrl"]))
            continue

    # try to load the image from disk
    image = cv2.imread(p)
    # ignore it if it is None
    if image is None:
        print("[INFO] deleting: {}".format(p))
        os.remove(p)
        continue
    # update the counter
    total += 1