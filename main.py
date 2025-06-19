import asyncio
import json
import re
from twikit import Client
import sys
import os

OUTPUT_FILE = "tweets.json"
PAGE_FETCH_DELAY = 3
MAX_TWEETS = 100
TWEETS_PER_PAGE = 20

async def run_main(cookie_path):
    print(f"[main.py] Loading cookies from: {cookie_path}")
    client = Client()
    client.load_cookies(path=cookie_path)

    tweet_data = []
    tweets = await client.get_timeline(count=TWEETS_PER_PAGE)

    while tweets and len(tweet_data) < MAX_TWEETS:
        for tweet in tweets:
            user = tweet.user
            media_urls = []

            # Handle media
            if tweet.media:
                for media in tweet.media:
                    if media.type == "photo":
                        url = getattr(media, "media_url_https", None) or getattr(media, "media_url", None)
                        if url:
                            media_urls.append(url)
                    elif media.type in ("video", "animated_gif") and hasattr(media, "streams"):
                        streams = media.streams or []
                        if streams:
                            best = streams[-1]
                            if best.url:
                                media_urls.append(best.url)

            profile_image_url = getattr(user, "profile_image_url_https", None) or getattr(user, "profile_image_url", None)
            cleaned_text = re.sub(r"https://t\.co/\w+", "", tweet.full_text).strip()

            tweet_data.append({
                 "username": tweet.user.screen_name,
                 "name": tweet.user.name,
                 "verified": tweet.user.is_blue_verified,
                 "profile_image_url": profile_image_url,
                 "text": cleaned_text,
                 "tweet_id": getattr(tweet, "id", None),
                 "created_at": str(tweet.created_at),
                 "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                 "media": media_urls,
                 "like_count": getattr(tweet, "favorite_count", 0),
                 "retweet_count": getattr(tweet, "retweet_count", 0),
                 "reply_count": getattr(tweet, "reply_count", 0),
                 "views": getattr(tweet, "view_count", 0)
            })

            if len(tweet_data) >= MAX_TWEETS:
                break

        if len(tweet_data) >= MAX_TWEETS:
            break

        await asyncio.sleep(PAGE_FETCH_DELAY)
        tweets = await tweets.next()

    # Save to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(tweet_data, f, ensure_ascii=False, indent=2)

    print(f"[main.py] ✅ tweets.json saved at: {os.path.abspath(OUTPUT_FILE)}")
    print(f"[main.py] ✅ Saved {len(tweet_data)} tweets to {OUTPUT_FILE}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[main.py] ERROR: Usage: python3 main.py <cookie.json path>")
        sys.exit(1)

    cookie_path = sys.argv[1]
    asyncio.run(run_main(cookie_path))
