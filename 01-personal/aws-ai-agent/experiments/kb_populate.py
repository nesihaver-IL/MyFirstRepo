"""
KB Population Script
====================
Uploads Garmin health documents to the S3 data source and triggers
ingestion into Knowledge Base JJDKJLE5BY.

Strategy
--------
Markdown files  → uploaded as-is (best for RAG retrieval)
JSON files      → large files are chunked into smaller text blocks
                  so Bedrock can embed them meaningfully

Run:
    python experiments/kb_populate.py [--dry-run]

Prerequisites:
    1. Run kb_diagnostic.py first to confirm the S3 bucket name.
    2. Set KB_S3_BUCKET below if the diagnostic shows a different bucket.
    3. Your AWS credentials must allow s3:PutObject on that bucket.
"""

import argparse
import json
import os
import sys
import time

import boto3

REGION = "us-east-1"
KB_ID = "K921550I3Z"

# ── Set this to your KB's S3 bucket name (from kb_diagnostic.py output) ──────
# Example: "my-garmin-kb-bucket-123456"
KB_S3_BUCKET = "awshealthdataactivity"
KB_S3_PREFIX = "Garmin/"   # matches the S3 data source prefix in the KB

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

# Files to upload — Markdown files go in as-is.
# Large JSON files are converted to readable text chunks.
MARKDOWN_FILES = [
    "Research_Summary_Running-EN.md",
    "Research_Summary_Swimming.md",
    "Research_Summary_sleeping.md",
    "Research_Summary_sleeping-1.md",
    "GARMIN_API_README.md",
    "garmin_health_api_guide.md",
]

JSON_FILES = [
    "nesihaver@gmail.com_personalRecord.json",
    "85435159_userBioMetrics.json",
    "vo2max_metrics_all_merged.json",
    # Large files below are chunked — set CHUNK_RECORDS to control size
    "sleep_all_merged.json",
    "training_history_all_merged.json",
    "race_predictions_all_merged.json",
    "nesihaver@gmail.com_0_summarizedActivities.json",
    "wellness_all_merged.json",
]

# Max records per chunk file for large JSON arrays
CHUNK_RECORDS = 200


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be uploaded without actually uploading",
    )
    return p.parse_args()


# ── Helpers ───────────────────────────────────────────────────────────────────

def json_to_text(data, filename: str) -> str:
    """Convert a JSON object/array into a readable text block for embedding."""
    name = filename.replace(".json", "").replace("_", " ").replace("-", " ")
    if isinstance(data, list):
        lines = [f"# {name} ({len(data)} records)\n"]
        for i, item in enumerate(data):
            lines.append(f"## Record {i + 1}\n")
            for k, v in (item.items() if isinstance(item, dict) else [("value", item)]):
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    elif isinstance(data, dict):
        lines = [f"# {name}\n"]
        for k, v in data.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    return str(data)


def upload_file(s3, bucket: str, key: str, body: bytes, content_type: str, dry_run: bool):
    size_kb = len(body) / 1024
    if dry_run:
        print(f"  [DRY RUN] would upload → s3://{bucket}/{key}  ({size_kb:.1f} KB)")
        return
    s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType=content_type)
    print(f"  ✅ uploaded → s3://{bucket}/{key}  ({size_kb:.1f} KB)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    if not KB_S3_BUCKET:
        print("❌ KB_S3_BUCKET is not set.")
        print("   1. Run kb_diagnostic.py to find your S3 bucket name.")
        print("   2. Set KB_S3_BUCKET at the top of this script.")
        sys.exit(1)

    s3 = boto3.client("s3", region_name=REGION)
    bedrock_agent = boto3.client("bedrock-agent", region_name=REGION)

    # ── Step 1: Upload Markdown files ─────────────────────────────────────────
    print("=" * 60)
    print("STEP 1: Uploading Markdown files")
    print("=" * 60)
    for fname in MARKDOWN_FILES:
        fpath = os.path.join(DOCS_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  ⚠️  not found, skipping: {fname}")
            continue
        with open(fpath, "rb") as f:
            body = f.read()
        key = f"{KB_S3_PREFIX}{fname}"
        upload_file(s3, KB_S3_BUCKET, key, body, "text/markdown", args.dry_run)

    # ── Step 2: Upload JSON files (chunked if large) ──────────────────────────
    print("\n" + "=" * 60)
    print("STEP 2: Uploading JSON files (chunking large arrays)")
    print("=" * 60)
    for fname in JSON_FILES:
        fpath = os.path.join(DOCS_DIR, fname)
        if not os.path.exists(fpath):
            print(f"  ⚠️  not found, skipping: {fname}")
            continue

        with open(fpath) as f:
            data = json.load(f)

        if isinstance(data, list) and len(data) > CHUNK_RECORDS:
            # Split into chunks
            chunks = [
                data[i : i + CHUNK_RECORDS]
                for i in range(0, len(data), CHUNK_RECORDS)
            ]
            print(f"  {fname}: {len(data)} records → {len(chunks)} chunks of {CHUNK_RECORDS}")
            for idx, chunk in enumerate(chunks):
                text = json_to_text(chunk, fname)
                chunk_fname = fname.replace(".json", f"_chunk{idx+1:03d}.txt")
                key = f"{KB_S3_PREFIX}{chunk_fname}"
                upload_file(
                    s3, KB_S3_BUCKET, key,
                    text.encode("utf-8"), "text/plain", args.dry_run
                )
        else:
            text = json_to_text(data, fname)
            txt_fname = fname.replace(".json", ".txt")
            key = f"{KB_S3_PREFIX}{txt_fname}"
            upload_file(
                s3, KB_S3_BUCKET, key,
                text.encode("utf-8"), "text/plain", args.dry_run
            )

    if args.dry_run:
        print("\n[DRY RUN complete — no files were uploaded, no ingestion triggered]")
        return

    # ── Step 3: Trigger ingestion job ─────────────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 3: Triggering KB ingestion job")
    print("=" * 60)

    ds_list = bedrock_agent.list_data_sources(knowledgeBaseId=KB_ID)[
        "dataSourceSummaries"
    ]
    if not ds_list:
        print("❌ No data sources found on the KB. Cannot trigger ingestion.")
        print("   Add an S3 data source pointing to your bucket in the Bedrock console.")
        return

    # Start an ingestion job for each S3 data source
    for ds in ds_list:
        ds_id = ds["dataSourceId"]
        print(f"  Starting ingestion for data source: {ds['name']} ({ds_id})")
        resp = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=KB_ID,
            dataSourceId=ds_id,
        )
        job_id = resp["ingestionJob"]["ingestionJobId"]
        print(f"  Job ID: {job_id} — Status: {resp['ingestionJob']['status']}")

    # ── Step 4: Poll until complete ───────────────────────────────────────────
    print("\nPolling for ingestion completion (this may take a few minutes)...")
    for ds in ds_list:
        ds_id = ds["dataSourceId"]
        jobs = bedrock_agent.list_ingestion_jobs(
            knowledgeBaseId=KB_ID,
            dataSourceId=ds_id,
            sortBy={"attribute": "STARTED_AT", "order": "DESCENDING"},
        )["ingestionJobSummaries"]
        if not jobs:
            continue
        job_id = jobs[0]["ingestionJobId"]

        for _ in range(40):   # up to ~10 minutes
            job = bedrock_agent.get_ingestion_job(
                knowledgeBaseId=KB_ID,
                dataSourceId=ds_id,
                ingestionJobId=job_id,
            )["ingestionJob"]
            status = job["status"]
            stats = job.get("statistics", {})
            print(
                f"  [{status}] "
                f"scanned={stats.get('numberOfDocumentsScanned', '?')}  "
                f"indexed={stats.get('numberOfNewDocumentsIndexed', '?')}  "
                f"failed={stats.get('numberOfDocumentsFailed', '?')}"
            )
            if status in ("COMPLETE", "FAILED", "STOPPED"):
                break
            time.sleep(15)

    print("\n✅ Done. Run kb_diagnostic.py to verify retrieval is now working.")


if __name__ == "__main__":
    main()
