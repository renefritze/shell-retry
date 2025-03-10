# coding=utf-8

import argparse
import logging
import time
from subprocess import Popen


def setup_logging(args):
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(format=log_format, level=level)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--backoff', help='backoff factor (sleep(--interval *= --backoff)', type=float, default=1)
    parser.add_argument('--retry-count', type=int, help='How many time re-run cmd if it fails', default=1)
    parser.add_argument('--interval', help='Initial interval between retries', type=float, default=1)
    parser.add_argument('--interval-max', help='upper limit for interval', type=float)
    parser.add_argument('--interval-min', help='lower limit for interval', type=float)
    parser.add_argument('--verbose', help='Be verbose, write how many retries left and how long will we wait',
                        action='store_true', default=False)
    parser.add_argument("cmd", nargs='+', type=str, action='store')
    return parser.parse_args()


def next_interval(args):
    interval = args.interval
    interval *= args.backoff
    if args.interval_max is not None:
        interval = min(interval, args.interval_max)
    if args.interval_min is not None:
        interval = max(interval, args.interval_min)
    return interval


def _run(args, retry):
    logging.info("run {0}".format(args.cmd))
    process = Popen(args.cmd)
    process.communicate()
    if process.returncode == 0:
        exit(0)
    logging.info("command returned {0}".format(process.returncode))
    try:
        process.kill()
    except OSError:
        pass
    if retry <= 0:
        exit(process.returncode)
    logging.info('waiting {0:f} seconds, {1} retries left'.format(args.interval, retry))
    time.sleep(args.interval)
    args.interval = next_interval(args)


def run(args):
    logging.info(args)
    for retry in range(args.retry_count, -1, -1):
        _run(args, retry)
    exit(1)


def main():
    args = parse_args()
    setup_logging(args)
    run(args)


if __name__ == '__main__':
    main()
