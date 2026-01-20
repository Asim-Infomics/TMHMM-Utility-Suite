# TMHMM Utility Suite

A comprehensive Python toolkit for filtering FASTA protein sequences based on TMHMM (Transmembrane Hidden Markov Model) predictions. This suite provides both web-based and command-line interfaces for removing proteins with transmembrane helices and filtering sequences by length.

## Features

- **PredHel-based Filtering**: Remove proteins with transmembrane helices based on TMHMM PredHel predictions
- **Length-based Filtering**: Filter sequences by maximum length threshold
- **FASTA File Merging**: Combine multiple FASTA files with duplicate header detection
- **Web Interface**: User-friendly Streamlit web application
- **Command-Line Interface**: Scriptable CLI tool for batch processing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/TMHMM.git
   cd TMHMM
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Application (Streamlit)

#### TMHMM Filter App

Run the main filtering application:

```bash
streamlit run streamlit_app.py
```

The app provides two modules:

1. **PredHel Filter**: Upload a FASTA file and TMHMM HTML output to filter proteins with transmembrane helices
   - Set maximum allowed PredHel count
   - View filtering statistics
   - Download filtered FASTA file
   - See detailed removal report

2. **Length Filter**: Upload a FASTA file to keep only sequences shorter than a specified length
   - Set maximum sequence length threshold
   - View filtering statistics
   - Download filtered FASTA file

#### FASTA Merger App

Combine multiple FASTA files with duplicate detection:

```bash
streamlit run streamlit_merge_fasta.py
```

- Upload multiple FASTA files
- Automatically detects and reports duplicate headers
- Downloads combined FASTA file

### Command-Line Interface

Filter FASTA sequences using the CLI:

```bash
python tmhmm_cli.py --fasta input.fasta --html tmhmm_result.html --max-predhel 0 --max-length 300 -o output.fasta
```

#### CLI Options

- `--fasta`: Path to the input FASTA file (required)
- `--html`: Path to the TMHMM HTML output file (required)
- `--max-predhel`: Maximum allowed PredHel count (default: 0)
- `--max-length`: Maximum sequence length to keep, sequences ≥ this value are removed (default: 300, use 0 to disable)
- `-o, --output`: Output FASTA file path (default: `filtered_no_transmembrane.fasta`)

#### Example

```bash
python tmhmm_cli.py --fasta proteins.fasta --html tmhmm_result.html --max-predhel 0 --max-length 300 -o filtered_proteins.fasta
```

## Project Structure

```
TMHMM/
├── streamlit_app.py          # Main Streamlit web application
├── streamlit_merge_fasta.py  # FASTA file merger application
├── tmhmm_cli.py              # Command-line interface
├── tmhmm_filter.py           # Core filtering logic
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## How It Works

1. **FASTA Parsing**: Reads and parses FASTA files, extracting sequence identifiers, headers, and sequences
2. **TMHMM Parsing**: Extracts PredHel (predicted transmembrane helices) counts from TMHMM HTML output
3. **Filtering**: Applies filtering criteria based on:
   - PredHel count (removes sequences exceeding threshold)
   - Sequence length (removes sequences exceeding threshold)
4. **Output**: Generates filtered FASTA files with detailed removal reports

## Requirements

- `streamlit` - Web application framework

All other dependencies are part of Python's standard library.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Asim.Infomics
## Acknowledgments

- TMHMM: Transmembrane Hidden Markov Model for protein topology prediction
