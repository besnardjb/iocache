import os
import argparse
import pathlib

import iosystem


class ArgParse():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._reg_args()
        self._args = self.parser.parse_args()

    def _reg_args(self):
        self.parser.add_argument('-c', '--config', nargs=1, type=pathlib.Path, help='Path to config file', required=True)

    @property
    def config(self):
        p = pathlib.Path(self._args.config[0])
        if not p.is_file():
            raise Exception("{} is not a regular file".format(p))
        if p.suffix != ".io":
            raise Exception("{} is not a .io file".format(p))
        return p


ap = ArgParse()


ios = iosystem.IOSystem(ap.config)

ios.ops_clear()

ios.ops_push(["a_local", "1G", 0.0])
ios.ops_push(["b_local", "20G", 10.0])
ios.ops_push(["c_local", "15G", 20.0])

ios.run(ref="lts", tick=1)


ios.plot()