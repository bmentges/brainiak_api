import subprocess
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a lot of cities in DEV Brainiak')
    parser.add_argument('num_times', type=int,
                        help='an integer for the accumulator')
    args = parser.parse_args()
    for i in range(args.num_times):
        cmd = 'curl -i -X POST -T new_city.json http://api.semantica.dev.globoi.com/v2/place/City'
        ret = subprocess.call(cmd.split())
        if ret != 0:
            print "Pau!"
