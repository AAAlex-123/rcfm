import argparse
import json
import praw
import prawcore

def read_json(filename):
    with open(filename, 'r') as f:
        loaded_json = json.load(f)

    return loaded_json

# TODO: split main to different functions, one for each command
# e.g. show/create/delete/add/...
def prototype_main(feeds_filename, **kwargs):

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

def _main_show(reddit, verbose, feeds):
    print(f"Calling _main_show() with {reddit=}, {verbose=} and {feeds=}")

    all_multireddits = reddit.user.multireddits()
    multireddit_names = [m.name for m in all_multireddits if m.name in feeds]
    multireddits = [m for m in all_multireddits if m.name in multireddit_names]
    missing_names = [f for f in feeds if f not in multireddit_names]

    string = "'SHOW' STRING NOT SET TO ANYTHING"

    if verbose == 0:
        string = ', '.join(m.display_name for m in multireddits)

    elif verbose == 1:
        string = ""
        for m in multireddits:
            string += f"{m.display_name} ({len(m.subreddits)} subreddits), "

        string = string[:-2]

    elif verbose == 2:
        string = ""
        for m in multireddits:
            subs = m.subreddits
            string += f"{m.display_name} ({len(subs)} subreddits): "
            string += f"{', '.join([sub.display_name for sub in subs])} \n"

        string = string[:-2]

    elif verbose == 3:
        string = ""
        for i, m in enumerate(multireddits):
            subs = m.subreddits
            string += f"""{f" {i+1}: {m.display_name} ({len(subs)} subreddits) ":-^80}\n"""
            for j, subreddit in enumerate(subs):
                string += f"--- {i+1}.{j+1}: {subreddit.display_name} ---\n{subreddit.description}\n\n"

            string += "\n"

    else:
        raise ValueError(f"Unrecognized verbose level: {verbose}")

    username = reddit.user.me().name
    multireddit_count = len(multireddits)
    missing_count = len(missing_names)

    if multireddit_count > 0:
        print(f"Found {multireddit_count} feeds for user '{username}':")
        print(string)

    if missing_count > 0:
        print(f"""The following {"feed doesn't" if missing_count == 1 else f"{missing_count} feeds don't"} exist for user '{username}': {', '.join(missing_names)}""")

def _main_create(reddit, feeds):
    print(f"Calling _main_create() with {reddit=}, {feeds=}")

    existing_feed_names = []

    for display_name in feeds:
        # TODO: error checking for invalid name
        m = reddit.multireddit.create(subreddits=[], display_name=display_name)

        expected_name = display_name.lower().replace(' ', '_')
        actual_name = m.name

        if expected_name != actual_name:
            m.delete()
            existing_feed_names.append(display_name)

    created_feed_names = [f for f in feeds if f not in existing_feed_names]
    created_count = len(created_feed_names)
    if created_count > 0:
        s = 's' if created_count > 1 else ''
        print(f"Created {created_count} feed{s}: {', '.join(created_feed_names)}")

    existing_count = len(existing_feed_names)
    if existing_count > 0:
        s, nots = ('s', '') if existing_count > 1 else ('', 's')
        print(f"The following {existing_count} feed{s} already exist{nots}: {', '.join(existing_feed_names)}")

def main():
    commands = {
        "show": _main_show,
        "create": _main_create,
    }

    parser = argparse.ArgumentParser(description="Show existing feeds (wip). More commands to come!")
    parser.add_argument("auth", help="path to the file which contains authorization data. The file should be in JSON format, containing a single object with the following five keys: client_id, client_secret, user_agent, username and password. The file should be similar to ./reddit_secrets-example.json.")
    subparsers = parser.add_subparsers(title="subcommands", required=True, help="the command to execute")

    curr_command = "show"
    parser_show = subparsers.add_parser(curr_command, help="show existing feeds", formatter_class=argparse.RawTextHelpFormatter)
    parser_show.add_argument("-v", "--verbose", default=2, type=int, choices=[i for i in range(0, 4)], help="how much information to show about each feed (default = %(default)s).\n"
    "    0: just the name\n"
    "    1: name and subreddit count\n"
    "    2: name, subreddit count and names of subreddits\n"
    "    3: name, subreddit count and names and descriptions of subreddits")
    parser_show.add_argument("feeds", nargs="*", help="which feeds to show; defaults to all")
    # TODO: more options like sorting alphabetically, by creation date, by subreddit count etc
    parser_show.set_defaults(func=commands[curr_command])

    curr_command = "create"
    parser_create = subparsers.add_parser(curr_command, help="create a new feed")
    parser_create.add_argument("feeds", nargs='+', help="the names of the feeds to create")
    # TODO: more options like verbose output etc
    parser_create.set_defaults(func=commands[curr_command])

    # TODO: fix what happens on error (https://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argu#answer-47440202)
    args = parser.parse_args()
    args_dict = vars(args)

    # TODO: error checking
    auth_file = args_dict.pop("auth")
    reddit_auth = read_json(auth_file)
    reddit = praw.Reddit(**reddit_auth)

    func = args_dict.pop("func")
    func(reddit, **args_dict)

if __name__ == "__main__":
    main()
