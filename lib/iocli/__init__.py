import os
import argparse
import pathlib

import lib.iosim.iosystem as iosystem


class ArgParse():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._reg_args()
        self._args = self.parser.parse_args()

    def _reg_args(self):
        self.parser.add_argument('-c', '--config', nargs=1, type=pathlib.Path, help='Path to config file', required=True)
        self.parser.add_argument('-s', '--ops', nargs=1, type=pathlib.Path, help='Path to operation file', required=False)
        self.parser.add_argument('-d', '--dot', nargs=1, type=pathlib.Path, help='Generate cache dotfile', required=False)
        self.parser.add_argument('-o', '--out', nargs=1, type=pathlib.Path, help='Output file for the graph', required=False)


    @property
    def config(self):
        p = pathlib.Path(self._args.config[0])
        if not p.is_file():
            raise Exception("{} is not a regular file".format(p))
        if p.suffix != ".io":
            raise Exception("{} is not a .io file".format(p))
        return p

    @property
    def ops(self):
        return self._args.ops

    @property
    def dot(self):
        return self._args.dot

    @property
    def output(self):
        if self._args.out is None:
            return None
        else:
            return self._args.out[0]


def cli_entry():

    ap = ArgParse()

    ios = iosystem.IOSystem(ap.config)

    # Generate DOT case
    if ap.dot:
        ios.dot(ap.dot[0])
        exit(0)

    if not ap.ops:
        raise Exception("You should pass an operation file to run simulation")
    else:
        ios.load_ops(ap.ops[0])

    ios.run()

    ios.plot(ap.output)

