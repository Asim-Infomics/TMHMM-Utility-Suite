from __future__ import annotations

import streamlit as st

from tmhmm_filter import (
    FilterResult,
    filter_by_length_only,
    filter_records,
    format_fasta,
    parse_fasta_text,
    parse_tmhmm_text,
)


st.set_page_config(page_title="TMHMM Filter", layout="wide")
st.title("TMHMM Utility Suite")
st.write("Select a module from the sidebar to run either PredHel-based filtering or length-only filtering.")


@st.cache_data(show_spinner=False)
def _parse_fasta(uploaded_bytes: bytes) -> dict:
    return parse_fasta_text(uploaded_bytes.decode("utf-8", errors="ignore"))


@st.cache_data(show_spinner=False)
def _parse_tmhmm(uploaded_bytes: bytes) -> dict:
    return parse_tmhmm_text(uploaded_bytes.decode("utf-8", errors="ignore"))


mode = st.sidebar.radio(
    "Select module",
    options=("PredHel filter", "Length filter"),
    help="Choose which type of filtering you want to run.",
)

if mode == "PredHel filter":
    st.header("PredHel-based Filtering")
    st.write("Upload the FASTA and TMHMM HTML output to remove proteins with transmembrane helices.")

    max_predhel = st.number_input(
        "Maximum allowed PredHel",
        min_value=0,
        max_value=20,
        value=0,
        help="Sequences with PredHel greater than this value will be removed.",
    )

    fasta_file = st.file_uploader(
        "FASTA file",
        type=["fasta", "fa", "faa", "txt"],
        key="predhel_fasta",
    )
    html_file = st.file_uploader(
        "TMHMM HTML file",
        type=["html", "htm"],
        key="predhel_html",
    )

    if fasta_file and html_file:
        try:
            fasta_records = _parse_fasta(fasta_file.getvalue())
            tmhmm_predictions = _parse_tmhmm(html_file.getvalue())
        except Exception as exc:  # pragma: no cover - Streamlit runtime feedback
            st.error(f"Failed to parse files: {exc}")
        else:
            result: FilterResult = filter_records(
                fasta_records,
                tmhmm_predictions,
                max_predhel=int(max_predhel),
                max_length=None,
            )
            col1, col2, col3 = st.columns(3)
            col1.metric("Total sequences", len(fasta_records))
            col2.metric("Kept", len(result.kept))
            col3.metric("Removed", len(result.removed))

            if result.missing_predictions:
                st.warning(
                    f"{len(result.missing_predictions)} sequences were not found in the TMHMM output and were kept."
                )

            filtered_fasta = format_fasta(result.kept.values())
            st.download_button(
                "Download filtered FASTA",
                data=filtered_fasta.encode("utf-8"),
                file_name="predhel_filtered.fasta",
                mime="text/plain",
            )

            if result.removed:
                removed_table = [
                    {
                        "Identifier": identifier,
                        "Length": detail.length,
                        "PredHel": detail.predhel if detail.predhel is not None else "—",
                        "Reason": detail.reason,
                    }
                    for identifier, detail in result.removed.items()
                ]
                st.subheader("Removed sequences (PredHel filter)")
                st.dataframe(removed_table, use_container_width=True)
    else:
        st.info("Upload both a FASTA file and a TMHMM HTML result to run this module.")

else:
    st.header("Length-based Filtering")
    st.write("Upload a FASTA file to keep only proteins shorter than the specified length.")

    max_length = st.number_input(
        "Maximum sequence length (keep if strictly less)",
        min_value=1,
        max_value=5000,
        value=300,
        help="Sequences with length ≥ this value will be removed.",
    )

    fasta_file = st.file_uploader(
        "FASTA file",
        type=["fasta", "fa", "faa", "txt"],
        key="length_fasta",
    )

    if fasta_file:
        try:
            fasta_records = _parse_fasta(fasta_file.getvalue())
        except Exception as exc:  # pragma: no cover
            st.error(f"Failed to parse FASTA: {exc}")
        else:
            result = filter_by_length_only(fasta_records, max_length=int(max_length))
            col1, col2, col3 = st.columns(3)
            col1.metric("Total sequences", len(fasta_records))
            col2.metric("Kept", len(result.kept))
            col3.metric("Removed", len(result.removed))

            filtered_fasta = format_fasta(result.kept.values())
            st.download_button(
                "Download length-filtered FASTA",
                data=filtered_fasta.encode("utf-8"),
                file_name="length_filtered.fasta",
                mime="text/plain",
            )

            if result.removed:
                removed_table = [
                    {
                        "Identifier": identifier,
                        "Length": detail.length,
                        "Reason": detail.reason,
                    }
                    for identifier, detail in result.removed.items()
                ]
                st.subheader("Removed sequences (length filter)")
                st.dataframe(removed_table, use_container_width=True)
    else:
        st.info("Upload a FASTA file to run the length module.")

