#!/usr/bin/env python

"Module for numbers processing for report"

import math

class Numbers:
    title = None    # string
    legend = None   # list of strings
    rows = None     # list of lists of strings

    def __init__(self, title, legend, rows):
        self.title = title
        self.legend = legend
        self.rows = rows

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        str_ = "title: %s\n" % self.title
        str_ += "%s" % self.legend + "\n"
        for row in self.rows:
            str_ += "%s" % row + "\n"
        return str_

    def csv(self):
        lines = []
        lines.append("title,%s" % self.title)
        lines.append(",".join(str(x) for x in self.legend))
        for row in self.rows:
            lines.append(",".join(str(x) for x in row))
        return '\n'.join(lines)

def from_csv(csv):
    lines = csv.split('\n')
    title = lines[0].split(',')[1]
    legend = lines[1].split(',')
    rows = []
    for line in lines[2:]:
        rows.append([float(x) for x in line.split(',')])
    return Numbers(title, legend, rows)

def keyindexs(legend, keys):
    kidxs = []
    for k in keys:
        for idx, name in enumerate(legend):
            if k == name:
                kidxs.append(idx)
    return kidxs

def nr_split(numbers, keys):
    """Split numbers into multiple numbers with same keys.

    Title of splitted numbers will be the keys.
    """
    kidxs = keyindexs(numbers.legend, keys)

    inter_map = {}
    for row in numbers.rows:
        key = "%s" % [row[idx] for idx in kidxs]
        if not inter_map.has_key(key):
            inter_map[key] = Numbers(key, numbers.legend, [])
        inter_map[key].rows.append(row)
    return inter_map.values()

def stat_of(numbers, keys):
    """Get average, min/max values, standard deviation of numbers with same
    keys.
    """
    new_legend = []
    for name in numbers.legend:
        new_legend.extend([name + "_min", name + "_max", name + "_avg",
                            name + "_stdev"])

    ret = Numbers(numbers.title, new_legend, [])

    nrs = nr_split(numbers, keys)
    for nr in nrs:
        new_row = []
        ret.rows.append(new_row)
        for i in range(len(numbers.legend)):
            vals = [row[i] for row in nr.rows]
            minv = min(vals)
            maxv = max(vals)
            avg = sum(vals) / len(vals)
            variance = float(sum([pow(v - avg, 2) for v in vals])) / len(vals)
            stdev_ = math.sqrt(variance)
            new_row.extend([minv, maxv, avg, stdev_])
    return ret

def sort_with(numbers, keys):
    kidxs = keyindexs(numbers.legend, keys)
    for i in reversed(kidxs):
        numbers.rows.sort(key=lambda x: x[i])
    return numbers

if __name__ == "__main__":
    n = Numbers("foo", ["key", "val"], [[1, 1], [1, 3], [1, 5],
                                        [2, 3], [2,4], [2,5], [3, 5]])
    nrs = nr_split(n, ["key"])
    for nr in nrs:
        print nr
    n = sort_with(stat_of(n, ["key"]), ["key_avg"])
    print n
    print n.csv()
    print ""
    print from_csv(n.csv())
