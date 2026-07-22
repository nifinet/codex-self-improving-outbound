"""A tiny YAML reader so the demo runs before `pip install`.

This handles exactly the two shapes this repo uses: the nested mapping in
config/scoring.yaml and the list-of-cases in evals/fixtures.yaml. It is not a
YAML parser and it is not trying to be one. Install pyyaml and this file is
never imported.
"""


def _coerce(value):
    value = value.strip()
    if not value:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [_coerce(p) for p in inner.split(",")] if inner else []
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def load_yaml(path):
    lines = []
    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        lines.append(raw.rstrip())

    def parse_block(index, indent):
        """Return (value, next_index) for the block starting at `index`."""
        # A block of list items at this indent.
        if index < len(lines) and _indent(lines[index]) == indent and lines[index].lstrip().startswith("- "):
            items = []
            while index < len(lines) and _indent(lines[index]) == indent and lines[index].lstrip().startswith("- "):
                first = lines[index].lstrip()[2:]
                item = {}
                key, _, value = first.partition(":")
                item[key.strip()] = _coerce(value)
                index += 1
                # Remaining keys of this item are indented past the dash.
                item_indent = indent + 2
                while index < len(lines) and _indent(lines[index]) == item_indent and not lines[index].lstrip().startswith("- "):
                    k, _, v = lines[index].lstrip().partition(":")
                    item[k.strip()] = _coerce(v)
                    index += 1
                items.append(item)
            return items, index

        # Otherwise a mapping.
        mapping = {}
        while index < len(lines) and _indent(lines[index]) == indent:
            key, _, value = lines[index].lstrip().partition(":")
            key = key.strip()
            index += 1
            if _coerce(value) is None and index < len(lines) and _indent(lines[index]) > indent:
                mapping[key], index = parse_block(index, _indent(lines[index]))
            else:
                mapping[key] = _coerce(value)
        return mapping, index

    value, _ = parse_block(0, 0)
    return value
