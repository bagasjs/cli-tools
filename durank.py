import os
from os import path

def to_pretty_size(size_in_bytes: int) -> str:
    if size_in_bytes < 1_000:
        return f"{size_in_bytes} bytes"
    if size_in_bytes < 1_000_000:
        return f"{size_in_bytes/1_000:.2f} KB"
    elif size_in_bytes < 1_000_000_000:
        return f"{size_in_bytes/1_000_000:.2f} MB"
    elif size_in_bytes < 1_000_000_000_000:
        return f"{size_in_bytes/1_000_000_000:.2f} GB"
    else:
        return f"{size_in_bytes/1_000_000_000_000:.2f} TB"

class Entry(object):
    def __init__(self, path: str, depth: int, size: int = 0, is_file: bool = False):
        self.path = path
        self.depth = depth
        self.size = size
        self.is_file = is_file

    def __str__(self):
        return f"Entry({self.path} {to_pretty_size(self.size)})"

    def __repr__(self):
        return f"Entry({self.path} {to_pretty_size(self.size)})"

class TopEntries:
    def __init__(self, N: int):
        self.N = N
        self.entries = []
    
    def update(self, entry: Entry):
        if len(self.entries) < self.N:
            self.entries.append(entry)
            self.entries = sorted(self.entries, key=lambda e: e.size, reverse=True)
        else:
            index = -1
            for i in range(self.N - 1, -1, -1):
                if self.entries[i].size < entry.size:
                    index = i
                else:
                    break

            if index >= 0:
                top_n_top, top_n_down = self.entries[:index], self.entries[index:]
                self.entries = []
                self.entries.extend(top_n_top)
                self.entries.append(entry)
                self.entries.extend(top_n_down[:-1])

    def display(self):
        for i, entry in enumerate(self.entries):
            rank = f'#{i+1}' 
            print(f"{rank:3} {to_pretty_size(entry.size):10} {entry.path}")

    def display2(self):
        for i, entry in enumerate(self.entries):
            if entry.is_file:
                print(f"#{i+1} [FILE] {entry.path} -> {to_pretty_size(entry.size)}")
            else:
                print(f"#{i+1} [FOLDER] {entry.path} -> {to_pretty_size(entry.size)}")

def show_directory_biggest_files(root: str, excluded: list[str], top_n: int = 10):
    if not path.isdir(root):
        print(f"ERROR: {root} is not a directory")

    usage = 0
    dirs = [ Entry(root, 0) ]
    top =  TopEntries(top_n)

    while len(dirs) > 0:
        dir = dirs.pop()
        if dir is None:
            continue
        try: 
            entries = os.listdir(dir.path)
            new_dirs = []
            for entry in entries:
                if entry in excluded:
                    continue
                if dir.path != root:
                    entry = os.path.join(dir.path, entry)

                if path.isdir(entry):
                    new_dirs.append(Entry(entry, dir.depth + 1))
                else:
                    try:
                        entry = Entry(entry, dir.depth + 1, path.getsize(entry), True)
                        top.update(entry)
                        usage += entry.size
                    except FileNotFoundError:
                        print(f"[WARNING] What the hell is {entry}? This will be skipped thus the ranking would be inaccurate")
            new_dirs.reverse()
            dirs.extend(new_dirs)
        except PermissionError:
            print(f"[WARNING] Skipping {dir.path} the results would be inaccurate")


    top.display()
    print(f"Total size of scanned from `{root}` is {to_pretty_size(usage)}")


if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-n", default=100, help="the amount of rank available")
    parser.add_option("--exclude", action="append", help="List of excluded entry", default=[])
    options, args = parser.parse_args()

    show_directory_biggest_files(os.getcwd(), options.exclude, top_n=int(options.n))
