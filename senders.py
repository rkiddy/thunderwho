
import argparse
import os.path
import traceback
from datetime import datetime as dt
from pprint import pprint

import sqlean


def arguments():
    parser = argparse.ArgumentParser()
    opts = parser.add_mutually_exclusive_group()
    opts.add_argument('--before', help="Look for senders with last sent only before this, like '2025-09-01'")
    opts.add_argument('--after', help="Look for senders with last sent only after this, like '2025-09-01'")
    opts.add_argument('--today', action="store_true", help="Today's email only.")
    opts.add_argument('--one-day', help="Given a date (YYYY-MM-DD) show only that date.")
    parser.add_argument('--name', help="Look for senders whose name includes this substring (case-insensitive)")
    parser.add_argument('--mailbox', help="Look only in this mailbox.")
    parser.add_argument('--profile', default="default")
    parser.add_argument('--verbose', '-v', action="store_true")
    return parser.parse_args()


def date_for_ts(t):

   t2 = int(str(t)[:10])
   return dt.fromtimestamp(t2).strftime('%Y-%m-%d %H:%S')


def date_is_ok(d):
    try:
        parts = d.split('-')
        if len(parts) != 3:
            return False
        if int(parts[0]) < 2000 or int(parts[0]) > 2030:
            return False
        if len(parts[1]) != 2 or int(parts[1]) < 1 or int(parts[1]) > 12:
            return False
        if len(parts[2]) != 2 or int(parts[2]) < 1 or int(parts[1]) > 31:
            return False
    except:
        return False
    return True


def dir(profile):
    tdir = f"{os.path.expanduser("~")}/.thunderbird"
    ddir = [r for r in os.listdir(tdir) if r.endswith(f".{profile}")]
    if len(ddir) == 0:
        return None
    else:
        return f"{tdir}/{ddir[0]}"


if __name__ == '__main__':

    args = arguments()

    # check parameter dates.
    if args.before is not None and not date_is_ok(args.before):
        raise Exception(f"Bad data value for before: {args.before}")
    if args.after is not None and not date_is_ok(args.after):
        raise Exception(f"Bad data value for after: {args.after}")
    if args.one_day is not None and not date_is_ok(args.one_day):
        raise Exception(f"Bad data value for \"--one-day\": {args.one_day}")

    # enable all extensions
    sqlean.extensions.enable_all()

    # db_file = '/home/ray/.thunderbird/xll9owtz.default/global-messages-db.sqlite'

    profile_dir = dir(args.profile)
    if not profile_dir:
        raise Exception(f"No profile directory found for: {dir(args.profile)}")

    os.system(f"cp {profile_dir}/global-messages-db.sqlite /tmp")

    db = sqlean.connect('/tmp/global-messages-db.sqlite')

    if args.mailbox:
        folder_table = ", folderLocations f1 "
        folder_qual = f"and m2.folderID = f1.id and f1.name = '{args.mailbox}' "
    else:
        folder_table = ""
        folder_qual = ""

    sql = "select m1.c3author, min(m2.date), max(m2.date) " \
          f"from messagesText_content m1, messages m2 {folder_table}" \
          f"where m1.docid = m2.id {folder_qual}" \
          "group by m1.c3author order by m1.c3author"

    if args.verbose:
        print(f"sql: {sql}")

    r = db.execute(sql)
 
    hdr = 'Earliest            Latest              Sender\n' \
          '==================  ==================  ===========================\n'

    for row in r.fetchall():
        row = list(row)
        row[0] = row[0].replace(' undefined', '')
        if row[0] == '':
            continue
        row[1] = date_for_ts(row[1])
        row[2] = date_for_ts(row[2])

        # only for today.
        if args.today:
            dt_str = dt.now().strftime('%Y-%m-%d')
            if row[2] < dt_str:
                continue

        # before or after some date.
        if args.after is not None and row[2] < args.after:
            continue
        if args.before is not None and row[2] > args.before:
            continue

        # only sender with this name.
        if args.name is not None and args.name.lower() not in row[0].lower():
            continue

        if args.one_day is not None:
            end = f"{args.one_day} 23:59"
            if (row[1] >= args.one_day and row[1] <= end) or (row[2] >= args.one_day and row[2] <= end):
                pass
            else:
                continue

        # format the dates for listing and print out the row.
        while len(row[1]) < 20:
            row[1] = f"{row[1]} "
        while len(row[2]) < 20:
            row[2] = f"{row[2]} "
        print(f"{hdr}{row[1]}{row[2]}{row[0]}")
        hdr = ''

    db.close()
