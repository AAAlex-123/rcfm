import json
import praw
import prawcore

def read_json(filename):
    with open(filename, 'r') as f:
        loaded_json = json.load(f)

    return loaded_json

# TODO: split main to different functions, one for each command
# e.g. list/create/delete/add/...
def main(feeds_filename, **kwargs):

    # TODO: maybe dataclass or something for kwargs
    reddit = praw.Reddit(**kwargs)

    # TODO: exception/error handling for file
    feeds = read_json(feeds_filename)

    for multireddit_name, subreddit_list in feeds.items():

        multireddit = reddit.multireddit(
            redditor=kwargs["username"],
            name=multireddit_name
        )

        # check if multireddit exists or not
        try:
            multireddit.display_name

        except prawcore.exceptions.NotFound as e:
            # 404 -> multireddit does not exist -> create and add

            multireddit.new()
            print(f"Created feed {multireddit.display_name}.")

            for subreddit_name in subreddit_list:
                subreddit = reddit.subreddit(subreddit_name)

                multireddit.add(subreddit)

                print(f"Added {subreddit.display_name} to feed {multireddit.display_name}.")

        else:
            # no 404 -> multireddit exists -> merge existing and file
            print(f"Feed {multireddit.display_name} already exists.")

if __name__ == "__main__":
    # TODO: remove hardcoded stuff and do some argparse instead
    secret_file = "./secret/reddit_secrets.json"
    feeds_file = "./feed_data/0feeds0.json"
    secret = read_json(secret_file)
    main(feeds_file, **secret)
