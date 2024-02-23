#!/usr/bin/env python3
import sys

DEBUG = False

def find_indents(file):
    config = []
    # if we hit a comment, then multiline is true
    multiline = False
    full_line = None

    for line in file.readlines():
        line = line.rstrip()

        # find the start of a multiline comment
        if '^C' in line and not multiline:
            # we are entering a multiline
            multiline = True
            full_line = line

        # find the end of a multiline comment
        elif '^C' in line and multiline:
            # we are exiting a multi-line
            full_line = f"{full_line}\n{line}"
            multiline = False

        # in the middle of a multiline comment
        elif multiline:
            # if we are in a multiline - we append the line
            full_line = f"{full_line}\n{line}"

        # if it is not the start, middle or end of a multiline comment, then it's just a standard line
        else:
            # if we are not in a multiline, then the full line is line
            full_line = line

        if not multiline:
            indent = len(full_line) - len(full_line.lstrip(' '))
            full_line = full_line.lstrip(' ')

            if full_line.startswith('!'):
                # it's just a comment - we can ignore it
                continue

            # if it's a no command, strip the no from the line and set the action to delete
            if full_line.startswith('no'):
                action = 'delete'
                full_line = full_line.lstrip('no ')
            else:
                action = 'set'

            this_line = [indent, action, full_line]
            config.append(this_line)

    return config


def find_previous_indent(data, pointer):
    # Get the line from the data at this pointer location
    line = data[pointer]

    # Get this lines indent
    indent = line[0]

    if DEBUG:
        print("** %s " % indent)

    pointer = pointer - 1

    # Look at the previous line
    back_one_line = data[pointer]

    # if this indent is not less that the indent we are looking for, keep looking
    while not back_one_line[0] < indent:
        if DEBUG:
            print(back_one_line)

        pointer = pointer - 1
        back_one_line = data[pointer]

    # once we have found a line with a smaller indent, return it
    return pointer, back_one_line


def collect_line_components(data):
    collected_lines = []
    for i in range(len(data)):
        # Data format is ident, set/delete, config line
        this_indent = data[i][0]

        # if this indent is 10 for example, then we need to look behind for something less than 10.  we
        # keep doing that until we get to 0 and then build our line

        line_components = [data[i]]

        pointer = i
        while this_indent > 0:
            pointer, line = find_previous_indent(data, pointer)
            line_components.append(line)
            this_indent = line[0]

        line_components.reverse()
        collected_lines.append(line_components)

    return collected_lines


def create_set_delete_line(collected_lines):
    lines = []
    for components in collected_lines:
        action = 'set'
        line = ""
        # for each component, add it to the line and keep track of any changes to the actions
        for component in components:
            if component[1] is 'delete':
                action = 'delete'

            line += " " + component[2].strip()

        full_line = f"{action}{line}"
        lines.append(full_line)

    return lines


def main():
    if len(sys.argv) == 2:
        _file = open(sys.argv[1])
    else:
        _file = sys.stdin

    _data = find_indents(_file)
    _collected_lines = collect_line_components(_data)
    _as_set_delete = create_set_delete_line(_collected_lines)
    for line in _as_set_delete:
        print(line)


if __name__ == "__main__":
    main()
