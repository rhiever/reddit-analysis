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
excludedWords = ["http://", "r/", "https://", "gt", "...", "deleted",
                 "k/year", "--", "/", "u/", ")x", "amp;c"]


def parseText(text, max_threshold=0.34, single_occurrence=False):
    """Parse the passed in text and add words that are not common.

    :param max_threshold: The maximum relative frequency in the text a word can
        appear to be added. This prevents word spamming.
    :param single_occurrence: When True, only count each word once, rather than
        how many times it appears in the text.

    """
    total = 0.  # intentionally a float
    text_words = defaultdict(int)
    for word in text.split():  # Split on all whitespace
        word = word.strip(punctuation).lower()
        total += 1
        if word and word not in commonWords:
            text_words[word] += 1


    # Add to popularWords list
    for word, count in text_words.items():
        if count / total <= max_threshold:
            if single_occurrence:
                popularWords[word] += 1
            else:
                popularWords[word] += count


def processRedditor(redditor, max_subs):
    """Parse all submissions and comments for the given Redditor."""
    for entry in with_status(redditor.get_overview(limit=max_subs)):
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


def processSubreddit(subreddit, max_subs):
    """Parse all comments, title text, and selftext in a given subreddit."""
    for submission in with_status(subreddit.get_top_from_month(limit=max_subs)):
        processSubmission(submission)


def with_status(iterable):
    """Wrap an interable outputing '.' for each item (up to 50 a line)."""
    for i, item in enumerate(iterable):
        sys.stderr.write('.')
        sys.stderr.flush()
        if i % 50 == 49:
            sys.stderr.write('\n')
        yield item


def main():
    try:
        username, target, max_subs = sys.argv[1:]
        
        if target.startswith('/r/'):
            is_subreddit = True
        elif target.startswith('/u/'):
            is_subreddit = False
        else:
            raise Exception
    
        target = target[3:]
        max_subs = int(max_subs)
        if max_subs == 0:
            max_subs = None

    except:
        print("Usage: subreddit_word_freqs.py YOUR_USERNAME TARGET MAX_SUBS\n\n"
              "TARGET should either be of the format '/r/SUBREDDIT' or '/u/USERNAME'.\n\n"
              "MAX_SUBS should be 0 for to scrape all submissions, otherwise specify the number.")
        return 1

    # open connection to Reddit
    r = praw.Reddit(user_agent="bot by /u/{0}".format(username))

    # run analysis
    sys.stderr.write('Analyzing {0}\n'.format(sys.argv[2]))
    sys.stderr.flush()

    if is_subreddit:
        processSubreddit(r.get_subreddit(target), max_subs)
    else:
        processRedditor(r.get_redditor(target), max_subs)

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
