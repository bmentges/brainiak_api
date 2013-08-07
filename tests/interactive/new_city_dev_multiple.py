import subprocess
import argparse
from multiprocessing import Pool


def spawn_client(repetitions):
    for i in range(repetitions):
        cmd = 'curl -i -X POST -T new_city.json http://api.semantica.dev.globoi.com/v2/place/City'
        subprocess.call(cmd.split())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a lot of cities in DEV Brainiak')
    parser.add_argument('num_times', type=int,
                        help='an integer for the accumulator')
    parser.add_argument('workers', type=int,
                        help='the number of client processes')
    args = parser.parse_args()
    pool = Pool(args.workers)
    pool.map(spawn_client, [args.num_times] * args.workers)
