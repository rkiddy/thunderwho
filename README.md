I use Thunderbird and I want to keep using it, but parts of its UI are amazingly bad, or they
seem to work against some of my organizational challenges. For example, I want to see a list of senders of
emails. I do not want to sort by sender. I want to see a list of senders, one sender for each row, with
inforamtion like the date of last message sent. Should this be so hard? I do not think so. But it seems
to be.

So I figured out a way to do this accessing the messages file directly and using SQLite to get to the
information that I want.

The "thunderwho" script is just a wrapper for calling the senders.py script. I put the "thunderwho" script
in a directory that is in my PATH and that is it.

```
$ thunderwho --help
usage: senders.py [-h] [--before BEFORE | --after AFTER | --today | --one-day ONE_DAY] [--name NAME]
                  [--mailbox MAILBOX] [--profile PROFILE] [--verbose]

options:
  -h, --help         show this help message and exit
  --before BEFORE    Look for senders with last sent only before this, like '2025-09-01'
  --after AFTER      Look for senders with last sent only after this, like '2025-09-01'
  --today            Today's email only.
  --one-day ONE_DAY  Given a date (YYYY-MM-DD) show only that date.
  --name NAME        Look for senders whose name includes this substring (case-insensitive)
  --mailbox MAILBOX  Look only in this mailbox.
  --profile PROFILE
  --verbose, -v
```
The default value of the profile is "default", as makes sense.

Installation:

Move the fetched thunderwho to wherever you want it and fix the location specified in the thunderwho script.
```
% alias tp='./.venv/bin/python'
% virtualenv .venv
% tp -m pip install sqlean.py==3.50.4.4
% tp ./senders.py --help
```
