from __future__ import annotations

import argparse
from pathlib import Path

from tmhmm_filter import filter_records, load_fasta, load_tmhmm, write_fasta


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Filter FASTA sequences by TMHMM predictions, removing proteins with "
            "transmembrane helices greater than the specified threshold."
        )
    )
    parser.add_argument("--fasta", required=True, help="Path to the FASTA file containing protein sequences.")
    parser.add_argument("--html", required=True, help="Path to the TMHMM HTML output file.")
    parser.add_argument(
        "--max-predhel",
        type=int,
        default=0,
        help="Maximum allowed PredHel count for sequences to keep (default: 0).",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=300,
        help="Keep sequences with length strictly less than this value (default: 300; use 0 to disable).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="filtered_no_transmembrane.fasta",
        help="Output FASTA path for sequences that meet the criterion.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    fasta_path = Path(args.fasta)
    html_path = Path(args.html)

    if not fasta_path.is_file():
        parser.error(f"FASTA file not found: {fasta_path}")
    if not html_path.is_file():
        parser.error(f"HTML file not found: {html_path}")

    fasta_records = load_fasta(fasta_path)
    tmhmm_predictions = load_tmhmm(html_path)

    max_length = args.max_length if args.max_length and args.max_length > 0 else None

    result = filter_records(
        fasta_records,
        tmhmm_predictions,
        max_predhel=args.max_predhel,
        max_length=max_length,
    )
    output_path = write_fasta(result.kept.values(), args.output)

    total = len(fasta_records)
    removed = len(result.removed)
    kept = len(result.kept)

    print(f"Total FASTA sequences: {total}")
    print(f"Sequences removed: {removed}")
    print(f"Sequences kept: {kept}")
    print(f"Output written to: {output_path}")

    if max_length is not None:
        print(f"Length filter applied: keep length < {max_length} amino acids.")
    else:
        print("Length filter disabled.")

    if missing := result.missing_predictions:
        print(f"Warning: {len(missing)} sequences lacked TMHMM predictions and were kept.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

