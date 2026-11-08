"""Allocate component numbers without recycling retired identities."""
import re


def allocate_part_numbers(existing, prefix, preserve=False, reserved=()):
    if not preserve:
        return [prefix + f'-{i:04d}' for i in range(1, len(existing) + 1)]
    pattern = re.compile(re.escape(prefix) + r'-(\d{4,})')
    used = set()
    maximum = 0
    for number in [*reserved, *(x for x in existing if x)]:
        match = pattern.fullmatch(number)
        if not match or int(match[1]) < 1:
            raise ValueError('Invalid retained part number: ' + str(number))
        if number in used:
            raise ValueError('Duplicate retained or retired part number: ' + number)
        used.add(number)
        maximum = max(maximum, int(match[1]))
    assigned = []
    for number in existing:
        if not number:
            maximum += 1
            number = prefix + f'-{maximum:04d}'
        assigned.append(number)
    return assigned
