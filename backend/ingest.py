from __future__ import annotations

import os
from pathlib import Path
from typing import List

import polars as pl
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from retrieval import VectorStoreSingleton
from config import get_settings

RAW_DIR = Path("data/raw")

KAGGLE_DATASETS = [
    "mtalhazafar/career-path-selection-challenges",
    "shanimmahir/studies-career-recommendation-dataset",
]


def try_download_with_kaggle() -> None:
    if not os.environ.get("KAGGLE_USERNAME") and not Path.home().joinpath(".kaggle/kaggle.json").exists():
        return
    try:
            import subprocess
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            for dataset in KAGGLE_DATASETS:
                subprocess.run(
                    ["kaggle", "datasets", "download", "-d", dataset, "-p", str(RAW_DIR), "--unzip"],
                    check=False,
                )
    except Exception:
        pass


def load_csvs() -> List[pl.DataFrame]:
    if not RAW_DIR.exists():
        RAW_DIR.mkdir(parents=True, exist_ok=True)
    csvs = list(RAW_DIR.glob("*.csv"))
    dataframes: List[pl.DataFrame] = []
    for csv_path in csvs:
        try:
            df = pl.read_csv(csv_path)
            df = df.with_columns(pl.lit(csv_path.name).alias("__source_file"))
            dataframes.append(df)
        except Exception:
            continue
    return dataframes


def row_to_text(row: dict) -> str:
    parts: List[str] = []
    for col, val in row.items():
        if str(col).startswith("__"):
            continue
        if val is None:
            continue
        text = str(val)
        if not text.strip():
            continue
        parts.append(f"{col}: {text}")
    return "\n".join(parts)


def df_to_documents(df: pl.DataFrame, dataset_name: str) -> List[Document]:
    documents: List[Document] = []
    for row in df.iter_rows(named=True):
        content = row_to_text(row)
        if not content.strip():
            continue
        metadata = {
            "dataset": dataset_name,
            "source": row.get("__source_file", dataset_name),
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents


def main() -> None:
    settings = get_settings()
    try_download_with_kaggle()

    dataframes = load_csvs()
    if not dataframes:
        print(f"No CSVs found in {RAW_DIR}. Place the Kaggle CSVs there or configure Kaggle API.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    all_docs: List[Document] = []

    for df in dataframes:
        dataset_name = str(df.select(pl.first("__source_file")).item()) if "__source_file" in df.columns else "dataset"
        docs = df_to_documents(df, dataset_name=dataset_name)
        chunks = splitter.split_documents(docs)
        all_docs.extend(chunks)

    print(f"Prepared {len(all_docs)} chunks. Indexing into Chroma at {settings.chroma_dir}...")
    store = VectorStoreSingleton.get_store()
    batch_size = 5000  # less than 5461
    for i in range(0, len(all_docs), batch_size):
        store.add_documents(all_docs[i:i+batch_size])
    # store.persist()
    print("Ingestion complete.")


if __name__ == "__main__":
    main()