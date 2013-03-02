import praw, heapq, csv, string
from collections import defaultdict

popularWords = defaultdict(int)
commonWords = defaultdict(int)

# punctuation to strip from words
punctuation = " " + string.punctuation + "\n"

# numbers to strip from words
for i in range(10):
    punctuation += str(i)

# store a list of common words to ignore
commonWordsFile = open("common-words.csv", "r")
for commonWordFileLine in csv.reader(commonWordsFile):
    for commonWord in commonWordFileLine:
        commonWords[commonWord.strip(punctuation).lower()] = 1
commonWordsFile.close()

dictionaryFile = open("/usr/share/dict/words", "r")
for dictionaryWord in dictionaryFile:
    dictionaryWord = dictionaryWord.strip(punctuation).lower()
    commonWords[dictionaryWord] = 1
dictionaryFile.close()

# open connection to Reddit
r = praw.Reddit(user_agent="bot by /u/<ENTER_USERNAME_HERE>")

# parses a comment
def parseComment(comm):
    try:
        for paragraph in comm.body.split("\n"):
            for word in paragraph.split(" "):
                word = word.strip(punctuation).lower()
                if word != "" and commonWords[word] < 1:
                    popularWords[word] += 1
    except AttributeError:
        pass


# parse all comments and posts for a given Reddit user
for entry in r.get_redditor("<ENTER_USERNAME_HERE>").get_overview(limit=None):
    parseComment(entry)


# put words here that you don't want to include in the word cloud
excludedWords = ["http://", "r/", "https://", "gt", "...", "deleted", "tl", "k/year", "--", "/", "u/", ")x"]

# build a string containing all the words for the word cloud software
output = ""

for word in sorted(popularWords.keys()):

    # tweak this number depending on the subreddit
    # some subreddits end up having TONS of words and it seems to overflow the Python string buffer
    if popularWords[word] > 2:
        pri = True
        
        # do not print a word if it is in the excluded word list
        for ew in excludedWords:
            if ew in word:
                pri = False
                break
             
        # add as many copies of the word as it was mentioned in the subreddit
        if pri:
            for i in range(popularWords[word]):
                output += word + " "

# print the series of words for the word cloud software
print output
