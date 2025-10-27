# counter_aist_aloha

Analysis tools for AIST ALOHA robot HDF5 datasets.

## Overview

This repository provides tools for analyzing HDF5 datasets of the AIST ALOHA robot.  
It mainly aggregates robot action data and segment counts, and outputs a summary in CSV format.

## Installation

Requires Python 3.8 or higher.  
Dependencies are `h5py` and `numpy`.

```bash
# after Git clone
cd counter_aist_aloha 
pip install -e .
```

## Usage

You can analyze HDF5 datasets using the command-line tool `analysis`.

```bash
cd counter_aist_aloha
python ./bin/analysis <path to data directory>
```
or
```bash
python -m counter_aist_aloha.bin.analysis
```

To batch analyze **all subfolders** and output a summary CSV and JSON to `./data`, use:

```bash
python ./bin/all_analysis.py <path to codebase folder>
```

The analysis results will be output as `hdf5_analysis_summary.csv` (single folder) or `summary_hdf5.csv` and `hdf5_total_summary.json` (batch mode) in the specified directory.

## Output Summary Items

- Task Name (Identifier)
- Total Time (seconds/hours)
- Frame Count
- Frame Rate
- Robot ID / Operator ID
- Segment Count
- Record Time
- Environment / Software Version
- Target Item / Target Area
- Data Description

## Configuration File

Describe robot and environment meta information in `counter_aist_aloha/config/meta.json`.

## License

MIT License

## Author

motoda
