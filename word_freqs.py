#!/usr/bin/env python

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

import csv
import praw
import string
import sys
from collections import defaultdict
from optparse import OptionParser
from requests.exceptions import HTTPError

popularWords = defaultdict(int)
commonWords = set()

# punctuation to strip from words
punctuation = " " + string.punctuation + "\n"

# load a list of common words to ignore
with open("common-words.csv", "r") as commonWordsFile:
    for commonWordFileLine in csv.reader(commonWordsFile):
        for commonWord in commonWordFileLine:
            commonWords.add(commonWord.strip(punctuation).lower())

with open("/usr/share/dict/words", "r") as dictionaryFile:
    for dictionaryWord in dictionaryFile:
        commonWords.add(dictionaryWord.strip(punctuation).lower())

# put words here that you don't want to include in the word cloud
excludedWords = ["http://", "r/", "https://", "gt", "...", "deleted",
                 "k/year", "--", "/", "u/", ")x", "amp;c"]

# command-line argument parsing
parser = OptionParser()

parser.add_option("-u", "--username",
                  action="store",
                  type="string",
                  dest="username",
                  help="your Reddit username.")

parser.add_option("-t", "--target",
                  action="store",
                  type="string",
                  dest="target",
                  help="subreddit or user to count word frequencies for. "
                  "enter /r/TARGET for subreddits or /u/TARGET for users.")

parser.add_option("-p", "--period",
                  action="store",
                  type="string",
                  dest="period",
                  default="month",
                  help="period to count words over: day/week/month/year/all. [default: month]")

parser.add_option("--ms", "--maxsubs",
                  action="store",
                  type="int",
                  dest="max_submissions",
                  default="0",
                  help="maximum number of submissions to count word frequencies for. "
                  "set MAX_SUBMISSIONS to 0 to count all submissions, otherwise specify "
                  "the number of submissions to count. "
                  "[default: 0]")

parser.add_option("--mt", "--maxthresh",
                  action="store",
                  type="float",
                  dest="max_threshold",
                  default="0.34",
                  help="maximum relative frequency in the text a word can "
                  "appear to be considered in word counts. prevents word spamming "
                  " in a single submission. [default: 0.34]")

parser.add_option("--cw",
                  action="store_false",
                  dest="count_word_freqs",
                  help="only gather which words occur, but not counts.")

parser.add_option("--cwf",
                  action="store_true",
                  dest="count_word_freqs",
                  default=True,
                  help="count the number of times each word occurs. "
                  "[default]")

(options, args) = parser.parse_args()

username = options.username
full_target = options.target
count_word_period = options.period
max_submissions = options.max_submissions
max_word_threshold = options.max_threshold
count_word_freqs = options.count_word_freqs

if full_target.startswith("/r/"):
    is_subreddit = True
elif full_target.startswith("/u/"):
    is_subreddit = False
else:
    raise Exception("\nInvalid target.\n")

target = full_target[3:]

if count_word_period not in ["day", "week", "month", "year", "all"]:
    raise Exception("\nInvalid period.\n")

if max_submissions == 0:
    max_submissions = None



def parseText(text):
    """Parse the passed in text and add words that are not common."""
    total = 0.0  # intentionally a float
    text_words = defaultdict(int)
    for word in text.split():  # Split on all whitespace
        word = word.strip(punctuation).lower()
        total += 1
        if word and word not in commonWords:
            text_words[word] += 1


    # Add to popularWords list
    for word, count in text_words.items():
        if count / total <= max_word_threshold:
            if count_word_freqs:
                popularWords[word] += count
            else:
                popularWords[word] += 1


def processRedditor(redditor):
    """Parse submissions and comments for the given Redditor."""
    for entry in with_status(redditor.get_overview(limit=max_submissions)):
        if isinstance(entry, praw.objects.Comment):  # Parse comment
            parseText(entry.body)
        else:  # Parse submission
            processSubmission(entry, include_comments=False)


def processSubmission(submission, include_comments=True):
    """Parse a submission's text and body (if applicable).

    Include the submission's comments when `include_comments` is True.

    """
    if include_comments:  # parse all the comments for the submission
        submission.replace_more_comments()
        for comment in praw.helpers.flatten_tree(submission.comments):
            parseText(comment.body)

    # parse the title of the submission
    parseText(submission.title)

    # parse the selftext of the submission (if applicable)
    if submission.is_self:
        parseText(submission.selftext)


def processSubreddit(subreddit):
    """Parse comments, title text, and selftext in a given subreddit."""
    
    submission_list = []
    
    # determine period to count the words over
    if count_word_period == "day":
        submission_list = subreddit.get_top_from_day(limit=max_submissions)
    elif count_word_period == "week":
        submission_list = subreddit.get_top_from_week(limit=max_submissions)
    elif count_word_period == "month":
        submission_list = subreddit.get_top_from_month(limit=max_submissions)
    elif count_word_period == "year":
        submission_list = subreddit.get_top_from_year(limit=max_submissions)
    elif count_word_period == "all":
        submission_list = subreddit.get_top_from_all(limit=max_submissions)

    for submission in with_status(submission_list):
        try:
            processSubmission(submission)
        except HTTPError as exc:
            sys.stderr.write("\nSkipping submission {0} due to HTTP status {1} error. Continuing...\n"
                             .format(submission.url, exc.response.status_code))
            continue


def with_status(iterable):
    """Wrap an interable outputing '.' for each item (up to 50 a line)."""
    for i, item in enumerate(iterable):
        sys.stderr.write('.')
        sys.stderr.flush()
        if i % 50 == 49:
            sys.stderr.write('\n')
        yield item


def main():

    # open connection to Reddit
    r = praw.Reddit(user_agent="bot by /u/{0}".format(username))

    # run analysis
    sys.stderr.write("Analyzing {0}\n".format(full_target))
    sys.stderr.flush()

    if is_subreddit:
        processSubreddit(r.get_subreddit(target))
    else:
        processRedditor(r.get_redditor(target))

    # build a string containing all the words for the word cloud software
    output = ""

    # open output file to store the output string
    outFileName = str(target) + ".csv"

    if not is_subreddit:
            outFileName = "user " + outFileName

    outFile = open(outFileName, "w")

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
                txt = ((word + " ") * popularWords[word])
                txt = txt.encode("UTF-8").strip(" ")
                txt += " "
                output += txt
                outFile.write(txt)

    outFile.close()

    # print the series of words for the word cloud software
    # place this text into wordle.net
    print output


if __name__ == '__main__':
    sys.exit(main())
