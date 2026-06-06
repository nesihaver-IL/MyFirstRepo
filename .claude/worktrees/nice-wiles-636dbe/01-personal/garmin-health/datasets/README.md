# Garmin RAG Dataset

This folder contains personal Garmin Connect data exports for RAG (Retrieval-Augmented Generation) training.

## Upload Instructions

Copy your Garmin export files here from:
```
C:\Users\Nhaver\OneDrive - COGNYTE\Desktop\Garmin\e673ddd8-6f2f-4218-a47a-83944157473a_1
```

## Recommended Files for RAG

| Priority | File/Folder | Purpose |
|----------|-------------|---------|
| 1 | `summarizedActivities.json` | Main activity history dataset |
| 2 | Wellness JSON files | Daily health metrics |
| 3 | Sleep data files | Sleep patterns and quality |

## Folder Structure

Once uploaded, organize as follows:
```
garmin-rag-dataset/
├── raw/              # Original export files
├── processed/        # Cleaned/transformed data
└── embeddings/       # Vector embeddings (if generated)
```
