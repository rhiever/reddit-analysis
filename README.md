# Reddit Analysis project

Copyright 2013 Randal S. Olson.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

## Prerequisites

You must first install <a href="https://github.com/praw-dev/praw" target="_blank">PRAW</a> PRAW and any of its prerequisites before you can use this script. This script uses PRAW to scrape posts from Reddit.

Also note that this script currently only works on *nix machines. Windows users may use cygwin or similar *nix emulators.


## Files

`word_freqs.py` scrapes a specific subreddit or Redditor and prints out all of the commonly-used words for the past month.

`common-words.csv` is a data file containing a list of words that should be considered common. Note that this list is not final and is constantly changing.

`data_dumps/*.csv` are all of the word dumps we've added to the repo. Usually we only add the data dumps by request.


## Usage

First make sure that `word_freqs.py` and `common-words.csv` are in the same directory. Next, enter:

  python word_freqs.py -h
  
This command will detail all of the command line options and arguments for the script.

### Make a word cloud for a subreddit

Enter the following command, then wait until the script finishes running.

  python word_freqs.py YOUR-USERNAME /r/SUBREDDIT
  
where `YOUR-USERNAME` is your Reddit username and `SUBREDDIT` is the subreddit you want to make the word cloud for. You must provide *both* arguments for the script to work properly.

Once the script completes, it will save a file called `SUBREDDIT.csv` to the directory you ran it in. This file contains all of the commonly-used words from the subreddit you specified in the frequencies they were used.

To make a word cloud out of the words, copy all of the words into http://www.wordle.net/create and click the Go button. Ta-da, you're done!


### Make a word cloud for a Redditor

Enter the following command, then wait until the script finishes running.

  python word_freqs.py YOUR-USERNAME /u/REDDITOR
  
where `YOUR-USERNAME` is your Reddit username and `REDDITOR` is the Reddit user you want to make the word cloud for. You must provide *both* arguments for the script to work properly.

Once the script completes, it will save a file called `user REDDITOR.csv` to the directory you ran it in. This file contains all of the commonly-used words by the Reddit user you specified in the frequencies they used them.

To make a word cloud out of the words, copy all of the words into http://www.wordle.net/create and click the Go button. Ta-da, you're done!
