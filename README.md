# AI-Knowledge-NotebookLM
AI Knowledge NotebookLM

Knowledge Base Automation

使用 GitHub Actions + Python + Google Drive + Gemini Notebook 建立自動化知識庫流程。

系統每天自動執行，將 GitHub Repository 中產生或更新的知識文件同步到 Google Drive，並可進一步提供給 Gemini Notebook / NotebookLM 進行摘要、分析與簡報產生。

Architecture
                         GitHub Repository
                                │
                                │
                         GitHub Actions
                                │
                                ▼
                    ┌────────────────────┐
                    │ Generate Knowledge │
                    │       Report       │
                    └─────────┬──────────┘
                              │
                              │ Markdown / PDF / DOCX
                              ▼
                    ┌────────────────────┐
                    │    Google Drive   │
                    │                    │
                    │  /sources         │
                    │  /reports         │
                    │  /summaries       │
                    │  /presentations   │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Gemini Notebook    │
                    │ / NotebookLM       │
                    │                    │
                    │ Knowledge Sources  │
                    └─────────┬──────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              ┌───────────┐       ┌───────────┐
              │  Summary  │       │   Slides  │
              └─────┬─────┘       └─────┬─────┘
                    │                   │
                    └─────────┬─────────┘
                              ▼
                       Google Drive

Features

目前系統提供以下功能：

GitHub Actions 自動排程

每日自動產生 Knowledge Report

Python 自動處理知識文件

Google Drive API 檔案同步

使用 MD5 判斷檔案是否有變更

Google Drive 不存在檔案時自動建立

Google Drive 已存在且內容相同時跳過

Google Drive 已存在但內容不同時更新

支援 GitHub Actions 手動執行

可延伸至 Gemini Notebook / NotebookLM

可延伸自動產生摘要

可延伸自動產生簡報

Repository Structure
.
├── .github/
│   └── workflows/
│       └── knowledge-sync.yml
│
├── scripts/
│   ├── generate_report.py
│   ├── upload_drive.py
│   ├── notebooklm.py
│   ├── generate_summary.py
│   └── generate_slides.py
│
├── data/
│   ├── sources/
│   ├── reports/
│   ├── summaries/
│   └── presentations/
│
├── requirements.txt
│
└── README.md

Workflow

GitHub Actions 每天執行一次：

01:00 UTC
   │
   │
   ▼
09:00 Taiwan Time
   │
   ▼
Generate Report
   │
   ▼
Calculate MD5
   │
   ▼
Check Google Drive
   │
   ├── File not found
   │       │
   │       └── Create
   │
   ├── MD5 identical
   │       │
   │       └── Skip
   │
   └── MD5 different
           │
           └── Update

GitHub Actions

Workflow 檔案：

.github/workflows/knowledge-sync.yml


範例：

name: Sync Knowledge Base

on:
  schedule:
    # 01:00 UTC = 09:00 Taiwan Time
    - cron: "0 1 * * *"

  workflow_dispatch:

permissions:
  contents: read

jobs:
  sync:
    runs-on: ubuntu-latest

    steps:

      - name: Checkout
        uses: actions/checkout@v6

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Generate report
        run: |
          python scripts/generate_report.py

      - name: Sync reports to Google Drive
        env:
          GOOGLE_TOKEN_JSON: ${{ secrets.GOOGLE_TOKEN_JSON }}
          DRIVE_FOLDER_ID: ${{ secrets.DRIVE_FOLDER_ID }}
        run: |
          python scripts/upload_drive.py \
            data/reports/*.md

Schedule

目前設定：

- cron: "0 1 * * *"


GitHub Actions 使用 UTC。

因此：

UTC 01:00
      ↓
Taiwan 09:00


注意：

GitHub Actions 的 cron 不使用台灣時區，因此需要使用 UTC 計算。

Manual Execution

除了每日排程之外，也可以從 GitHub Actions 手動執行。

Workflow 包含：

workflow_dispatch:


使用方式：

開啟 GitHub Repository

進入 Actions

選擇 Sync Knowledge Base

點選 Run workflow

選擇 branch

執行 Workflow

Google Drive

系統使用 Google Drive API 管理文件。

建議在 Google Drive 建立：

Knowledge Base
│
├── sources
│
├── reports
│
├── summaries
│
└── presentations


用途：

Folder	Purpose
sources	原始資料
reports	每日 Knowledge Report
summaries	AI 摘要
presentations	AI 簡報
Google Drive Synchronization

upload_drive.py 負責檔案同步。

同步邏輯：

Local File
    │
    ▼
Calculate MD5
    │
    ▼
Search Google Drive
    │
    ├── Not Found
    │      │
    │      └── Create
    │
    ├── Found + Same MD5
    │      │
    │      └── Skip
    │
    └── Found + Different MD5
           │
           └── Update


因此同一個檔案每天執行時，不會在 Google Drive 中不斷建立重複檔案。

Google Drive API

Python 程式使用：

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


Drive API Scope：

SCOPES = [
    "https://www.googleapis.com/auth/drive.file"
]

Google Credentials

目前程式支援兩種方式：

1. Environment Variable
GOOGLE_TOKEN_JSON


例如：

export GOOGLE_TOKEN_JSON='...'


GitHub Actions 中：

env:
  GOOGLE_TOKEN_JSON: ${{ secrets.GOOGLE_TOKEN_JSON }}

2. Local token.json

本機開發時可以使用：

token.json


程式會自動讀取：

GOOGLE_TOKEN_FILE


如果沒有設定：

token.json


會被當作預設值。

GitHub Secrets

Repository 需要設定：

Settings
   ↓
Secrets and variables
   ↓
Actions
   ↓
New repository secret


建立：

GOOGLE_TOKEN_JSON
DRIVE_FOLDER_ID

DRIVE_FOLDER_ID

Google Drive Folder URL 通常類似：

https://drive.google.com/drive/folders/XXXXXXXXXXXXXXXX


其中：

XXXXXXXXXXXXXXXX


就是 Folder ID。

設定：

DRIVE_FOLDER_ID


例如：

DRIVE_FOLDER_ID=XXXXXXXXXXXXXXXX


不要將 Folder ID 寫死在 Python 程式碼中。

requirements.txt

基本依賴：

google-api-python-client
google-auth
google-auth-httplib2
google-auth-oauthlib


如果後續加入 Gemini / Notebook API，可以再加入對應的 Google Cloud SDK / API Client。

Generate Report

目前每日報告可以產生：

data/reports/YYYY-MM-DD.md


例如：

data/reports/2026-09-25.md


內容：

# Daily Report 2026-09-25

Generated automatically by GitHub Actions.

Repository:
owner/repository

Workflow:
Sync Knowledge Base

Run:
123456789


未來可以將這裡改成真正的 Knowledge Collector，例如：

RSS

Web API

GitHub Issues

GitHub Discussions

GitHub Releases

Markdown documents

PDF

Google Drive documents

公司內部資料

其他 API

Gemini Notebook / NotebookLM

系統可以進一步將 Google Drive 或本地產生的文件加入 Gemini Notebook。

概念：

Markdown
   │
   ▼
Google Drive
   │
   ▼
Gemini Notebook
   │
   ├── Source
   │
   ├── Summary
   │
   ├── Question & Answer
   │
   └── Presentation


Notebook 不建議每天重新建立。

建議使用一個長期存在的 Notebook：

Daily Knowledge Base


每天只加入新的 Source。

例如：

Daily Knowledge Base
│
├── 2026-09-23.md
├── 2026-09-24.md
├── 2026-09-25.md
├── article-001.pdf
├── article-002.md
└── research-001.pdf

Incremental Synchronization

為避免每天重複加入相同文件，建議建立 Source Mapping。

例如：

{
  "2026-09-25.md": {
    "drive_id": "xxxxx",
    "source_id": "xxxxx",
    "md5": "xxxxx"
  }
}


同步時：

New File
   │
   ▼
Calculate MD5
   │
   ▼
Compare Mapping
   │
   ├── Same
   │    └── Skip
   │
   └── Changed
        └── Update

AI Summary

未來可以新增：

scripts/generate_summary.py


產生：

data/summaries/2026-09-25-summary.md


建議固定格式：

# Daily Knowledge Summary

## Executive Summary

## Key Findings

## Important Changes

## Trends

## Risks

## Follow-up

## Sources


固定輸出格式可以讓每日報告比較容易閱讀與比較。

Presentation

可以新增：

scripts/generate_slides.py


產生：

data/presentations/2026-09-25.pptx


建議簡報結構：

Slide 1
Daily Knowledge Report

Slide 2
Executive Summary

Slide 3
Key Findings

Slide 4
Important Changes

Slide 5
Trends

Slide 6
Risks

Slide 7
Follow-up

Slide 8
Sources

Recommended Pipeline

完整流程：

                   GitHub
                     │
                     ▼
             GitHub Actions
                     │
                     ▼
             Collect Sources
                     │
                     ▼
              Generate Report
                     │
                     ▼
               MD5 Check
                     │
                     ▼
              Google Drive
                     │
                     ▼
             Gemini Notebook
                     │
              ┌──────┴──────┐
              ▼             ▼
           Summary        Analysis
              │             │
              └──────┬──────┘
                     ▼
              Generate Slides
                     │
                     ▼
              Google Drive

Security

不要將以下資料直接提交到 Git Repository：

token.json
credentials.json
GOOGLE_TOKEN_JSON
service-account.json
*.pem
*.key


建議加入：

.gitignore


內容：

# Google credentials
token.json
credentials.json
service-account.json

# Environment
.env
.env.*

# Python
__pycache__/
*.pyc

# Generated files
data/reports/*
data/summaries/*
data/presentations/*


如果某些 generated files 需要進 Git，請依專案需求調整 .gitignore。

Recommended Google Cloud Setup

建議建立一個專用 Google Cloud Project：

Google Cloud Project
        │
        ├── Google Drive API
        │
        ├── Gemini / Notebook API
        │
        └── Authentication


不要使用個人開發環境的 credential 作為正式 production credential。

Production 建議使用短期 credential 與 GitHub Actions OIDC / Workload Identity Federation，而不是長期保存 OAuth refresh token。

Local Development

Clone repository：

git clone https://github.com/USERNAME/REPOSITORY.git

cd REPOSITORY


建立 virtual environment：

python -m venv .venv


啟動：

Linux / macOS：

source .venv/bin/activate


Windows：

.venv\Scripts\activate


安裝：

pip install -r requirements.txt


設定：

export DRIVE_FOLDER_ID="YOUR_FOLDER_ID"
export GOOGLE_TOKEN_JSON="YOUR_TOKEN_JSON"


執行：

python scripts/generate_report.py


同步：

python scripts/upload_drive.py \
  data/reports/*.md

Troubleshooting
Google credentials not found

錯誤：

Google credentials not found.


確認：

GOOGLE_TOKEN_JSON


或：

token.json


是否存在。

DRIVE_FOLDER_ID is not set

錯誤：

Environment variable DRIVE_FOLDER_ID is not set.


設定：

export DRIVE_FOLDER_ID="YOUR_FOLDER_ID"


GitHub Actions 則確認：

Settings
→ Secrets and variables
→ Actions


是否存在：

DRIVE_FOLDER_ID

Google credentials are invalid

錯誤：

Google credentials are invalid or expired.


可能原因：

OAuth token 過期

Refresh token 不存在

Google Cloud Project 設定錯誤

Drive API 未啟用

OAuth Scope 不正確

GitHub Secret 內容錯誤

File is uploaded repeatedly

確認：

md5Checksum


是否正常取得。

目前同步機制：

Local MD5
    ↓
Drive MD5
    ↓
Same?
    ├── Yes → Skip
    └── No  → Update

Future Improvements

後續可以加入：

 RSS 自動收集

 Web API 自動收集

 GitHub Release 自動收集

 PDF 解析

 DOCX 解析

 Web page extraction

 Gemini Notebook source 自動同步

 AI 自動摘要

 AI 自動分類

 AI 自動標籤

 AI 自動產生簡報

 Google Slides 自動產生

 Email 通知

 Slack / Teams 通知

 Incremental source synchronization

 GitHub Actions OIDC

 Google Cloud Workload Identity Federation

 Workflow failure notification

 Retry mechanism

 Audit log

Design Principles

本專案遵循以下原則：

1. GitHub 負責 Automation

GitHub Actions 負責：

Schedule
Execution
Version Control
CI/CD

2. Google Drive 負責 File Storage

Google Drive 負責：

Source
Report
Summary
Presentation

3. Gemini Notebook 負責 Knowledge Layer

Gemini Notebook 負責：

Knowledge Sources
Context
Research
Analysis

4. AI Output 必須可追溯

每一份摘要或簡報應保留：

Source
Generated Date
Workflow Run
Input Files


以便日後確認內容來源。

License

請依實際專案需求設定 License。

例如：

MIT License


或使用其他適合的開源授權。
