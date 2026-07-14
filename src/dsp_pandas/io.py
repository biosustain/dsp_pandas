"""Helper to read and write data from and to different formats."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pandas as pd


def read_all_excel_sheets(
    fname: str | Path, index_col: int = 0, drop_empty: bool = True
) -> SimpleNamespace:
    """Import all sheets as pandas DataFrames from an Excel table into a SimpleNamespace object.

    Parameters
    ----------
    fname : str | Path
        Path to the Excel file.
    index_col : int, optional
        Index columns to use, by default 0
    drop_empty : bool, optional
        Wheater to drop the entirely missing columns although they might be named, by default True

    Returns
    -------
    SimpleNamespace
        Object with all the sheet names as attributes. White space are replaced by underscores.
    """
    with pd.ExcelFile(fname) as excel_reader:
        # Get the sheet names
        sheet_names = excel_reader.sheet_names
        sheets = SimpleNamespace(sheet_names=sheet_names)
        sheets_names_attr = [
            sheet_name.strip().replace(" ", "_") for sheet_name in sheet_names
        ]
        sheets.sheet_names_attr = sheets_names_attr
        for sheet_name, sheet_attr in zip(sheet_names, sheets_names_attr):
            _df = excel_reader.parse(sheet_name, index_col=index_col)
            if drop_empty:
                _df = _df.dropna(axis=1, how="all").dropna(axis=0, how="all")
            setattr(sheets, sheet_attr, _df)
    return sheets


def read_diann_protein_groups(fn: str, filter_crap: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read a DIA-NN `report.pg_matrix.tsv` file.

    Parameters
    ----------
    fn : str
        Path to the DIA-NN protein-group matrix TSV (`report.pg_matrix.tsv`).
    filter_crap : bool, optional
        If True, drop rows whose protein-group ID starts with ``cRAP-``.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        (protein_meta, proteingroups) where `protein_meta` contains the first 5
        metadata columns and `proteingroups` contains the remaining sample columns.
    """
    proteingroups = pd.read_csv(fn, sep="\t", index_col=0)

    if filter_crap:
        proteingroups = proteingroups.loc[
            ~proteingroups.index.astype(str).str.startswith("cRAP-")
        ]
    protein_meta = proteingroups.iloc[:, :5]
    proteingroups = proteingroups.iloc[:, 5:]

    return protein_meta, proteingroups
