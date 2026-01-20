from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True)
class FastaRecord:
    """Container for a FASTA entry."""

    identifier: str
    header: str
    sequence: str


@dataclass(frozen=True)
class FilterResult:
    """Result of filtering FASTA records by TMHMM predictions."""

    kept: OrderedDict[str, FastaRecord]
    removed: OrderedDict[str, "RemovalDetail"]
    missing_predictions: tuple[str, ...]


@dataclass(frozen=True)
class RemovalDetail:
    record: FastaRecord
    reason: str
    predhel: int | None
    length: int


FASTA_LINE_WRAP = 60
TMHMM_LINE_PATTERN = re.compile(r"^(?P<id>\S+).*?\bPredHel=(?P<count>\d+)")


def parse_fasta_text(text: str) -> OrderedDict[str, FastaRecord]:
    """Parse FASTA text into an ordered mapping of identifier -> record."""
    records: "OrderedDict[str, FastaRecord]" = OrderedDict()
    header: str | None = None
    seq_chunks: list[str] = []

    def flush_record() -> None:
        nonlocal header, seq_chunks
        if header is None:
            return
        identifier = header.split()[0]
        sequence = "".join(seq_chunks).replace(" ", "").replace("\r", "")
        records[identifier] = FastaRecord(identifier=identifier, header=header, sequence=sequence)
        header = None
        seq_chunks = []

    for line in text.splitlines():
        if not line:
            continue
        if line.startswith(">"):
            flush_record()
            header = line[1:].strip()
        else:
            seq_chunks.append(line.strip())

    flush_record()
    return records


def parse_tmhmm_text(text: str) -> dict[str, int]:
    """Parse TMHMM HTML/plain text into mapping of identifier -> PredHel count."""
    predictions: dict[str, int] = {}
    for line in text.splitlines():
        match = TMHMM_LINE_PATTERN.search(line)
        if not match:
            continue
        identifier = match.group("id")
        count = int(match.group("count"))
        predictions[identifier] = count
    return predictions


def filter_records(
    fasta_records: Mapping[str, FastaRecord],
    tmhmm_predictions: Mapping[str, int],
    max_predhel: int = 0,
    max_length: int | None = None,
) -> FilterResult:
    """Split FASTA records based on TMHMM PredHel and length thresholds."""
    kept: "OrderedDict[str, FastaRecord]" = OrderedDict()
    removed: "OrderedDict[str, RemovalDetail]" = OrderedDict()
    missing: list[str] = []

    for identifier, record in fasta_records.items():
        predhel = tmhmm_predictions.get(identifier)
        length = len(record.sequence)
        length_ok = max_length is None or length < max_length
        predhel_ok = predhel is None or predhel <= max_predhel

        if predhel is None:
            missing.append(identifier)

        if predhel_ok and length_ok:
            kept[identifier] = record
        else:
            reasons = []
            if not predhel_ok:
                reasons.append(f"PredHel>{max_predhel}")
            if not length_ok and max_length is not None:
                reasons.append(f"Length≥{max_length}")
            removed[identifier] = RemovalDetail(
                record=record,
                reason=", ".join(reasons) if reasons else "Filtered",
                predhel=predhel,
                length=length,
            )

    return FilterResult(kept=kept, removed=removed, missing_predictions=tuple(missing))


def format_fasta(records: Iterable[FastaRecord]) -> str:
    """Format FASTA records into text."""
    lines: list[str] = []
    for record in records:
        lines.append(f">{record.header}")
        seq = record.sequence
        for start in range(0, len(seq), FASTA_LINE_WRAP):
            lines.append(seq[start : start + FASTA_LINE_WRAP])
    return "\n".join(lines) + ("\n" if lines else "")


def write_fasta(records: Iterable[FastaRecord], output_path: str | Path) -> Path:
    """Write FASTA records to disk."""
    output = Path(output_path)
    output.write_text(format_fasta(records))
    return output


def load_fasta(path: str | Path) -> OrderedDict[str, FastaRecord]:
    """Load a FASTA file from disk."""
    text = Path(path).read_text()
    return parse_fasta_text(text)


def load_tmhmm(path: str | Path) -> dict[str, int]:
    """Load TMHMM results (HTML/plain text) from disk."""
    text = Path(path).read_text()
    return parse_tmhmm_text(text)


def filter_by_length_only(
    fasta_records: Mapping[str, FastaRecord],
    max_length: int,
) -> FilterResult:
    """Filter FASTA records by length only."""
    kept: "OrderedDict[str, FastaRecord]" = OrderedDict()
    removed: "OrderedDict[str, RemovalDetail]" = OrderedDict()

    for identifier, record in fasta_records.items():
        length = len(record.sequence)
        if length < max_length:
            kept[identifier] = record
        else:
            removed[identifier] = RemovalDetail(
                record=record,
                reason=f"Length≥{max_length}",
                predhel=None,
                length=length,
            )

    return FilterResult(kept=kept, removed=removed, missing_predictions=())

