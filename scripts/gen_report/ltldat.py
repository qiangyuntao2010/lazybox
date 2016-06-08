#!/usr/bin/env python

"Module for little data processing"

import math

class ATable:
    title = None    # string
    legend = None   # list of strings
    rows = None     # list of dicts[column name: value]

    def __init__(self, title, legend, rows):
        """received `rows` is list of list."""
        self.title = title
        self.legend = legend
        self.rows = []
        for row in rows:
            self.rows.append({legend[i]: row[i] for i in range(len(legend))})

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        str_ = "title: %s\n" % self.title
        str_ += "%s" % self.legend + "\n"
        for row in self.rows:
            str_ += "%s\n" % [row[cname] for cname in self.legend]
        return str_

    def item_at(self, row, col):
        return self.rows[row][col]

    def update_at(self, row, col, val):
        self.rows[row][col] = val

    def nr_rows(self):
        return len(self.rows)

    def remove_row(self, idx):
        del self.rows[idx]

    def replace_legend(self, oldlegend, newlegend):
        for idx, name in enumerate(self.legend):
            if name == oldlegend:
                self.legend[idx] = newlegend
        for row in self.rows:
            row[newlegend] = row.pop(oldlegend)
        return self

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def append_column(self, col_name, generator):
        self.legend.append(col_name)
        for idx in range(len(self.rows)):
            self.rows[idx][col_name] = generator(idx)
        return self

    def convert_column(self, col_name, converter):
        for idx in range(len(self.rows)):
            self.rows[idx][col_name] = converter(idx)
        return self

    def csv(self):
        lines = []
        lines.append("title, %s" % self.title)
        lines.append(", ".join(str(x) for x in self.legend))
        for row in self.rows:
            lines.append(", ".join(
                [str(row[cname]) for cname in self.legend]))
        return '\n'.join(lines)

def from_csv(csv):
    """Parse csv text and construct a table."""
    lines = csv.split('\n')
    title = lines[0].split(',')[1].strip()
    legend = [x.strip() for x in lines[1].split(',')]
    rows = []
    for line in lines[2:]:
        rows.append([x.strip() for x in line.split(',')])
    return ATable(title, legend, rows)

def pick_fields(table, fields):
    """Reconstruct table with selected fields only"""
    new_rows = []
    for row in table.rows:
        new_rows.append([row[col] for col in fields])
    return ATable(table.title, fields, new_rows)

def merge(tables):
    """Merge multiple tables into one tables.

    Tables should have same legend and same number of rows.  If tables have
    differenct number of rows, compensate() function may be helpful.
    Each name of tables should be unique.
    """
    new_legend = []
    for table in tables:
        for name in table.legend:
            new_legend.append('-'.join([table.title, name]))
    new_rows = []

    for idx, table in enumerate(tables):
        for ridx, row in enumerate(table.rows):
            if idx == 0:
                new_rows.append([])
            new_rows[ridx].extend([row[col] for col in tables[0].legend])
    return ATable('-'.join([table.title for table in tables]),
            new_legend, new_rows)

def merge_vertical(tables):
    """Merge multiple tables into one tables vertically.

    Tables should have same legend.  If not, consider to use
    `compensate_columns()` first."""
    new_rows = []
    if len(tables) < 1:
        return None

    for table in tables:
        for row in table.rows:
            new_rows.append([row[col] for col in tables[0].legend])
    return ATable('-'.join([table.title for table in tables]),
            tables[0].legend, new_rows)

def split_with_key(table, keys):
    """Split a table into multiple tables with same keys.

    Title of each splitted tables will be the key.
    """
    inter_map = {}
    for row in table.rows:
        key = '-'.join([str(row[key]) for key in keys])
        if not inter_map.has_key(key):
            inter_map[key] = ATable(key, table.legend, [])
        inter_map[key].rows.append(row)
    return inter_map.values()

def __calc_stat(vals):
    minv = min(vals)
    maxv = max(vals)
    avg = sum(vals) / len(vals)
    variance = float(sum([pow(v - avg, 2) for v in vals])) / len(vals)
    stdev_ = math.sqrt(variance)
    return [minv, maxv, avg, stdev_, len(vals)]

def default_exclude_fn(col, val):
    return False

def calc_stat(table, keys, exclude_fn = default_exclude_fn):
    """Get average, min/max values, standard deviation of values in a table
    with same keys.
    """
    new_legend = []
    suffixes = ["_min", "_max", "_avg", "_stdev", "_nr_samples"]
    for name in table.legend:
        new_legend.extend([name + suffix for suffix in suffixes])

    new_rows = []
    ret = ATable(table.title, new_legend, [])

    tables = split_with_key(table, keys)
    for subtable in tables:
        new_row = []
        new_rows.append(new_row)
        for col in subtable.legend:
            try:
                vals = [float(row[col]) for row in subtable.rows
                        if not exclude_fn(col, row[col])]
            except ValueError:
                val = subtable.rows[0][col]
                new_row.extend([val, val, val, val, len(vals)])
                continue
            new_row.extend(__calc_stat(vals))
    return ATable(table.title, new_legend, new_rows)

def sort_with(tables, keys):
    for key in reversed(keys):
        tables.rows.sort(key=lambda x: x[key])
    return tables

def compensate(tables, key_col, default_val):
    """Compensate tables to have same keys.

    Rows in tables should be sorted by the key."""
    total_keys = []
    for table in tables:
        for row in table.rows:
            key = row[key_col]
            if not key in total_keys:
                total_keys.append(key)
    total_keys.sort()
    for table in tables:
        for idx, key in enumerate(total_keys):
            if len(table.rows) <= idx or table.rows[idx][key_col] != key:
                new_row = {col: default_val for col in table.legend}
                new_row[key_col] = key
                table.rows.insert(idx, new_row)

def compensate_columns(tables, default_val):
    """Compensate tables to have same columns."""
    unified_legend = []
    for table in tables:
        for name in table.legend:
            if not name in unified_legend:
                unified_legend.append(name)
    for table in tables:
        for name in unified_legend:
            if name in table.legend:
                continue
            for row in table.rows:
                row[name] = default_val
        table.legend = unified_legend
    return tables

if __name__ == "__main__":
    t = ATable("foo", ["key", "val", "something"],
            [
                [1, 1, 'a'], [1, 3, 'a'], [1, 5, 'a'],
                [2, 3, 'b'], [2,4,'b'], [2,5,'b'], [3, 5, 'c']])
    stat_calced = calc_stat(t, ["key"])
    sorted_ = sort_with(stat_calced, ["key_avg"])
    print t
    print sorted_
    print sorted_.csv()
    print from_csv(sorted_.csv())
    print sort_with(calc_stat(from_csv(t.csv()), ["key"]), ["key_avg"])

    t = ATable("foo", ["thrs", "system", "value1", "value2"], [
                [1, 'A', 10, 90],
                [2, 'A', 20, 80],
                [4, 'A', 30, 70],
                [1, 'B', 40, 60],
                [2, 'B', 50, 50],
                [4, 'B', 60, 40],
                [1, 'sys', 70, 30],
                [2, 'sys', 80, 20],
                [4, "sys", 90, 10],
            ])
    splits = split_with_key(t, ["system"])
    print merge(splits)
    print pick_fields(merge(splits).replace_legend("A-thrs", "thrs"),
            ["thrs", "A-value1", "B-value1", "A-value2", "B-value2"])

    t2 = t.append_column("avg", lambda x:
                        t.item_at(x, "value1") + t.item_at(x, "value2") / 2)
    print t2

    t = ATable("foo", ["key", "val"], [[1, 3], [3, 5], [5, 7]])
    t2 = ATable("bar", ["key", "val"], [[1, 3], [2, 4], [5, 7]])
    print t
    print t2
    compensate([t, t2], "key", -1)
    print "compensated"
    print t
    print t2

    t = ATable("foo", ["key", "val"], [[1, 3], [3, 5]])
    t.convert_column("key", lambda r: str(t.item_at(r, "val")))
    print t

    t = ATable("foo", ["key", "val"], [[1, 3], [2, 4]])
    t2 = ATable("foo2", ["key", "val"], [[3,3], [4,8]])
    print merge_vertical([t, t2])


    t3 = ATable("fooo", ["key", "val2"], [[3,4], [4,5]])
    compensate_columns([t, t3], -1)
    print "column compensated"
    print t
    print t3