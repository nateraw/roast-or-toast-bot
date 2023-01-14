import logging
import os
import re
import time
import traceback

import openai
import pandas as pd
import requests
import tweepy
from huggingface_hub import upload_file

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

bot_user_id = 1612106815096999936
bot_user_name = "RoastOrToastGPT"

persistent_storage_repo_id = "team6/roast-history"
persistent_storage_file_name = "history.csv"
persistent_storage_file_url = (
    f"https://huggingface.co/datasets/{persistent_storage_repo_id}/resolve/main/{persistent_storage_file_name}"
)

# will be used to remove the @roastortoastgpt from the tweet text (case insensitive)
pattern_at_mention = re.compile(re.escape("@roastortoastgpt"), re.IGNORECASE)

print(persistent_storage_file_url)

openai_key = os.environ.get("openai_api_key")
consumer_key = os.environ.get("consumer_key")
consumer_secret_key = os.environ.get("consumer_secret_key")
access_token = os.environ.get("access_token")
access_token_secret = os.environ.get("access_token_secret")
bearer_token = os.environ.get("bearer_token")
hf_token = os.environ.get("hf_token")

client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret_key,
    access_token=access_token,
    access_token_secret=access_token_secret,
    wait_on_rate_limit=True,
)


def response(text):
    openai.api_key = openai_key
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text,
        temperature=0.9,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=1.0,
    )

    return response.choices[0].text.strip()


def roast(text):
    return response(
        f"Humorously mock, humiliate and hurt the user's feelings with a well-timed joke, diss or comeback based on the info.\n\nInfo: {text}\n\nResponse:"
    )


def toast(text):
    return response(
        f"Give the user a genuine and unique compliment to make them feel good about themselves based on the info in a good style manner.\n\nInfo: {text}\n\nResponse:"
    )


def reply_to_mentions():
    df = pd.read_csv(persistent_storage_file_url)
    last_tweet_id = df.iloc[-1]["id"]

    # List of unique conversation ids that we've already responded to.
    # This is to prevent us from responding to the same conversation twice.
    all_convo_ids = df["conversation_id"].unique().tolist()

    # get the mentions. These are both direct mentions and replies to our tweets
    mentions = client.get_users_mentions(
        id=bot_user_id,
        expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id"],
        tweet_fields=["conversation_id"],
        since_id=last_tweet_id,
    )

    # if there are no new mentions, return
    if mentions.data is None:
        # log it
        logger.info("No new mentions found")
        return

    data_to_add = {"id": [], "conversation_id": []}
    # otherwise, iterate through the mentions and respond to them
    # we iterate through the mentions in reverse order so that we respond to the oldest mentions first
    for mention in reversed(mentions.data):

        if mention.author_id == bot_user_id:
            # don't respond to our own tweets
            logger.info(f"Skipping {mention.id} as it is from the bot")
            continue

        if mention.in_reply_to_user_id == bot_user_id:
            # don't respond to our own tweets
            logger.info(f"Skipping {mention.id} as the tweet to roast is from the bot")
            continue

        if not mention.referenced_tweets:
            logger.info(f"Skipping {mention.id} as it is not a reply")
            continue

        # if we've already responded to this conversation, skip it
        # also should catch the case where we've already responded to this tweet (though that shouldn't happen)
        if mention.conversation_id in all_convo_ids:
            logger.info(f"Skipping {mention.id} as we've already responded to this conversation")
            continue

        logger.info(f"Responding to {mention.id}, which said {mention.text}")

        tweet_to_roast_id = mention.referenced_tweets[0].id
        tweet_to_roast = client.get_tweet(tweet_to_roast_id)
        text_to_roast = tweet_to_roast.data.text

        mention_text = mention.text
        mention_text = pattern_at_mention.sub("", mention_text)
        logger.info(f"Mention Text: {mention_text}")

        if "roast" in mention_text.lower():
            logger.info(f"Roasting {mention.id}")
            text_out = roast(text_to_roast)
        elif "toast" in mention_text.lower():
            logger.info(f"Toasting {mention.id}")
            text_out = toast(text_to_roast)
        else:
            logger.info(f"Skipping {mention.id} as it is not a roast or toast")
            continue

        # Quote tweet the tweet to roast
        logger.info(f"Quote tweeting {tweet_to_roast_id} with response: {text_out}")
        quote_tweet_response = client.create_tweet(
            text=text_out,
            quote_tweet_id=tweet_to_roast_id,
        )
        print("QUOTE TWEET RESPONSE", quote_tweet_response.data)
        response_quote_tweet_id = quote_tweet_response.data.get("id")
        logger.info(f"Response Quote Tweet ID: {response_quote_tweet_id}")
        response_quote_tweet_url = f"https://twitter.com/{bot_user_name}/status/{response_quote_tweet_id}"
        logger.info(f"Response Quote Tweet URL: {response_quote_tweet_url}")

        # reply to the mention with the link to the response tweet
        logger.info(f"Responding to: {mention.id}")
        response_reply = client.create_tweet(
            text=f"Here's my response: {response_quote_tweet_url}",
            in_reply_to_tweet_id=mention.id,
        )
        response_reply_id = response_reply.data.get("id")
        logger.info(f"Response Reply ID: {response_reply_id}")

        # add the mention to the history
        data_to_add["id"].append(mention.id)
        data_to_add["conversation_id"].append(mention.conversation_id)

        # add a line break to the log
        logger.info("-" * 100)

    # update the history df and upload it to the persistent storage repo
    if len(data_to_add["id"]) == 0:
        logger.info("No new mentions to add to the history")
        return

    logger.info(f"Adding {len(data_to_add['id'])} new mentions to the history")

    df_to_add = pd.DataFrame(data_to_add)
    df = pd.concat([df, df_to_add], ignore_index=True)
    df.to_csv(persistent_storage_file_name, index=False)
    upload_file(
        repo_id=persistent_storage_repo_id,
        path_or_fileobj=persistent_storage_file_name,
        path_in_repo=persistent_storage_file_name,
        repo_type="dataset",
        token=hf_token,
    )


def main():
    logger.info("Starting up...")

    while True:
        try:
            # Dummy request to keep the Hugging Face Space awake
            # Not really working as far as I can tell
            # logger.info("Pinging Hugging Face Space...")
            # requests.get("https://team6-roast.hf.space/", timeout=5)
            logger.info("Replying to mentions...")
            reply_to_mentions()
        except Exception as e:
            logger.error(e)
            traceback.print_exc()

        logger.info("Sleeping for 30 seconds...")
        time.sleep(30)


if __name__ == "__main__":
    main()
