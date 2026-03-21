"""
KB Diagnostic Script
====================
Checks the state of Bedrock Knowledge Base JJDKJLE5BY:
- KB status and configuration
- Data source type and S3 bucket (if applicable)
- Ingestion job history (last 10 jobs)
- Live retrieval probe to confirm empty/populated state

Run:
    python experiments/kb_diagnostic.py
"""

import boto3
import json
from datetime import timezone

REGION = "us-east-1"
KB_ID = "K921550I3Z"


def main():
    bedrock_agent = boto3.client("bedrock-agent", region_name=REGION)
    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=REGION)

    # ── 1. KB overview ────────────────────────────────────────────────────────
    print("=" * 60)
    print("1. KNOWLEDGE BASE OVERVIEW")
    print("=" * 60)
    kb = bedrock_agent.get_knowledge_base(knowledgeBaseId=KB_ID)["knowledgeBase"]
    print(f"  Name   : {kb['name']}")
    print(f"  Status : {kb['status']}")
    print(f"  Role   : {kb['roleArn']}")
    storage = kb.get("storageConfiguration", {})
    print(f"  Storage: {storage.get('type', 'unknown')}")
    if storage.get("type") == "OPENSEARCH_SERVERLESS":
        oss = storage["opensearchServerlessConfiguration"]
        print(f"    Collection ARN : {oss['collectionArn']}")
        print(f"    Vector index   : {oss['vectorIndexName']}")

    # ── 2. Data sources ───────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("2. DATA SOURCES")
    print("=" * 60)
    ds_list = bedrock_agent.list_data_sources(knowledgeBaseId=KB_ID)[
        "dataSourceSummaries"
    ]
    if not ds_list:
        print("  ⚠️  NO DATA SOURCES CONFIGURED — KB cannot be populated until")
        print("      you add an S3 or CUSTOM data source in the Bedrock console.")
        return

    for ds_summary in ds_list:
        ds_id = ds_summary["dataSourceId"]
        ds = bedrock_agent.get_data_source(
            knowledgeBaseId=KB_ID, dataSourceId=ds_id
        )["dataSource"]
        print(f"  ID     : {ds_id}")
        print(f"  Name   : {ds['name']}")
        print(f"  Status : {ds['status']}")
        cfg = ds.get("dataSourceConfiguration", {})
        ds_type = cfg.get("type", "unknown")
        print(f"  Type   : {ds_type}")
        if ds_type == "S3":
            s3_cfg = cfg["s3Configuration"]
            print(f"  S3 URI : s3://{s3_cfg['bucketArn'].split(':::')[-1]}/")
            if s3_cfg.get("inclusionPrefixes"):
                print(f"  Prefix : {s3_cfg['inclusionPrefixes']}")
        print()

        # ── 3. Ingestion job history ──────────────────────────────────────────
        print(f"  Ingestion jobs for '{ds['name']}':")
        jobs = bedrock_agent.list_ingestion_jobs(
            knowledgeBaseId=KB_ID,
            dataSourceId=ds_id,
            sortBy={"attribute": "STARTED_AT", "order": "DESCENDING"},
        ).get("ingestionJobSummaries", [])

        if not jobs:
            print("    ⚠️  No ingestion jobs found — sync has never been triggered.")
        else:
            for job in jobs[:10]:
                started = job.get("startedAt", "?")
                updated = job.get("updatedAt", "?")
                stats = job.get("statistics", {})
                print(
                    f"    [{job['status']:12}] started={started}  "
                    f"scanned={stats.get('numberOfDocumentsScanned', '?')}  "
                    f"indexed={stats.get('numberOfNewDocumentsIndexed', '?')}  "
                    f"failed={stats.get('numberOfDocumentsFailed', '?')}"
                )

    # ── 4. Live retrieval probe ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("3. LIVE RETRIEVAL PROBE")
    print("=" * 60)
    probes = ["running activities", "sleep score", "vo2max", "wellness"]
    for query in probes:
        resp = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": 3}
            },
        )
        count = len(resp["retrievalResults"])
        status = "✅" if count > 0 else "❌ empty"
        print(f"  '{query}' → {count} result(s) {status}")

    print("\nDone. If all probes are empty, run kb_populate.py next.")


if __name__ == "__main__":
    main()
