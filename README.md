# Reddit Analysis project

Please send all requests to make a Most-Used Words (MUW) word cloud to http://www.reddit.com/r/MUWs/

Feel free to post the MUWs you've made there, too.

## License

Copyright 2013 Randal S. Olson.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see http://www.gnu.org/licenses/.

## Dependencies

You must first install the Python library if you do not have that already.
Preferably, use the <a href="http://www.enthought.com/products/epd_free.php"
target="_blank">Enthought Python Distribution</a> (EPD) for an easy install.

Next, you must install <a href="https://github.com/praw-dev/praw"
target="_blank">PRAW</a> and any of its dependencies before you can use this
script. This script uses PRAW to fetch data from reddit. Enter the following
command into the terminal:

    easy_install praw
    
You may need to put `sudo` in front of the above command if your system requires
root access.

Note that this script currently only works on *nix machines. Windows users
may use cygwin or similar *nix emulators.

On Linux systems, this script also depends on the `words` package.


## Files in this repository

`word_freqs.py` scrapes a specific subreddit or redditor and prints out all of
the commonly-used words for the past month.

`common-words.csv` is a data file containing a list of words that should be
considered common. Note that this list is not final and is constantly changing.

`data_dumps/*.csv` are all of the word dumps we've added to the repo. Usually
we only add the data dumps by request.


## Usage

First make sure that `word_freqs.py` and `common-words.csv` are in the same
directory. Next, enter:

    python word_freqs.py --help

This command will detail all of the command line options and arguments for the
script.

### Make a word cloud for a subreddit or redditor

To count the most-used words for a subreddit over the last month, enter the
following command:

    python word_freqs.py YOUR-USERNAME /r/SUBREDDIT

Similarly, for a reddit user:

    python word_freqs.py YOUR-USERNAME /u/REDDITOR

where `YOUR-USERNAME` is your reddit username and `SUBREDDIT` / `REDDITOR` is
the subreddit / redditor you want to make the word cloud for. You
must provide *both* arguments for the script to work properly.

Once the script completes, it will create a file called `SUBREDDIT.csv` (or
`user-REDDITOR.csv`) to the directory you ran it in. This file contains all of
the commonly-used words from the subreddit / redditor you specified in the
frequencies they were used.

To make a word cloud out of the words, copy all of the words into
http://www.wordle.net/create and click the Go button. Ta-da, you're done!
