<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0,20,20,40,0&height=2&section=header" width="100%"/>

```
██████╗  █████╗ ████████╗ █████╗     ██████╗  █████╗ ███████╗██╗  ██╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ██╔══██╗██╔══██╗██╔════╝██║  ██║
██║  ██║███████║   ██║   ███████║    ██║  ██║███████║███████╗███████║
██║  ██║██╔══██║   ██║   ██╔══██║    ██║  ██║██╔══██║╚════██║██╔══██║
██████╔╝██║  ██║   ██║   ██║  ██║    ██████╔╝██║  ██║███████║██║  ██║
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

<img src="https://capsule-render.vercel.app/api?type=soft&color=gradient&customColorList=2,3&height=3&section=header" width="100%"/>

### `v2.0` · Upload Any File · Ask AI · Get Instant Insights

[![Live Demo](https://img.shields.io/badge/▶_LIVE_DEMO-ai--universal--data--dashboard.streamlit.app-22c55e?style=for-the-badge&logo=streamlit&logoColor=white)](https://ai-universal-data-dashboard.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-f59e0b?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-ef4444?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq AI](https://img.shields.io/badge/Groq-llama--3.3--70b-a855f7?style=for-the-badge)](https://console.groq.com)
[![GitHub](https://img.shields.io/badge/GitHub-akshayy718-white?style=for-the-badge&logo=github&logoColor=black)](https://github.com/akshayy718)

</div>

---

## `$ what_is_this`

Drop **any** data file — Excel, CSV, PDF, or Word — and this dashboard figures out what's inside, builds charts automatically, and lets you have a conversation with your data using **Groq AI**. No setup. No configuration. No SQL.

> Just upload → explore → ask questions → export.

---

## `$ features --list`

```
✦ FILE SUPPORT
  ├── CSV            →  Auto-parsed, any structure
  ├── Excel (.xlsx)  →  Multi-sheet aware
  ├── PDF            →  Table extraction via pdfplumber
  └── Word (.docx)   →  Table extraction via python-docx

✦ AUTO-DETECTION
  ├── Task / Name column
  ├── Status column   (Done · Pending · In Progress · Closed...)
  ├── Due Date column (EDD · Deadline · Target · End Date...)
  └── Category column (Department · Type · Module · Team...)

✦ SMART METRICS
  ├── Total rows · Completed · Pending
  ├── Overdue count · Due this week · No due date
  └── Live progress bar with completion %

✦ CHARTS (Auto-Generated)
  ├── Pie  → Tasks by Category
  ├── Bar  → Tasks by Status (colour-coded)
  ├── Pie  → Due Date Status Distribution
  ├── Scatter → Task Timeline by Due Date
  └── General Analyzer → any other numeric/category columns

✦ GROQ AI
  ├── 📊 Generate a 5-point insight summary
  ├── 🚨 "What should I focus on?" — top 3 priorities
  └── 💬 Free-text Q&A — ask anything about your data

✦ EXPORT
  ├── Filtered data  → CSV
  ├── Overdue tasks  → CSV
  └── Summary report → CSV (per category breakdown)
```

---

## `$ demo`

<div align="center">

| What you upload | What you get |
|----------------|-------------|
| A project tracker Excel | Status charts, overdue alerts, timeline view |
| A sales CSV | Category breakdown, numeric summaries, AI insights |
| A report PDF with tables | Extracted data, instant visualisations |
| Any spreadsheet | Auto-detected columns, charts, AI Q&A |

**→ Try it live:** [ai-universal-data-dashboard.streamlit.app](https://ai-universal-data-dashboard.streamlit.app/)

</div>

---

## `$ architecture`

```
┌─────────────────────────────────────────────────────────┐
│                     YOUR BROWSER                         │
│                                                          │
│   Sidebar                     Main Panel                 │
│   ┌──────────────┐           ┌─────────────────────┐    │
│   │ 🔑 Groq Key  │           │  📈 Metrics Row      │    │
│   │ 📁 Upload    │           │  📊 Auto Charts      │    │
│   │ 🔍 Filters   │    ───▶   │  📋 Task Detail View │    │
│   │              │           │  ⏰ Upcoming Deadlines│    │
│   │              │           │  🤖 AI Chat          │    │
│   └──────────────┘           │  💾 Export Buttons   │    │
│                              └─────────────────────┘    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  STREAMLIT CLOUD                          │
│                                                          │
│  app.py                                                  │
│  ├── load_file()        →  CSV / Excel / PDF / DOCX     │
│  ├── detect_columns()   →  Auto column detection        │
│  ├── general_analysis() →  Find chartable columns       │
│  ├── build_summary()    →  Token-efficient AI context   │
│  └── call_groq()        →  Groq API (llama-3.3-70b)    │
│                                                          │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Groq API             │
              │   llama-3.3-70b        │
              │   (free · fast · smart)│
              └────────────────────────┘
```

---

## `$ quick_start`

### Run locally

```bash
# 1. Clone
git clone https://github.com/akshayy718/AI-Universal-Data-Dashboard.git
cd AI-Universal-Data-Dashboard

# 2. Install
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

Open → `http://localhost:8501`

### Get a free Groq API key

```
1. Go to  →  console.groq.com
2. Sign up (free)
3. Create API Key
4. Paste it in the sidebar of the app
```

---

## `$ stack`

| Layer | Tool | Why |
|-------|------|-----|
| **UI Framework** | Streamlit | Fast, Python-native web app |
| **Data** | Pandas | DataFrame manipulation |
| **Charts** | Plotly | Interactive, beautiful visuals |
| **AI** | Groq + llama-3.3-70b | Fast inference, free tier |
| **PDF** | pdfplumber | Accurate table extraction |
| **Word** | python-docx | DOCX table parsing |
| **Hosting** | Streamlit Cloud | One-click deploy from GitHub |

---

## `$ requirements.txt`

```
streamlit
pandas
plotly
requests
pdfplumber
python-docx
openpyxl
```

---

## `$ roadmap`

```diff
+ Uploaded CSV / Excel / PDF / Word support
+ Auto column detection
+ Groq AI Q&A
+ Overdue tracking + timeline chart
+ Export to CSV
+ Live on Streamlit Cloud

~ Claude API support (multi-model)
~ Persistent chat history
~ AI-suggested chart types
~ Natural language filters
~ Multi-file upload & merge
```

---

## `$ author`

<div align="center">

**Akshay Santhosh** — AI/ML Engineer · Data & Dashboard Builder

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Akshay%20Santhosh-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/akshay-santhosh-)
[![GitHub](https://img.shields.io/badge/GitHub-akshayy718-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/akshayy718)
[![Email](https://img.shields.io/badge/Gmail-akshaysanthosh718-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:akshaysanthosh718@gmail.com)

</div>

---

<div align="center">

`built with Python · Streamlit · Plotly · Groq AI`

*Drop a file. Ask a question. Get an answer.*

</div>
