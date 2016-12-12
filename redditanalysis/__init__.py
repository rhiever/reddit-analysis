"""
    This is the Reddit Analysis project.

    Copyright 2016 Randal S. Olson.

    This program is free software: you can redistribute it and/or modify it under
    the terms of the GNU General Public License as published by the Free Software
    Foundation, either version 3 of the License, or (at your option) any later
    version.

    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
    details.

    You should have received a copy of the GNU General Public License along with
    this program.  If not, see http://www.gnu.org/licenses/.
"""

import os
import praw
import re
import sys
from bs4 import BeautifulSoup
from collections import defaultdict
from markdown import markdown
from optparse import OptionParser
from requests.exceptions import HTTPError
from update_checker import update_check

__version__ = "1.0.5"

PACKAGE_DIR = os.path.dirname(__file__)

all_words = defaultdict(int)
popular_words = defaultdict(int)
COMMON_WORDS = set()

# load a list of common words to ignore
with open(os.path.join(PACKAGE_DIR, "words", "common-words.txt"), "r") as in_file:
    for line in in_file:
        COMMON_WORDS.add(line.strip().lower())

# Tokens that match this regular expression are immediately discared
# This should be used pretty much to just discard links
URL_RE = re.compile(
    "|".join(["^(http(s)?://|www\.)",  # begins with
              "\.(com|it|net|org)($|/)"  # ends with tld or is followed by /
             ]))

# A valid token regular expression
TOKEN_RE = re.compile(r"[\w]+(?:\'(?:d|ll|m|re|s|t|ve))?", flags=re.UNICODE)


def parse_cmd_line():
    """Command-line argument parsing."""

    usage = ("usage: %prog [options] USERNAME TARGET\n\n"
             "USERNAME sets your Reddit username for the bot\n"
             "TARGET sets the subreddit or user to count word frequencies for."
             "\nenter /r/TARGET for subreddits or /u/TARGET for users.")
    parser = OptionParser(usage=usage)

    parser.add_option("-p", "--period",
                      action="store",
                      type="string",
                      dest="period",
                      default="month",
                      help=("period to count words over:"
                            " day/week/month/year/all"
                            " [default: month]"))

    parser.add_option("-l", "--limit",
                      action="store",
                      type="int",
                      dest="limit",
                      help=("maximum number of submissions/comments to count"
                            " word frequencies for"
                            " [default: no limit]"))

    parser.add_option("-m", "--maxthresh",
                      action="store",
                      type="float",
                      dest="max_threshold",
                      default=0.34,
                      help=("maximum relative frequency in the text a word can"
                            " appear to be considered in word counts (prevents"
                            " word spamming in a single submission)"
                            " [default: 0.34]"))

    parser.add_option("-o", "--only_one",
                      action="store_false",
                      dest="count_word_freqs",
                      default=True,
                      help=("only count a word once per text block (title,"
                            " selftext, comment body) rather than incrementing"
                            " the total for each instance"
                            " [default: false]"))

    parser.add_option("-u", "--multiprocess",
                      action="store_true",
                      default=False,
                      help=("enable PRAW multiprocess support"
                            " [default: false]"))

    parser.add_option("-i", "--include-dictionary",
                      action="store_true",
                      default=False,
                      help=("exclude words found in the dictionary from the"
                            " word cloud"
                            " [default: false]"))

    parser.add_option("-r", "--no-raw-data",
                      action="store_true",
                      default=False,
                      help=("disable raw word count output file"
                            " [default: false]"))

    parser.add_option("-v", "--verbose",
                      action="store_true",
                      default=False,
                      help=("print all program output to the terminal"
                            " [default: false]"))

    options, args = parser.parse_args()

    if len(args) != 2:
        parser.error("Invalid number of arguments provided.")
    user, target = args

    if target.startswith("/r/"):
        options.is_subreddit = True
    elif target.startswith("/u/"):
        options.is_subreddit = False
    else:
        parser.error("Invalid target.")

    if options.period not in ["day", "week", "month", "year", "all"]:
        parser.error("Invalid period.")

    if options.include_dictionary:
        with open(os.path.join(PACKAGE_DIR, "words", "dict-words.txt"), "r") as in_file:
            for line in in_file:
                COMMON_WORDS.add(line.strip().lower())

    return user, target, options


def tokenize(text):
    """Return individual tokens from a block of text."""
    def normalized_tokens(token):
        """Yield lower-case tokens from the given token."""
        for sub in TOKEN_RE.findall(token):
            if sub:
                yield sub.lower()

    for token in text.split():  # first split on whitespace
        if URL_RE.search(token):  # Ignore invalid tokens
            continue
        for sub_token in normalized_tokens(token):
            if sub_token.endswith("'s"):  # Fix possessive form
                sub_token = sub_token[:-2]
            yield sub_token


def parse_text(text, count_word_freqs, max_threshold, is_markdown=True):
    """Parse the passed in text and add words that are not common.

    :param count_word_freqs: if False, only count a word once per text block
        (title, selftext, comment body) rather than incrementing the total for
        each instance.

    :param max_threshold: maximum relative frequency in the text a word can
        appear to be considered in word counts. prevents word spamming in a
        single submission.

    :param is_markdown: When True, parse as markdown and extract the text.

    """

    if is_markdown:
        soup = BeautifulSoup(markdown(text), "lxml")
        text = "".join(soup.findAll(text=True))

    total = 0.0  # intentionally a float
    text_words = defaultdict(int)
    for token in tokenize(text):
        total += 1
        # add to the raw word list
        all_words[token] += 1
        if token not in COMMON_WORDS:
            text_words[token] += 1

    # Count the popular words
    for word, count in text_words.items():
        if count / total <= max_threshold:
            if count_word_freqs:
                popular_words[word] += count
            else:
                popular_words[word] += 1


def with_status(iterable):
    """Wrap an iterable outputting '.' for each item (up to 100 per line)."""
    for i, item in enumerate(iterable):
        sys.stderr.write(".")
        sys.stderr.flush()
        if i % 100 == 99:
            sys.stderr.write("\n")
        yield item

    sys.stderr.write("\n")


def process_redditor(redditor, limit, count_word_freqs, max_threshold):
    """Parse submissions and comments for the given Redditor.

    :param limit: the maximum number of submissions to scrape from the
        subreddit

    :param count_word_freqs: if False, only count a word once per text block
        (title, selftext, comment body) rather than incrementing the total for
        for each instance.

    :param max_threshold: maximum relative frequency in the text a word can
        appear to be considered in word counts. prevents word spamming in a
        single submission.

    """
    for entry in with_status(iterable=redditor.get_overview(limit=limit)):
        if isinstance(entry, praw.objects.Comment):  # Parse comment
            parse_text(text=entry.body, count_word_freqs=count_word_freqs,
                       max_threshold=max_threshold)
        else:  # Parse submission
            process_submission(submission=entry,
                               count_word_freqs=count_word_freqs,
                               max_threshold=max_threshold,
                               include_comments=False)


def process_submission(submission, count_word_freqs, max_threshold, include_comments=True):
    """Parse a submission's text and body (if applicable).

    :param count_word_freqs: if False, only count a word once per text block
        (title, selftext, comment body) rather than incrementing the total for
        for each instance.

    :param max_threshold: maximum relative frequency in the text a word can
        appear to be considered in word counts. prevents word spamming in a
        single submission.

    :param include_comments: include the submission's comments when True

    """
    if include_comments:  # parse all the comments for the submission
        submission.replace_more_comments()
        for comment in praw.helpers.flatten_tree(submission.comments):
            parse_text(text=comment.body, count_word_freqs=count_word_freqs,
                       max_threshold=max_threshold)

    # parse the title of the submission
    parse_text(text=submission.title, count_word_freqs=count_word_freqs,
               max_threshold=max_threshold, is_markdown=False)

    # parse the selftext of the submission (if applicable)
    if submission.is_self:
        parse_text(text=submission.selftext, count_word_freqs=count_word_freqs,
                   max_threshold=max_threshold)


def process_subreddit(subreddit, period, limit, count_word_freqs, max_threshold):
    """Parse comments, title text, and selftext in a given subreddit.

    :param period: the time period to scrape the subreddit over (day, week,
    month, etc.)

    :param limit: the maximum number of submissions to scrape from the
    subreddit

    :param count_word_freqs: if False, only count a word once per text block
        (title, selftext, comment body) rather than incrementing the total for
        for each instance.

    :param max_threshold: maximum relative frequency in the text a word can
        appear to be considered in word counts. prevents word spamming in a
        single submission.

    """

    # determine period to count the words over
    params = {"t": period}
    for submission in with_status(iterable=subreddit.get_top(limit=limit, params=params)):
        try:
            process_submission(submission=submission,
                               count_word_freqs=count_word_freqs,
                               max_threshold=max_threshold)
        except HTTPError as exc:
            sys.stderr.write("\nSkipping submission {0} due to HTTP status {1}"
                             " error. Continuing...\n"
                             .format(submission.permalink.encode("UTF-8"),
                                     exc.response.status_code))
        except ValueError:  # Occurs occasionally with empty responses
            sys.stderr.write("\nSkipping submission {0} due to ValueError.\n"
                             .format(submission.permalink.encode("UTF-8")))


def main():
    # parse the command-line options and arguments
    user, target, options = parse_cmd_line()

    # Check for package updates
    update_check(__name__, __version__)

    # open connection to Reddit
    handler = None

    if options.multiprocess:
        from praw.handlers import MultiprocessHandler
        handler = MultiprocessHandler()

    reddit = praw.Reddit(
        user_agent="/u/{0} reddit analyzer".format(user), handler=handler)

    reddit.config.decode_html_entities = True

    # run analysis
    sys.stderr.write("Analyzing {0}\n".format(target))
    sys.stderr.flush()

    target = target[3:]

    if options.is_subreddit:
        process_subreddit(subreddit=reddit.get_subreddit(target),
                          period=options.period, limit=options.limit,
                          count_word_freqs=options.count_word_freqs,
                          max_threshold=options.max_threshold)
    else:
        process_redditor(redditor=reddit.get_redditor(target), limit=options.limit,
                         count_word_freqs=options.count_word_freqs,
                         max_threshold=options.max_threshold)

    # build a string containing all the words for the word cloud software
    output = ""

    # open output file to store the output string
    out_file_name = "{0}.csv".format(target)

    if options.is_subreddit:
        out_file_name = "subreddit-{0}".format(out_file_name)
    else:
        out_file_name = "user-{0}".format(out_file_name)

    out_file = open(out_file_name, "w")

    # combine singular and plural forms of words into single count
    for word in list(popular_words.keys()):
        count = popular_words[word]

        # e.g.: "picture" and "pictures"
        if word.endswith("s"):
            # if the singular form of the word was used
            singular = word[:-1]
            if popular_words[singular] > 0:

                # combine the count into the most-used form of the word
                if popular_words[singular] > count:
                    popular_words[singular] += popular_words[word]
                    del popular_words[word]
                else:
                    popular_words[word] += popular_words[singular]
                    del popular_words[singular]

        # e.g.: "furry" and "furries"
        if word.endswith("ies"):
            # if the singular form of the word was used
            singular = "{0}y".format(word[:-3])
            if popular_words[singular] > 0:
                # combine the count into the most-used form of the word
                if popular_words[singular] > count:
                    popular_words[singular] += popular_words[word]
                    del popular_words[word]
                else:
                    popular_words[word] += popular_words[singular]
                    del popular_words[singular]

    for word in sorted(popular_words, key=popular_words.get, reverse=True):
        # tweak this number depending on the subreddit
        # some subreddits end up having TONS of words and it seems to overflow
        # the Python string buffer
        if popular_words[word] > 5:
            pri = True

            # don't print the word if it's just a number
            if word.isdigit():
                pri = False

            # add as many copies of the word as it was mentioned in the
            # subreddit
            if pri:
                out_text = str("{0}:{1}\n".format(word.encode('utf-8'), popular_words[word]))
                output += out_text
                out_file.write(out_text)

    out_file.close()

    # print the series of words for the word cloud software
    # place this text into wordle.net
    if options.verbose:
        print(output)

    # save the raw word counts to a file
    if not options.no_raw_data:
        out_file = open("raw-{0}".format(out_file_name), "w")
        for word in sorted(all_words, key=all_words.get, reverse=True):
            out_text = str("{0}:{1}\n".format(word.encode('utf-8'), all_words[word]))
            out_file.write(out_text)
        out_file.close()


if __name__ == "__main__":
    sys.exit(main())
