# This is the Reddit Analysis project.
#
# Copyright 2013 Randal S. Olson.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.

import os
import praw
import string
import sys
from BeautifulSoup import BeautifulSoup
from collections import defaultdict
from markdown import markdown
from optparse import OptionParser
from requests.exceptions import HTTPError
from update_checker import update_check

__version__ = '0.1'

PACKAGE_DIR = os.path.dirname(__file__)

popularWords = defaultdict(int)
commonWords = set()

# punctuation to strip from words
punctuation = " " + string.punctuation + "\n"



# load a list of common words to ignore
for line in open(os.path.join(PACKAGE_DIR, "words", "common-words.txt"), "r"):
    commonWords.add(line.strip(punctuation).lower())

# put words here that you don't want to include in the word cloud
excludedWords = ["/", "--", "...", "deleted", ")x"]


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
                      help=("period to count words over: "
                            "day/week/month/year/all"
                            " [default: month]"))

    parser.add_option("-l", "--limit",
                      action="store",
                      type="int",
                      dest="limit",
                      help=("maximum number of submissions/comments to count "
                            "word frequencies for"
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
                      help=("only count a word once per text block (title, "
                            "selftext, comment body) rather than incrementing"
                            "the total for for each instance"
                            " [default: false]"))

    parser.add_option("-i", "--include-dictionary",
                      action="store_true",
                      default=False,
                      help=("exclude words found in the dictionary from the"
                            " word cloud"
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
        for line in open(os.path.join(PACKAGE_DIR, "words", "dict-words.txt"),
                         "r"):
            commonWords.add(line.strip(punctuation).lower())
    
    return user, target, options


def parseText(text, count_word_freqs, max_threshold, is_markdown=True):
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
        soup = BeautifulSoup(markdown(text),
                             convertEntities=BeautifulSoup.HTML_ENTITIES)
        text = ''.join(soup.findAll(text=True))

    total = 0.0  # intentionally a float
    text_words = defaultdict(int)
    for word in text.split():  # Split on all whitespace
        word = word.strip(punctuation).lower()
        total += 1
        if word and word not in commonWords:
            text_words[word] += 1

    # Add to popularWords list
    for word, count in text_words.items():
        if count / total <= max_threshold:
            if count_word_freqs:
                popularWords[word] += count
            else:
                popularWords[word] += 1


def processRedditor(redditor, limit, count_word_freqs, max_threshold):
    """Parse submissions and comments for the given Redditor.
        
    :param limit: the maximum number of submissions to scrape from the subreddit
        
    :param count_word_freqs: if False, only count a word once per text block
        (title, selftext, comment body) rather than incrementing the total for for each instance.
    
    :param max_threshold: maximum relative frequency in the text a word can
        appear to be considered in word counts. prevents word spamming in a single submission.
        
    """
    for entry in with_status(iterable=redditor.get_overview(limit=limit)):
        if isinstance(entry, praw.objects.Comment):  # Parse comment
            parseText(text=entry.body, count_word_freqs=count_word_freqs,
                      max_threshold=max_threshold)
        else:  # Parse submission
            processSubmission(submission=entry, count_word_freqs=count_word_freqs,
                              max_threshold=max_threshold, include_comments=False)


def processSubmission(submission, count_word_freqs, max_threshold, include_comments=True):
    """Parse a submission's text and body (if applicable).

    :param count_word_freqs: if False, only count a word once per text block (title,
        selftext, comment body) rather than incrementing the total for for each instance.
    
    :param max_threshold: maximum relative frequency in the text a word can
        appear to be considered in word counts. prevents word spamming in a single submission.
    
    :param include_comments: include the submission's comments when True

    """
    if include_comments:  # parse all the comments for the submission
        submission.replace_more_comments()
        for comment in praw.helpers.flatten_tree(submission.comments):
            parseText(text=comment.body, count_word_freqs=count_word_freqs,
                      max_threshold=max_threshold)

    # parse the title of the submission
    parseText(text=submission.title, count_word_freqs=count_word_freqs,
              max_threshold=max_threshold, is_markdown=False)

    # parse the selftext of the submission (if applicable)
    if submission.is_self:
        parseText(text=submission.selftext, count_word_freqs=count_word_freqs,
                  max_threshold=max_threshold)


def processSubreddit(subreddit, period, limit, count_word_freqs, max_threshold):
    """Parse comments, title text, and selftext in a given subreddit.
    
    :param period: the time period to scrape the subreddit over (day, week, month, etc.)
    
    :param limit: the maximum number of submissions to scrape from the subreddit
    
    :param count_word_freqs: if False, only count a word once per text block
        (title, selftext, comment body) rather than incrementing the total for for each instance.
    
    :param max_threshold: maximum relative frequency in the text a word can
        appear to be considered in word counts. prevents word spamming in a single submission.
    
    """

    # determine period to count the words over
    params = {'t': period}
    for submission in with_status(iterable=subreddit.get_top(limit=limit, params=params)):
        try:
            processSubmission(submission=submission, count_word_freqs=count_word_freqs,
                              max_threshold=max_threshold)
        except HTTPError as exc:
            sys.stderr.write("\nSkipping submission {0} due to HTTP status {1}"
                             " error. Continuing...\n"
                             .format(submission.url, exc.response.status_code))
        except ValueError:  # Occurs occasionally with empty responses
            sys.stderr.write("\nSkipping submission {0} due to ValueError.\n"
                             .format(submission.url))


def with_status(iterable):
    """Wrap an iterable outputting '.' for each item (up to 100 per line)."""
    for i, item in enumerate(iterable):
        sys.stderr.write('.')
        sys.stderr.flush()
        if i % 100 == 99:
            sys.stderr.write('\n')
        yield item
    
    sys.stderr.write('\n')

def main():
    # parse the command-line options and arguments
    user, target, options = parse_cmd_line()

    # Check for package updates
    update_check(__name__, __version__)

    # open connection to Reddit
    r = praw.Reddit(user_agent="bot by /u/{0}".format(user),
                    disable_update_check=True)
    r.config.decode_html_entities = True

    # run analysis
    sys.stderr.write("Analyzing {0}\n".format(target))
    sys.stderr.flush()

    target = target[3:]

    if options.is_subreddit:
        processSubreddit(subreddit=r.get_subreddit(target), period=options.period,
                         limit=options.limit, count_word_freqs=options.count_word_freqs,
                         max_threshold=options.max_threshold)
    else:
        processRedditor(redditor=r.get_redditor(target), limit=options.limit,
                        count_word_freqs=options.count_word_freqs,
                        max_threshold=options.max_threshold)

    # build a string containing all the words for the word cloud software
    output = ""

    # open output file to store the output string
    outFileName = target + ".csv"

    if not options.is_subreddit:
            outFileName = "user-" + outFileName

    outFile = open(outFileName, "w")

    # combine similar words into single count
    # e.g.: combine "picture," "pictures," and "picture's" into single count
    for word, count in popularWords.items():
        
        if word.endswith("'s"):
            
            # if the shorter form of the word was used
            if popularWords[word[:-2]] > 0:

                # combine the count into the most-used form of the word
                if popularWords[word[:-2]] > count:
                    popularWords[word[:-2]] += popularWords[word]
                    del popularWords[word]
                else:
                    popularWords[word] += popularWords[word[:-2]]
                    del popularWords[word[:-2]]
                       
        elif word.endswith("s"):

            # if the shorter form of the word was used
            if popularWords[word[:-1]] > 0:

                # combine the count into the most-used form of the word
                if popularWords[word[:-1]] > count:
                    popularWords[word[:-1]] += popularWords[word]
                    del popularWords[word]
                else:
                    popularWords[word] += popularWords[word[:-1]]
                    del popularWords[word[:-1]]

    for word in sorted(popularWords.keys()):

        # tweak this number depending on the subreddit
        # some subreddits end up having TONS of words and it seems to overflow
        # the Python string buffer
        if popularWords[word] > 2:
            pri = True

            # do not print a word if it is in the excluded word list
            for ew in excludedWords:
                if ew in word:
                    pri = False
                    break

            # don't print the word if it's just a number
            try:
                int(word)
                pri = False
            except:
                pass

            # add as many copies of the word as it was mentioned in the
            # subreddit
            if pri:
                txt = word + ":" + str(popularWords[word]) + "\n"
                txt = txt.encode("UTF-8")
                output += txt
                outFile.write(txt)

    outFile.close()

    # print the series of words for the word cloud software
    # place this text into wordle.net
    if options.verbose:
        print(output)


if __name__ == '__main__':
    sys.exit(main())
