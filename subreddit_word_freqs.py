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
excludedWords = ["http://", "r/", "https://", "gt", "...", "deleted", "tl",
                 "k/year", "--", "/", "u/", ")x"]


def parseText(text):
    """Parse the passed in text and add words that are not common."""
    for word in text.split():  # Split on all whitespace
        word = word.strip(punctuation).lower()
        if word not in commonWords:  # Guaranteed not to be ''
            popularWords[word] += 1


def processSubreddit(r, subreddit):
    """Parse all comments, title text, and selftext in a given subreddit."""
    sys.stderr.write('Analyzing /r/{0}\n'.format(subreddit))
    for submission in subreddit.get_top_from_month(limit=None):

        # Provide a visible status indicator
        sys.stderr.write('.')
        sys.stderr.flush()

        # parse all the comments for the submission
        submission.replace_more_comments()
        for comment in praw.helpers.flatten_tree(submission.comments):
            parseText(comment.body)

        # parse the title of the submission
        parseText(submission.title)

        # parse the selftext of the submission (if applicable)
        if submission.is_self:
            parseText(submission.selftext)


def main():
    try:
        username, subreddit = sys.argv[1:]
    except:
        print 'Usage: subreddit_word_freqs.py username subreddit'
        return 1

    # open connection to Reddit
    r = praw.Reddit(user_agent="bot by /u/{0}".format(username))
    processSubreddit(r, r.get_subreddit(subreddit))

    # build a string containing all the words for the word cloud software
    output = ""

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
                output += (word + " ") * popularWords[word]

    # print the series of words for the word cloud software
    print output


if __name__ == '__main__':
    sys.exit(main())
