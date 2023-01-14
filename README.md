# roast-or-toast-bot

A fun (yet toxic) twitter bot that uses GPT-3 to either roast 😈 or toast 🥂 a tweet if you mention it in the replies

<img width="587" alt="Screen Shot 2023-01-14 at 1 19 19 AM" src="https://user-images.githubusercontent.com/32437151/212440593-330efca7-1e88-46c8-a04b-c92aa70a9807.png">

## Disclaimer

By using artificial intelligence (AI) to gently tease others, you acknowledge that you are solely responsible for any consequences that may arise from your acts.

This bot may (no, will) tweet unpredictable, toxic, and/or nonsensical content.

## How to Use

Tag [@RoastOrToastGPT](https://twitter.com/RoastOrToastGPT) in a reply to a tweet and include one of the keywords "toast" or "roast". It will respond with something nice if you said "toast", and something not so nice if you say "roast". If you include both words, it's gunna roast ya.

## How it Works

- Uses [`tweepy`](https://docs.tweepy.org/en/stable/) to connect to Twitter APIv2.
- Uses `openai` GPT-3 and some hacky prompting to get either a toast or a roast, depending on what a user asked for when they mentioned it in a reply (literally `if 'roast' in text` then `elif 'toast' in text`).
  - TODO: use open model so we don't go broke
- Automatically pushed and hosted on @huggingface [spaces](https://hf.co/spaces) using Docker (thanks to [this GitHub action](https://github.com/nateraw/huggingface-sync-action))
  - This bit is slightly broken right now, as spaces is expecting the app to have some hosted web app component talking on a port. Have to restart it manually from time to time
- Uses @huggingface [datasets](https://hf.co/datasets) repo for persistent storage of the tweet history so it doesn't keep replying to the same tweet/conversation.
  - If a bunch of people start using this bot, this solution will not scale so nice 😅 but we'll cross that bridge when we come to it.

## TODO

- [ ] Make prompts more consistent so we don't get so much nonsense/simply repeated tweets
- [ ] Fix hosting (preferably on Spaces) so I don't have to reset it every 30 mins manually

## Contributors

This project was mostly hacked together in ~3 hours during the Hugging Face 2023 offsite Hackathon by the following team:

- Thibault Goehringer
- Derek Thomas
- Lysandre Debut
- Scott Edelstein
- Ola Piktus
- Michelle Habonneau
- Thomas Wolf
- Nate Raw
