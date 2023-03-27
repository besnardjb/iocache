
import json
from os import name

import random

import matplotlib.pyplot as plt


class Link():
    def __init__(self, bandwith, name="link"):
        self._output = None
        self._input = None
        self._bw = bandwith
        self._to_write = 0
        self.name = name

    def __str__(self):
        return "{} ({} - {}) @ {}".format(self.name, "NONE" if not self._input else self._input.name, "NONE" if not self._output else self._output.name, self.bandwidth)

    def bind_out(self, output):
        self._output = output

    def bind_in(self, input):
        self._input = input

    @property
    def lin(self):
        return self._input

    @property
    def lout(self):
        return self._output

    @property
    def writing(self):
        return self._to_write

    @property
    def bandwidth(self):
        cache_bw = self._output.bandwidth
        return self._bw if self._bw < cache_bw else cache_bw

    def write_init(self, size, tick=1.0):
        self._to_write = size

    def write_tick(self, tick=1.0):
        # Is link bandwith limitting transmit ?
        tick_size = self.bandwidth * tick
        size = self._to_write if self._to_write <= tick_size else tick_size
        ret = self._output.write_tick(size, tick)
        return ret

    def write_done(self):
        self._to_write = 0


class Cache():
    def __init__(self, size, bandwith, name="cache", inputs=None, outputs=None):
        self._data_current = 0
        self._data_size = size
        self._bw = bandwith
        self._in = inputs if inputs else []
        self._out = outputs if outputs else []
        self._agv_in_bw = 0
        self.name = name

    def __str__(self):
        ret = "{} BW {}\n".format(self.name, self.bandwidth)
        for e in self._in:
            ret += "   IN: {}\n".format(e)
        for e in self._out:
            ret += "   OUT: {}\n".format(e)
        return ret

    @property
    def size(self):
        return self._data_size;

    def _bind(self):
        for e in self._in:
            e.bind_out(self)
        for e in self._out:
            e.bind_in(self)

    def attach_in(self, link):
        self._in.append(link)
        link.bind_out(self)

    def attach_out(self, link):
        self._out.append(link)
        link.bind_in(self)

    @property
    def current(self):
        return self._data_current

    @property
    def sizeleft(self):
        return self._data_size - self._data_current

    def flush_tick(self, tick=1.0):
        cursize = self._data_current

        for e in self._out:
            e.write_init(cursize, tick)

        for e in self._out:
            written = e.write_tick(tick)
            self._data_current = self._data_current - written

    @property
    def input_avg_bw(self):
        to_write = sum([1 for x in self._in if x.writing])
        if to_write == 0:
            to_write = 1
        return float(self.bandwidth) / to_write;



    def write_tick(self, size, tick=1.0):

        if self.full:
            return 0

        # Cannot write more than sizeleft
        szl = self.sizeleft
        written = size if size < szl else szl

        avg_bw = self.input_avg_bw

        # Cannot write more than bandwidth
        tick_size = avg_bw * tick
        written = written if written <= tick_size else tick_size

        self._data_current += written

        return written

    @property
    def bandwidth(self):
        return 0 if self.full else self._bw

    @property
    def empty(self):
        return (self._data_current == 0)

    @property
    def full(self):
        return (self._data_size <= self._data_current)

def uconvert(val):
    if val.endswith("K"):
        return float(val[:-1]) * (1024*1024);
    if val.endswith("M"):
        return float(val[:-1]) * (1024*1024);
    if val.endswith("G"):
        return float(val[:-1]) * (1024*1024*1024);
    if val.endswith("T"):
        return float(val[:-1]) * (1024*1024*1024*1024);
    return float(val)


SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

def rfsize(size_in_bytes, pos=None):
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{size_in_bytes:.2f} {SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'

class IOSystem():
    def __init__(self, config_file):
        self._conf = config_file
        self.caches = {}
        self.links = {}
        self._load_conf(config_file)

        self.ref = None
        self.tick = None

        self.iops = []
        self.xaxis = []
        self.bws = {}
        self.sizes = {}
        self._mark_val = 0

    def _load_conf(self, config_file):
        with open(config_file) as f:
            data = json.load(f)

        if not "links" in data:
            raise Exception("No link list")

        if not "caches" in data:
            raise Exception("No caches")

        for c,v in data["caches"].items():
            nc = Cache(uconvert(v["size"]), uconvert(v["bw"]), name=c)
            self.caches[c] = nc
            print("New cache {} with size {}({}) and bandwidth {}({})".format(c, v["size"], nc.size, v["bw"], nc.bandwidth))

        for l,v in data["links"].items():
            print("{} : {}".format(l,v))
            nl = Link(uconvert(v["bw"]), name=l)
            self.links[l] = nl
            if "from" in v:
                self.caches[v["from"]].attach_out(nl)
            if "to" in v:
                self.caches[v["to"]].attach_in(nl)

        for c in self.caches.values():
            print(c)

    def ops_clear(self):
        self.iops = []
        self.bws = {}
        self.sizes = {}
        self.xaxis = []

    def ops_push(self, op):
        if len(op) != 3:
            raise Exception("Operations must have three elements")
        self.iops.append(op)

    def _random_marker(self):
        m = [".", "x", "o", "<", ">", "v", "^", "+", "H", "h", "*"]
        ret = m[self._mark_val]
        self._mark_val = (self._mark_val + 1) % len(m)
        return ret

    def run(self, ref=None, tick=None):

        if ref is None:
            ref = self.ref

        if tick is None:
            tick = self.tick

        if tick is None:
            tick = 1.0

        total = self.ops_total(self.iops)

        time = 0

        while abs(self.caches[ref].current - total) > 1:
            print(self.iops)

            runningops = [ x for x in self.iops if x[2] <= time]

            ret_ops, w = self.write(runningops, tick)

            i = 0
            for op in ret_ops:
                link = self.links[op[0]]
                if not link.name in self.bws:
                    self.bws[link.name] = []
                self.bws[link.name].append(w[i]/tick)
                i = i +1

            # If op is not running add 0.0
            for op in self.iops:
                not_running = 1
                for rop in runningops:
                    if rop[0] == op[0]:
                        not_running = 0
                        break
                if not_running:
                    link = self.links[op[0]]
                    if not link.name in self.bws:
                        self.bws[link.name] = []
                    self.bws[link.name].append(0.0)

            for c in self.caches.values():
                name = c.name
                if not name in self.sizes:
                    self.sizes[name] = []
                self.sizes[name].append(c.current)

            self.xaxis.append(time)

            # We need to backport size_left to original array
            for rop in runningops:
                for top in self.iops:
                    if rop[0] == top[0]:
                        top[1] = rop[1]

            print(self.cache_state())

            time = time + tick



    def plot(self, output=None):
        # First pad all arrays in BW
        maxlen = max([len(self.bws[x]) for x in self.bws])

        tmp = {}

        plt.rcParams.update({'font.size': 6})


        for c,v in self.bws.items():
            t = v + [0.0] * (maxlen - len(v))
            tmp[c] = t

        self.bws.update(tmp)

        # Now plot
        count = len(self.sizes) + 1
        fig, axs = plt.subplots(count)

        axs[0].yaxis.set_major_formatter(rfsize)
        axs[0].set_title("Bandwiths on links with IOPs")
        for n,v in self.bws.items():
            axs[0].plot(self.xaxis, v, label=n, marker=self._random_marker(), linewidth=0.3, markersize=2)

        axs[0].legend()

        cnt = 0
        for c,v in self.sizes.items():
            axs[1+cnt].yaxis.set_major_formatter(rfsize)
            #axs[1+cnt].set_title(c)
            axs[1+cnt].plot(self.xaxis, v, label=c)
            axs[1+cnt].legend()
            cnt=cnt+1

        if output is None:
            plt.show()
        else:
            plt.savefig(output)

    def ops_done(self, ops):
        left = self.ops_total(ops)
        return left == 0

    def ops_total(self, ops):
        return sum([ uconvert(x[1]) for x in ops ])

    def write(self, ops, tick=1.0):
        # First flush caches in random order
        cl = [v for v in self.caches.values()]
        random.shuffle(cl)

        # Intialize OP write
        for op in ops:
            ln = op[0]
            size = uconvert(op[1])
            l = self.links[ln]
            l.write_init(size, tick)


        for c in cl:
            c.flush_tick(tick)


        ret = [None] * len(ops)

        # Proceed on ops in random order
        idxs = [ i for i in range(0, len(ops)) ]
        random.shuffle(idxs)

        for i in idxs:
            op = ops[i]
            ln = op[0]
            l = self.links[ln]
            written = l.write_tick(tick)
            ret[i]= written
            op[1] = "{}".format(uconvert(op[1]) - written)

        # Write DONE
        for op in ops:
            ln = op[0]
            l = self.links[ln]
            l.write_done()

        return ops, ret

    def dot(self,outpath):

        with open(outpath.as_posix(), "w") as f:
            f.write("Digraph G{\n")

            # Create cache node for all caches
            for c in self.caches.values():
                f.write("\"{}\" [label=\"{} size {} BW {}\", shape=cylinder]\n".format(c.name, c.name, rfsize(c.size), rfsize(c.bandwidth)))

            # Create input / output nodes for all links with no input / output
            # Create cache node for all caches
            for l in self.links.values():
                if not l.lin:
                    f.write("\"{}_in\" [label=\"{}\" shape=cds]\n".format(l.name, l.name))
                if not l.lout:
                    f.write("\"{}_out\" [label=\"NULL {}\"]\n".format(l.name, l.name))

            for l in self.links.values():
                if l.lin is None:
                    lin = "{}_in".format(l.name)
                else:
                    lin = l.lin.name
                if l.lout is None:
                    lout = "{}_out".format(l.name)
                else:
                    lout = l.lout.name

                f.write("\"{}\" -> \"{}\" [label=\"{} BW {}\"]\n".format(lin, lout, l.name, rfsize(l.bandwidth)))

            f.write("}\n")

    def load_ops(self, path):
        self.ops_clear()
        with open(path) as f:
            data = json.load(f)
            if not "reference" in data:
                raise Exception("{} should contain a 'reference' key".format(path))
            if not "ops" in data:
                raise Exception("{} should contain an 'ops' array".format(path))

            self.ref = data["reference"]

            if "tick" in data:
                self.tick = float(data["tick"])

            for op in data["ops"]:
                self.ops_push(op)



    def cache_state(self):
        ret = {}
        for c,v in self.caches.items():
            ret[c] = v.current
        return ret
