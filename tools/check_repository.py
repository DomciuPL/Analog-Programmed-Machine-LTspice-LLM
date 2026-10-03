#!/usr/bin/env python3
"""Read-only structural checks for APM-1; not an LTspice parser/simulator."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SCALED = {'MUL', 'MULPINV', 'SUMP', 'DPT', 'DAC8', 'PWM', 'WOBLIN'}
ASSIGN = re.compile(r'([A-Za-z_]\w*)\s*=\s*(\{[^}]*\}|[^\s]+)')


@dataclass
class Block:
    name: str
    pins: list[str]
    params: dict[str, str]
    location: str


def lines(path: Path):
    """Join SPICE continuation lines, retaining their original line number."""
    current = ''
    number = 0
    for n, raw in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        if raw.lstrip().startswith('+'):
            current += ' ' + raw.lstrip()[1:].split(';')[0].strip()
        else:
            if current:
                yield number, current
            current, number = raw.split(';')[0].strip(), n
    if current:
        yield number, current


def expand(path: Path, stack=()):
    path = path.resolve()
    if path in stack:
        raise ValueError('Include cycle: ' + ' -> '.join(p.name for p in (*stack, path)))
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f'Include escapes repository: {path}')
    for number, line in lines(path):
        if re.match(r'^\.(include|inc)\s', line, re.I):
            match = re.match(r'^\.(?:include|inc)\s+(?:"([^"]+)"|(\S+))\s*$', line, re.I)
            if not match:
                raise ValueError(f'{path}:{number}: malformed include')
            target = match[1] or match[2]
            yield from expand(path.parent / target.replace('\\', '/'), (*stack, path))
        else:
            yield path, number, line


def signature(line, location=''):
    prefix = re.split(r'\s+PARAMS:\s*|\s+(?=[A-Za-z_]\w*\s*=)', line, maxsplit=1, flags=re.I)[0]
    tokens = prefix.split()
    return Block(tokens[1], tokens[2:], {m[1].upper(): m[2] for m in ASSIGN.finditer(line)}, location)


def library_blocks():
    result = {}
    for filename in ('apm1_lib.txt', 'apm1_wob_lib.txt'):
        for number, line in lines(ROOT / filename):
            if line.lower().startswith('.subckt '):
                block = signature(line, f'{filename}:{number}')
                key = block.name.upper()
                if key in result:
                    raise ValueError(f'Duplicate block {block.name}')
                result[key] = block
    return result


def api_table():
    rows = ['| Blok | Piny w kolejności wywołania | Parametry domyślne |',
            '|---|---|---|']
    for block in library_blocks().values():
        params = ', '.join(f'{key}={value}' for key, value in block.params.items()) or 'brak'
        rows.append(f'| `{block.name}` | `{", ".join(block.pins)}` | `{params}` |')
    return '\n'.join(rows)


def check_deck(path: Path):
    errors = []
    expanded = list(expand(path))
    blocks = {}
    scope = None
    scope_pins = set()
    instance_names = set()
    calls = []
    measures = set()
    analyses = 0
    ends = 0
    result_begin = result_end = 0
    for source, number, line in expanded:
        location = f'{source.relative_to(ROOT)}:{number}'
        lower = line.lower()
        if 'RESULTS_BEGIN' in line:
            result_begin += 1
        if 'RESULTS_END' in line:
            result_end += 1
        if lower.startswith('.subckt '):
            if scope:
                errors.append(f'{location}: nested subcircuit is outside this checker contract')
            block = signature(line, location)
            scope = block.name.upper()
            scope_pins = {pin.upper() for pin in block.pins}
            if scope in blocks:
                errors.append(f'{location}: duplicate subcircuit {scope}')
            blocks[scope] = block
        elif lower.startswith('.ends'):
            if not scope or (len(line.split()) > 1 and line.split()[1].upper() != scope):
                errors.append(f'{location}: mismatched .ends')
            scope, scope_pins = None, set()
        elif not line.startswith(('*', '.', '+')):
            name = line.split()[0].upper()
            identity = (scope, name)
            if identity in instance_names:
                errors.append(f'{location}: duplicate instance {name} in {scope or "top"}')
            instance_names.add(identity)
            if name.startswith('X'):
                prefix = re.split(r'\s+PARAMS:\s*|\s+(?=[A-Za-z_]\w*\s*=)', line, maxsplit=1, flags=re.I)[0]
                tokens = prefix.split()
                calls.append((location, tokens[-1].upper(), tokens[1:-1],
                              {m[1].upper(): m[2] for m in ASSIGN.finditer(line)}, scope, scope_pins.copy()))
        if not scope:
            if lower.startswith('.tran '):
                analyses += 1
            if lower == '.end':
                ends += 1
            if lower.startswith('.meas '):
                name = line.split()[2].lower()
                if name in measures:
                    errors.append(f'{location}: duplicate measurement {name}')
                measures.add(name)
    if scope:
        errors.append(f'{path.name}: unclosed subcircuit {scope}')
    for location, name, pins, params, parent, formal_pins in calls:
        if name not in blocks:
            errors.append(f'{location}: unknown block {name}')
            continue
        block = blocks[name]
        if len(pins) != len(block.pins):
            errors.append(f'{location}: {name}: {len(pins)} pins, expected {len(block.pins)}')
        elif pins[-1].upper() != ('GDN' if parent else '0'):
            errors.append(f'{location}: computational ground must be {"GDN" if parent else "0"}')
        for param in params.keys() - block.params.keys():
            errors.append(f'{location}: unknown parameter {name}.{param}')
        if name in SCALED and 'VL' not in params:
            errors.append(f'{location}: explicitly forward VL to {name}')
        if name == 'DIF' and params.get('LEAK', '0') not in ('0', '{0}'):
            errors.append(f'{location}: DIF.leak is deprecated; use tau for filtering')
    if analyses != 1 or ends != 1:
        errors.append(f'{path.name}: expected one .tran and one .end after includes; got {analyses}, {ends}')
    if result_begin != 1 or result_end != 1 or not measures:
        errors.append(f'{path.name}: expected one RESULTS block with measurements')
    return errors, measures


def check_markdown(path):
    text = path.read_text(encoding='utf-8')
    errors = []
    if sum(bool(re.match(r'^\s*```', line)) for line in text.splitlines()) % 2:
        errors.append(f'{path.relative_to(ROOT)}: unclosed code fence')
    for match in re.finditer(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', text):
        target = match[1].split('#')[0]
        if not target or re.match(r'\w+://', target):
            continue
        if not (path.parent / unquote(target)).exists():
            errors.append(f'{path.relative_to(ROOT)}: broken local link {target}')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-api', action='store_true', help='Refresh the generated API table only')
    args = parser.parse_args(argv)
    reference = ROOT / 'docs/reference_pl.md'
    begin, end = '<!-- BEGIN GENERATED API -->', '<!-- END GENERATED API -->'
    text = reference.read_text(encoding='utf-8')
    expected = begin + '\n' + api_table() + '\n' + end
    actual = re.search(re.escape(begin) + r'[\s\S]*?' + re.escape(end), text)
    if args.write_api:
        if not actual:
            parser.error('Missing API markers')
        reference.write_text(text[:actual.start()] + expected + text[actual.end():], encoding='utf-8')
        return 0
    errors = []
    if not actual or actual[0] != expected:
        errors.append('API table differs from .subckt signatures; run --write-api')
    decks = sorted([*ROOT.glob('*.cir'), *ROOT.glob('examples/*.cir'), *ROOT.glob('tests/*.cir')])
    measurement_sets = {}
    for deck in decks:
        try:
            deck_errors, measurements = check_deck(deck)
            errors.extend(deck_errors)
            measurement_sets[deck.relative_to(ROOT).as_posix()] = measurements
        except (OSError, ValueError, IndexError) as exc:
            errors.append(f'{deck.name}: {exc}')
    for path in [ROOT / 'README.md', *ROOT.glob('docs/**/*.md'), ROOT / 'examples/README.md']:
        errors.extend(check_markdown(path))
    manifest = json.loads((ROOT / 'tests/acceptance.json').read_text())
    for case in manifest['cases']:
        present = measurement_sets.get(case['path'], set())
        if not present:
            errors.append(f"Acceptance case missing: {case['path']}")
        for measurement in case['limits']:
            if measurement.lower() not in present:
                errors.append(f"{case['path']}: acceptance measurement {measurement} is missing")
    if errors:
        print('\n'.join('ERROR: ' + error for error in errors))
        return 1
    print(f'Structure OK: {len(library_blocks())} blocks, {len(decks)} netlist entry points, documentation links and acceptance declarations.')
    print('LTspice syntax, convergence and measured numerical results are NOT verified by this command.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
