"""Check saved physical BReps from one immutable Git revision using OCC BOP checks.

The snapshot is opened without recompute or save. This detects geometric
defects missed by the basic isValid() check; it does not measure hardware.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.environ.get('PATH_TO_FREECAD_LIBDIR', ''))
import FreeCAD as App
import Part
import Sketcher

ROOT = Path(__file__).resolve().parents[1]


def git(*arguments):
    return subprocess.check_output(['git', '-C', str(ROOT), *arguments])


def worker(connection):
    while True:
        try:
            data = connection.recv()
        except EOFError:
            return
        if data is None:
            return
        try:
            shape = Part.Shape()
            shape.importBrepFromString(data)
            shape.check(True)
            connection.send({'status': 'passed'})
        except Exception as error:
            connection.send({'status': 'failed', 'error': str(error)})


class BoundedChecker:
    def __init__(self, timeout):
        self.timeout = timeout
        self.process = None
        self.connection = None

    def start(self):
        context = mp.get_context('spawn')
        self.connection, child = context.Pipe()
        self.process = context.Process(target=worker, args=(child,))
        self.process.start()
        child.close()

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            self.process.join(timeout=2)
            if self.process.is_alive():
                self.process.kill()
                self.process.join(timeout=2)
            self.process = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def check(self, shape):
        if self.process is None:
            self.start()
        try:
            self.connection.send(shape.exportBrepToString())
            if self.connection.poll(self.timeout):
                return self.connection.recv()
            self.stop()
            return {'status': 'timeout', 'error': 'Strict BOP check exceeded %.1f seconds; not accepted as passed' % self.timeout}
        except (EOFError, BrokenPipeError, OSError) as error:
            self.stop()
            return {'status': 'worker_error', 'error': str(error)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('devices', nargs='*')
    parser.add_argument('--commit', default='HEAD')
    parser.add_argument('--timeout', type=float, default=20)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('Timeout must be positive')
    commit = git('rev-parse', args.commit).decode().strip()
    catalog = json.loads(git('show', commit + ':site/src/catalog.json'))
    unknown = set(args.devices) - {row['id'] for row in catalog}
    if unknown:
        parser.error('Unknown device IDs: ' + ', '.join(sorted(unknown)))
    selected = [row for row in catalog if not args.devices or row['id'] in args.devices]
    report = dict(commit=commit, complete=False,
                  method='Read-only saved BRep Shape.check(True) in a bounded subprocess; immutable Git snapshot',
                  timeout_seconds_per_component=args.timeout, factory_equivalence_verified=False, devices=[])
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def persist():
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    checker = BoundedChecker(args.timeout)
    try:
        with tempfile.TemporaryDirectory(prefix='cad-strict-') as temp:
            for entry in selected:
                started = time.time()
                source = 'devices/%s/output/%s_Complete.FCStd' % (entry['id'], entry['prefix'])
                payload = git('show', commit + ':' + source)
                path = Path(temp) / (entry['prefix'] + '_Complete.FCStd')
                path.write_bytes(payload)
                row = dict(device=entry['id'], source=source, source_sha256=hashlib.sha256(payload).hexdigest(),
                           complete=False, attempted=0, completed_checks=0, errors=[])
                report['devices'].append(row)
                doc = None
                try:
                    doc = App.openDocument(str(path))
                    parts = [o for o in doc.Objects if getattr(o, 'PhysicalPart', False)]
                    row['physical_components'] = len(parts)
                    if not parts:
                        raise ValueError('No traced physical parts')
                    for obj in parts:
                        row['current_part'] = obj.PartID
                        persist()
                        if obj.Shape.isNull() or not obj.Shape.Solids:
                            result = {'status': 'failed', 'error': 'Null or non-solid physical component'}
                        else:
                            result = checker.check(obj.Shape)
                        if result['status'] in ('passed', 'failed'):
                            row['completed_checks'] += 1
                        if result['status'] != 'passed':
                            row['errors'].append(dict(part_id=obj.PartID, name=obj.Name, **result))
                        row['attempted'] += 1
                        row['elapsed_seconds'] = time.time() - started
                    row.pop('current_part', None)
                    row.update(complete=True, passed=not row['errors'], elapsed_seconds=time.time()-started)
                except Exception as error:
                    row['load_error'] = str(error)
                    row.update(complete=True, passed=False)
                finally:
                    if doc is not None:
                        App.closeDocument(doc.Name)
                    path.unlink(missing_ok=True)
                persist()
                print(json.dumps({key: value for key, value in row.items() if key != 'errors'} | {'error_count': len(row['errors'])}), flush=True)
    finally:
        checker.stop()
    report.update(complete=True, passed=all(row['passed'] for row in report['devices']))
    persist()
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
