# streamlit_merge_fasta_header_duplicates.py

import streamlit as st

st.set_page_config(page_title="FASTA Merger with Header Duplicate Report", layout="centered")
st.title("Combine FASTA Files with Header-Based Duplicate Analysis")

st.markdown("""
Upload your FASTA files (apoplastic, cytoplasmic, or dual-localized).  
The app will combine them into one FASTA file and check for duplicates **based on headers** (the text after `>`), ignoring sequence content.
""")

# File uploader
uploaded_files = st.file_uploader(
    "Upload FASTA files", 
    type=["fasta", "fa", "txt"], 
    accept_multiple_files=True
)

def read_fasta(file):
    """Reads sequences from an uploaded FASTA file."""
    sequences = []
    content = file.getvalue().decode("utf-8")
    lines = content.splitlines()
    header, seq = "", ""
    for line in lines:
        if line.startswith(">"):
            if header:
                sequences.append((header, seq))
            header = line
            seq = ""
        else:
            seq += line.strip()
    if header:
        sequences.append((header, seq))
    return sequences

if uploaded_files:
    all_sequences = []
    header_set = set()  # To detect header duplicates
    duplicate_count_total = 0
    file_duplicate_report = {}

    for file in uploaded_files:
        seqs = read_fasta(file)
        duplicates_in_file = 0
        for header, seq in seqs:
            if header in header_set:
                duplicate_count_total += 1
                duplicates_in_file += 1
            else:
                header_set.add(header)
                all_sequences.append((header, seq))
        file_duplicate_report[file.name] = duplicates_in_file
        st.success(f"Loaded {len(seqs)} sequences from {file.name} ({duplicates_in_file} duplicate headers)")

    st.write(f"**Total sequences combined (after removing duplicate headers): {len(all_sequences)}**")
    st.write(f"**Total duplicate headers found across all files: {duplicate_count_total}**")

    st.write("### Duplicate Header Report per File:")
    for fname, dup_count in file_duplicate_report.items():
        st.write(f"- {fname}: {dup_count} duplicate header(s)")

    st.info("**Note:** Duplicates are predicted by **header identity** (the text after `>`), sequences are ignored.")

    # Create combined FASTA content
    combined_fasta = ""
    for header, seq in all_sequences:
        combined_fasta += f"{header}\n{seq}\n"

    # Download button
    st.download_button(
        label="Download Combined FASTA",
        data=combined_fasta,
        file_name="combined_effectors.fasta",
        mime="text/plain"
    )

else:
    st.info("Please upload at least one FASTA file to combine.")
