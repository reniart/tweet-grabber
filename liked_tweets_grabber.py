#code sampled from TwitterDev github

import requests
import os
import json

# setting twitterDev project token
bearer_token = os.environ.get("BEARER_TOKEN")

def create_url():
    # additional fields include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    tweet_fields = "tweet.fields=lang,author_id,created_at,geo"
    # additional ids can be added with comma spacing
    id = "2973885323"

    url = "https://api.twitter.com/2/users/{}/liked_tweets".format(id)
    return url, tweet_fields

def bearer_ouath(request):
    # twitterDev project authentication
    request.headers["Authorization"] = f"Bearer {bearer_token}"
    request.headers["User-Agent"] = "liked_twt_grabber"
    return request

def connect_endpoint(url, tweet_fields):
    response = requests.request(
        "GET", url, auth=bearer_ouath, params=tweet_fields)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def main():
    url, tweet_fields = create_url()
    json_response = connect_endpoint(url, tweet_fields)

    grabbed_tweets = open("liked_tweets.txt", 'w')    
    grabbed_tweets.write(str(json.dumps(json_response, indent=4, sort_keys=True)))
    grabbed_tweets.close()

if __name__ == "__main__":
    main()

