# aws-cleanup — AWS Audit & Cleanup Project

## Project Overview
Documentation and utilities related to AWS infrastructure audit, cleanup decisions, and balance management for company projects.

## Contents
| File | Purpose |
|------|---------|
| `AWS-AUDIT-README.md` | Overview of AWS audit findings |
| `AWS-AUDIT-REPORT.md` | Detailed audit report with recommendations |
| `AWS-CLEANUP-COMPLETE.md` | Completion status of cleanup tasks |
| `AWS-CLEANUP-DECISION-GUIDE.md` | Decision framework for cleanup prioritization |
| `check_aws_balance.py` | Script to monitor AWS account balance |

## Quick Start
```bash
cd 02-work/aws-cleanup
python3 check_aws_balance.py
```

## Related Documents
- See `DECISIONS.md` at repo root for architectural decisions
- See global `CLAUDE.md` for AWS credential management standards

## Notes
- All scripts assume AWS CLI credentials are configured
- See global CLAUDE.md for venv and Python environment setup
