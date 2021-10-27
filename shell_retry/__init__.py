# coding=utf-8

import argparse
import logging
from packaging.version import Version
from subprocess import check_output, CalledProcessError

import backoff

if Version(backoff.__version__) >= Version('2'):
    other_kwargs = {'raise_on_giveup': False}
else:
    other_kwargs = {}
args = None


def setup_logging(args):
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(format=log_format, level=level)
    logging.getLogger('backoff').addHandler(logging.StreamHandler())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--retry-count', type=int, help='How many times to re-run cmd if it fails', default=10)
    parser.add_argument('--verbose', help='Be verbose, write how many retries left and how long will we wait',
                        action='store_true', default=False)
    parser.add_argument("cmd", nargs='+', type=str, action='store')
    return parser.parse_args()


def _max_tries():
    return args.retry_count + 1


@backoff.on_exception(wait_gen=backoff.expo,
                      exception=CalledProcessError,
                      max_tries=_max_tries,
                      **other_kwargs)
def _run(args, retry):
    logging.info("run {0}".format(args.cmd))
    return check_output(args.cmd)


def run(args):
    logging.info(args)
    for retry in range(args.retry_count, -1, -1):
        _run(args, retry)
    exit(1)


def main():
    global args
    args = parse_args()
    setup_logging(args)
    run(args)


if __name__ == '__main__':
    main()
