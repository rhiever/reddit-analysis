[![PyPI version](https://badge.fury.io/py/redditanalysis.svg)](https://badge.fury.io/py/redditanalysis)
![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)
![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)

# Reddit Analysis project

Please send all requests to make a Most-Used Words (MUW) cloud to http://www.reddit.com/r/MUWs/

Feel free to post the MUWs you've made there, too.

## License

Copyright 2016 Randal S. Olson.

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
Preferably, use the [Anaconda Python distribution](http://continuum.io/downloads) for an easy install.

Next, you can install this package. Enter the following command into the
terminal:

    pip install redditanalysis

You may need to put `sudo` in front of the above command if your system
requires root access.

If you want to install the lastest development version from github first
clone the package:

    git clone https://github.com/rhiever/reddit-analysis.git

change into the `reddit-analysis` directory:

    cd reddit-analysis

then run the update script:

    python setup.py install


## Files in this repository

`redditanalysis/words/common-words.txt` is a data file containing a list of words
that should be considered common. Note that this list is not final and is
constantly changing.

`redditanalysis/words/dict-words.txt` is a data file containing a list of words
from a dictionary. It is only recommended to use this file (with the `-x` option)
if you want `word_freqs` to pick out very uncommon words.


## Usage

Once installed, run the following on your command line to produce a usage
message:

    word_freqs --help

This command will detail all of the command line options and arguments for the
`word_freqs`.

### Make a MUW cloud for a subreddit or redditor


#### Before you use - create an app
To query the subreddits, you need two configurations:
- client id 
- client secret 

If you have a Reddit App, you can copy the configurations, 
else, create one (here)[https://www.reddit.com/prefs/apps]

#### Before you use the CLI - set environment variables
- praw_client_id whose value is the client id
- praw_client_secret whose value is the client secret

#### How to use the command 

To count the most-used words for a subreddit over the last month, enter the
following command:

    word_freqs YOUR-USERNAME /r/SUBREDDIT
OR if there are more than one subreddits to search
    word_freqs YOUR-USERNAME "/r/SUBREDDIT1;/r/SUBREDDIT2;/r/SUBREDDIT3"

Similarly, for a reddit user:

    word_freqs YOUR-USERNAME /u/REDDITOR

where `YOUR-USERNAME` is your reddit username and `SUBREDDIT` / `REDDITOR` is
the subreddit / redditor you want to make the MUW cloud for. You
must provide *both* arguments for the script to work properly.

#### Example usages
Produce word frequency for two subreddits `/r/sharktankindia` and `/r/sharktank`
```console
foo@bar:~$ word_freqs someusername "/r/sharktankindia;/r/sharktank" 
```
Produce word frequency for two subreddits `/r/sharktankindia` and `/r/sharktank` for the submissions which happened in the last day as well as matching the string "Season 2"
```console
foo@bar:~$ word_freqs someusername "/r/sharktankindia;/r/sharktank" -p day -s "Season 2"
```

Produce work frequency for two subreddits `/r/Pizza` and `/r/Connecticut` matching one of the strings "New York" OR "NY Style" OR "China Dishes"
```console
foo@bar:~$ word_freqs someusername "/r/Pizza;/r/Connecticut" -p day -s '"Detroit" OR "New York" OR "NY Style" OR "China Dishes"'
```

The above query will search the submission title as well as the comments of the submission for the matches. 

**Why is your username required?** Simply because it will be used as the user-agent when making the Reddit API request. Reddit asks its API users to use something unique as the user-agent and recomends to use the users username.

Once the script completes, it will create a file called `subreddit-SUBREDDIT.csv` (or
`user-REDDITOR.csv`) to the directory you ran it in. This file contains all of
the commonly-used words from the subreddit / redditor you specified in the
frequencies they were used.

To make a MUW cloud out of the words, copy all of the words into
http://www.wordle.net/compose and click the Go button. Ta-da, you're done!

### Multiprocess

`reddit-analysis` supports multiprocess PRAW. This allows you to run multiple instances
of `reddit-analysis` simultaneously and not risk getting banned for overusing the reddit API.
To enable multiprocess PRAW in `reddit-analysis`, add the `-u` flag.

See the [PRAW documentation](https://praw.readthedocs.org/en/latest/pages/multiprocess.html) for more information.


