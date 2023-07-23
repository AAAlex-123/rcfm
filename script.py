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

def _main_show(verbose, feeds):
    print(f"Calling _main_show() with {verbose=} and {feeds=}")

def main():

    commands = {
        "show": _main_show,
    }

    parser = argparse.ArgumentParser(description="Show existing feeds (wip). More commands to come!")
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

    # TODO: fix what happens on error (https://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argu#answer-47440202)
    args = parser.parse_args()
    args_dict = vars(args)

    func = args_dict.pop("func")
    func(**args_dict)

if __name__ == "__main__":
    main()
