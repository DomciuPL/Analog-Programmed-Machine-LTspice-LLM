#!/usr/bin/env python3
"""Run the declared LTspice cases, retaining logs and strict acceptance results."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NUMBER = r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'


def parse_log(text):
    """Read scalar measurements and LTspice's per-measurement step tables."""
    values = {}
    table = None
    for line in text.splitlines():
        match = re.match(r'\s*Measurement:\s*(\S+)\s*$', line, re.I)
        if match:
            table = match[1].lower()
            values.setdefault(table, [])
            continue
        if table:
            match = re.match(r'\s*\d+\s+(' + NUMBER + r')(?:\s|$)', line)
            if match:
                values[table].append(float(match[1]))
                continue
        match = re.match(r'^\s*([A-Za-z_]\w*)\s*(?::[^\n]*?=|=)\s*(' + NUMBER + r')(?:\s|$)', line)
        if match:
            table = None
            values.setdefault(match[1].lower(), []).append(float(match[2]))
    return values


def acceptance(case, values):
    errors = []
    for name, limit in case['limits'].items():
        samples = values.get(name.lower(), [])
        if len(samples) != case['runs']:
            errors.append(f'{name}: got {len(samples)} results, expected {case["runs"]}')
            continue
        for step, value in enumerate(samples, 1):
            lo, hi = limit
            if not math.isfinite(value) or not lo <= value <= hi:
                errors.append(f'{name}, run {step}: {value} outside [{lo}, {hi}]')
    return errors


def read_log(path):
    data = path.read_bytes()
    if data.startswith((b'\xff\xfe', b'\xfe\xff')) or b'\x00' in data[:200]:
        return data.decode('utf-16')
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError:
        return data.decode('cp1252')


def find_executable(explicit):
    if explicit:
        candidate = Path(explicit).expanduser()
        return str(candidate.resolve()) if candidate.is_file() else shutil.which(explicit)
    for candidate in ('LTspice.exe', 'XVIIx64.exe', 'ltspice'):
        found = shutil.which(candidate)
        if found:
            return found
    candidates = []
    if os.environ.get('LOCALAPPDATA'):
        candidates.append(Path(os.environ['LOCALAPPDATA']) / 'Programs/ADI/LTspice/LTspice.exe')
    if os.environ.get('ProgramFiles'):
        candidates += [Path(os.environ['ProgramFiles']) / 'ADI/LTspice/LTspice.exe',
                       Path(os.environ['ProgramFiles']) / 'LTC/LTspiceXVII/XVIIx64.exe']
    return next((str(path) for path in candidates if path.is_file()), None)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', help='Full path to the LTspice executable')
    parser.add_argument('--suite', choices=('core', 'all'), default='core')
    parser.add_argument('--timeout', type=float, default=300, help='Seconds per case')
    parser.add_argument('--version-note', default='not supplied', help='Exact LTspice version from Help/About')
    parser.add_argument('--list', action='store_true', help='List cases without running')
    args = parser.parse_args(argv)
    manifest = json.loads((ROOT / 'tests/acceptance.json').read_text(encoding='utf-8'))
    cases = [case for case in manifest['cases'] if args.suite == 'all' or case['suite'] == 'core']
    if args.list:
        for case in cases:
            print(f"{case['path']} ({case['runs']} runs)")
        return 0
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    exe = find_executable(args.exe)
    if not exe:
        print('LTspice not found. Supply --exe with the actual executable path. No simulations were performed.', file=sys.stderr)
        return 2
    destination = ROOT / 'build/ltspice'
    destination.mkdir(parents=True, exist_ok=True)
    report = {'created_utc': datetime.now(timezone.utc).isoformat(), 'executable': exe,
              'version_note': args.version_note, 'suite': args.suite, 'cases': []}
    with tempfile.TemporaryDirectory(prefix='apm1-', dir=ROOT / 'build') as temporary:
        staged = Path(temporary)
        sources = [ROOT / 'apm1_lib.txt', ROOT / 'apm1_wob_lib.txt',
                   *ROOT.glob('*.cir'), *ROOT.glob('examples/*.cir'), *ROOT.glob('tests/*.cir')]
        for path in sources:
            target = staged / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        for case in cases:
            deck = staged / case['path']
            command = [exe, '-b', str(deck)]
            errors = []
            output = ''
            returncode = None
            try:
                result = subprocess.run(command, cwd=deck.parent, capture_output=True,
                                        timeout=args.timeout, text=True, errors='replace')
                returncode = result.returncode
                output = result.stdout + result.stderr
                if returncode != 0:
                    errors.append(f'LTspice process exited with {returncode}')
            except subprocess.TimeoutExpired:
                errors.append(f'Timeout after {args.timeout}s')
            except OSError as exc:
                errors.append(str(exc))
            log = deck.with_suffix('.log')
            values = {}
            if log.is_file():
                log_text = read_log(log)
                shutil.copyfile(log, destination / (deck.stem + '.log'))
                if re.search(r'fatal error|time ?step too small|singular matrix|unknown subcircuit|undefined symbol|measurement[^\n]*failed|error on line', log_text, re.I):
                    errors.append('LTspice log reports a simulation or measurement error')
                values = parse_log(log_text)
                errors.extend(acceptance(case, values))
            else:
                errors.append('Fresh .log file was not produced')
            (destination / (deck.stem + '.stdout.txt')).write_text(output, encoding='utf-8')
            record = {'path': case['path'], 'command': command, 'returncode': returncode,
                      'passed': not errors, 'errors': errors, 'measurements': values}
            report['cases'].append(record)
            print(('PASS ' if not errors else 'FAIL ') + case['path'], flush=True)
            for error in errors:
                print('  ' + error, flush=True)
    report['passed'] = all(case['passed'] for case in report['cases'])
    (destination / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
