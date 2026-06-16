"""
nlmc_swc.py  --  Thin subprocess wrapper around NLMorphologyConverter.exe
                 for converting neuron morphology files to SWC format.

Place this file in the same directory as NLMorphologyConverter.exe.
Standard library only: subprocess, pathlib, argparse, sys.

Usage examples
--------------
Single file (output next to input with .swc extension):
    python nlmc_swc.py myCell.hoc

Single file with explicit output and overwrite:
    python nlmc_swc.py "Fast Spiking Basket cells Somogyi_1.hoc" out.swc --overwrite

Single file with morphology stats printed before conversion:
    python nlmc_swc.py myCell.asc --stats

Batch-convert all .hoc files in a folder:
    python nlmc_swc.py --batch ./Geometry/Neuron --pattern "*.hoc"

Batch with explicit output directory and per-file stats:
    python nlmc_swc.py --batch ./Geometry --out ./SWC_output --pattern "*.asc" --stats

Public API
----------
    convert_to_swc(input_path, output_path=None, exe_path=None,
                   stats=False, overwrite=False) -> str
    convert_folder(input_dir, output_dir=None, pattern="*",
                   exe_path=None, stats=False, overwrite=False) -> dict
"""

import argparse
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_EXE_NAME = "NLMorphologyConverter.exe"
_SWC_FORMAT_ARG = "SWC"
_MIN_VALID_LINES = 2       # minimum non-comment SWC data lines required
_SWC_FIELD_COUNT = 7       # id type x y z radius parent


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _default_exe():
    """Path to NLMorphologyConverter.exe sitting next to this script."""
    return Path(__file__).parent / _EXE_NAME


def _resolve_exe(exe_path):
    """Return a resolved Path to the exe; raise FileNotFoundError if absent."""
    p = Path(exe_path).resolve() if exe_path is not None else _default_exe().resolve()
    if not p.exists():
        raise FileNotFoundError(
            "NLMorphologyConverter.exe not found at: {}".format(p)
        )
    return p


def _run_subprocess(cmd, label):
    """
    Run cmd (list of str) via subprocess.run with captured output.
    No shell=True; args-as-list handles paths containing spaces correctly.
    Returns subprocess.CompletedProcess.  Raises RuntimeError on OS error.
    """
    try:
        return subprocess.run(
            [str(c) for c in cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
        )
    except OSError as exc:
        raise RuntimeError("Failed to launch {}: {}".format(label, exc)) from exc


def _captured_text(result):
    """Decode stdout + stderr from a CompletedProcess into a single string."""
    return (result.stdout + result.stderr).decode("ascii", errors="replace").strip()


def _parse_swc_line(line):
    """
    Parse one non-comment SWC data line.
    Returns (type_id, x, y, z, radius, parent) or None if the line is invalid.
    """
    fields = line.split()
    if len(fields) != _SWC_FIELD_COUNT:
        return None
    try:
        type_id = int(fields[1])
        x       = float(fields[2])
        y       = float(fields[3])
        z       = float(fields[4])
        radius  = float(fields[5])
        parent  = int(fields[6])
        return type_id, x, y, z, radius, parent
    except ValueError:
        return None


def _validate_swc(path, captured_exe_output):
    """
    Validate that path is a parseable SWC file.  Three checks:
      (a) file exists and is non-empty
      (b) the first non-comment data line has 7 correctly-typed fields
      (c) at least _MIN_VALID_LINES valid data lines exist AND
          at least one root sample (parent == -1) is present

    Raises RuntimeError (including captured exe stdout/stderr) on any failure
    so the caller can surface exactly why NLMorphologyConverter rejected the input.
    """
    p = Path(path)
    if not p.exists():
        raise RuntimeError(
            "Conversion produced no output file: {}\nExe output:\n{}".format(
                p, captured_exe_output
            )
        )
    if p.stat().st_size == 0:
        raise RuntimeError(
            "Conversion produced an empty file: {}\nExe output:\n{}".format(
                p, captured_exe_output
            )
        )

    valid_count = 0
    has_root    = False
    first_bad   = None

    with p.open("r", encoding="ascii", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parsed = _parse_swc_line(line)
            if parsed is None:
                if first_bad is None:
                    first_bad = line[:120]
                continue
            valid_count += 1
            _type_id, _x, _y, _z, _radius, parent = parsed
            if parent == -1:
                has_root = True

    if valid_count < _MIN_VALID_LINES:
        detail = ""
        if first_bad is not None:
            detail = "\nFirst unparseable line: {!r}".format(first_bad)
        raise RuntimeError(
            "SWC file has fewer than {} valid data lines (got {}).{}\n"
            "Exe output:\n{}".format(
                _MIN_VALID_LINES, valid_count, detail, captured_exe_output
            )
        )
    if not has_root:
        raise RuntimeError(
            "SWC file contains no root sample (parent == -1).\n"
            "Exe output:\n{}".format(captured_exe_output)
        )


def _ensure_ascii(path):
    """
    Guarantee the SWC file contains only 7-bit ASCII bytes.

    Design choice: STRIP non-ASCII bytes (replace with '?') and WARN rather
    than raising.  Rationale: NEURON crashes silently on non-ASCII in loaded
    morphology files, so a slightly altered but working file is safer than
    aborting an otherwise successful conversion.  The user is notified via a
    printed WARNING so they can inspect the output.
    """
    p = Path(path)
    raw = p.read_bytes()
    bad_offsets = [i for i, b in enumerate(raw) if b > 127]
    if not bad_offsets:
        return
    cleaned = bytes(b if b <= 127 else ord("?") for b in raw)
    p.write_bytes(cleaned)
    print(
        "WARNING: {} non-ASCII byte(s) found in '{}' and replaced with '?'. "
        "Verify the output is correct before use.".format(len(bad_offsets), p.name)
    )


def _query_stats(exe, input_path):
    """
    Run the exe in --stats --warnings mode on input_path.
    Returns the captured output string.
    Never raises -- stats failure is non-fatal for the conversion.
    """
    cmd = [exe, str(input_path), "--stats", "--warnings"]
    try:
        result = _run_subprocess(cmd, "stats query")
        return _captured_text(result)
    except Exception as exc:
        return "(stats query failed: {})".format(exc)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def convert_to_swc(input_path, output_path=None, exe_path=None,
                   stats=False, overwrite=False):
    """
    Convert a neuron morphology file to SWC using NLMorphologyConverter.exe.

    Format is auto-detected by the exe from the input file extension/content;
    do not specify an input format here.

    Parameters
    ----------
    input_path : str or Path
        Source morphology file (any format supported by NLMorphologyConverter).
    output_path : str or Path or None
        Destination SWC file.  Default: same directory and stem as input_path
        with the .swc extension.
    exe_path : str or Path or None
        Path to NLMorphologyConverter.exe.  Default: the copy sitting next to
        this script (Path(__file__).parent).
    stats : bool
        When True, also run --stats --warnings on the input and print the
        morphology summary before converting.  A stats failure does NOT abort
        the conversion.
    overwrite : bool
        When False (default), raise FileExistsError if the output already
        exists.

    Returns
    -------
    str
        Absolute path of the written SWC file.

    Raises
    ------
    FileNotFoundError   -- exe or input file not found
    FileExistsError     -- output exists and overwrite=False
    RuntimeError        -- exe invocation failed or output failed validation;
                          the exception message includes the exe's captured
                          stdout/stderr so the root cause is visible
    """
    inp = Path(input_path).resolve()
    if not inp.exists():
        raise FileNotFoundError("Input file not found: {}".format(inp))

    exe = _resolve_exe(exe_path)

    out = inp.with_suffix(".swc") if output_path is None else Path(output_path).resolve()

    if out.exists() and not overwrite:
        raise FileExistsError(
            "Output file already exists (pass overwrite=True to replace): {}".format(out)
        )

    # Optional stats query -- informational, non-fatal
    if stats:
        stats_text = _query_stats(exe, inp)
        print("=== Morphology stats: {} ===".format(inp.name))
        print(stats_text if stats_text else "(no output)")
        print()

    # Conversion
    cmd = [exe, str(inp), str(out), _SWC_FORMAT_ARG]
    result = _run_subprocess(cmd, _EXE_NAME)
    captured = _captured_text(result)

    # Validate output (returncode alone is not reliable for this exe -- a
    # format-detection failure may still return 0 but produce no valid SWC).
    _validate_swc(out, captured)

    # ASCII safety pass
    _ensure_ascii(out)

    return str(out)


def convert_folder(input_dir, output_dir=None, pattern="*",
                   exe_path=None, stats=False, overwrite=False):
    """
    Convert every file matching pattern in input_dir to SWC.

    One failed file does NOT abort the batch; its exception is stored in the
    returned dict so callers can inspect per-file outcomes.

    Parameters
    ----------
    input_dir : str or Path
    output_dir : str or Path or None
        Where to write output SWC files.  Default: same as input_dir.
    pattern : str
        Glob pattern applied inside input_dir (e.g. "*.hoc", "*.asc", "*").
    exe_path : str or Path or None
    stats : bool
    overwrite : bool

    Returns
    -------
    dict
        {str(input_path): str(output_path)}   on success
        {str(input_path): Exception}           on failure
        One entry per matched file.
    """
    src = Path(input_dir).resolve()
    if not src.is_dir():
        raise NotADirectoryError("Input directory not found: {}".format(src))

    dst = Path(output_dir).resolve() if output_dir is not None else src
    dst.mkdir(parents=True, exist_ok=True)

    exe = _resolve_exe(exe_path)

    candidates = sorted(p for p in src.glob(pattern) if p.is_file())
    if not candidates:
        print("No files matched pattern {!r} in {}".format(pattern, src))
        return {}

    results = {}
    for inp in candidates:
        out = dst / inp.with_suffix(".swc").name
        try:
            out_path = convert_to_swc(
                inp, out,
                exe_path=exe, stats=stats, overwrite=overwrite,
            )
            results[str(inp)] = out_path
            print("OK    {}  ->  {}".format(inp.name, Path(out_path).name))
        except Exception as exc:
            results[str(inp)] = exc
            # Print only the first line of the exception to keep batch output readable
            first_line = str(exc).splitlines()[0] if str(exc) else repr(exc)
            print("FAIL  {}  --  {}".format(inp.name, first_line))

    n_ok   = sum(1 for v in results.values() if not isinstance(v, Exception))
    n_fail = len(results) - n_ok
    print()
    print("Batch complete: {} converted, {} failed.".format(n_ok, n_fail))
    if n_fail:
        print("Failed files:")
        for k, v in results.items():
            if isinstance(v, Exception):
                print("  {}".format(Path(k).name))
                for line in str(v).splitlines()[:6]:   # cap detail at 6 lines
                    print("    {}".format(line))

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser():
    p = argparse.ArgumentParser(
        prog="nlmc_swc",
        description=(
            "Convert neuron morphology files to SWC via NLMorphologyConverter.exe.\n"
            "Format is auto-detected by the exe; do not specify an input format."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python nlmc_swc.py myCell.hoc\n"
            "  python nlmc_swc.py \"My Cell.hoc\" out.swc --overwrite\n"
            "  python nlmc_swc.py myCell.asc --stats\n"
            "  python nlmc_swc.py --batch ./Geometry --pattern \"*.hoc\"\n"
            "  python nlmc_swc.py --batch ./Geometry --out ./SWC_output --stats\n"
        ),
    )

    p.add_argument(
        "input", nargs="?",
        help="Input morphology file (single-file mode).",
    )
    p.add_argument(
        "output", nargs="?",
        help="Output SWC file (optional; default: next to input with .swc extension).",
    )
    p.add_argument(
        "--exe", metavar="PATH",
        help="Path to NLMorphologyConverter.exe "
             "(default: same folder as this script).",
    )
    p.add_argument(
        "--stats", action="store_true",
        help="Print morphology stats from the exe before converting.",
    )
    p.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite output file if it already exists.",
    )

    batch = p.add_argument_group("batch mode  (use --batch instead of INPUT)")
    batch.add_argument(
        "--batch", metavar="INPUT_DIR",
        help="Convert every matching file in INPUT_DIR.",
    )
    batch.add_argument(
        "--out", metavar="OUTPUT_DIR",
        help="Output directory for batch mode (default: same as INPUT_DIR).",
    )
    batch.add_argument(
        "--pattern", default="*", metavar="GLOB",
        help='Glob pattern for batch mode (default: "*").',
    )

    return p


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    # ---- batch mode ----
    if args.batch:
        if args.input:
            parser.error("Provide either INPUT or --batch, not both.")
        try:
            results = convert_folder(
                args.batch,
                output_dir=args.out,
                pattern=args.pattern,
                exe_path=args.exe,
                stats=args.stats,
                overwrite=args.overwrite,
            )
        except Exception as exc:
            print("ERROR: {}".format(exc), file=sys.stderr)
            sys.exit(1)
        n_fail = sum(1 for v in results.values() if isinstance(v, Exception))
        sys.exit(1 if n_fail else 0)

    # ---- single-file mode ----
    if not args.input:
        parser.error("Provide an INPUT file, or use --batch for a directory.")

    try:
        out_path = convert_to_swc(
            args.input,
            output_path=args.output,
            exe_path=args.exe,
            stats=args.stats,
            overwrite=args.overwrite,
        )
        print("Converted: {}".format(out_path))
    except Exception as exc:
        print("ERROR: {}".format(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
