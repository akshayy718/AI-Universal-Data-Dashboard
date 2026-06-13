<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0,FF4B4B,FF8C00,FFD700&height=200&section=header&fontSize=42&fontColor=fff&animation=fadeIn&fontAlignY=36" width="100%"/>
</div>

<div align="center">

<pre>
 █████╗ ██╗    ██████╗  █████╗ ████████╗ █████╗ 
██╔══██╗██║    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
███████║██║    ██║  ██║███████║   ██║   ███████║
██╔══██║██║    ██║  ██║██╔══██║   ██║   ██╔══██║
██║  ██║██║    ██████╔╝██║  ██║   ██║   ██║  ██║
╚═╝  ╚═╝╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗ 
██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
██║  ██║███████║███████╗███████║██████╔╝██║   ██║███████║██████╔╝██║  ██║
██║  ██║██╔══██║╚════██║██╔══██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║
██████╔╝██║  ██║███████║██║  ██║██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
</pre>

### 🚀 Live App → **[ai-universal-data-dashboard.streamlit.app](https://ai-universal-data-dashboard.streamlit.app/)**

[![Live App](https://img.shields.io/badge/▶_Open_Live_App-ai--universal--data--dashboard.streamlit.app-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://ai-universal-data-dashboard.streamlit.app/)
[![Groq AI](https://img.shields.io/badge/🤖_Groq_AI-llama--3.3--70b-FF8C00?style=for-the-badge)](https://console.groq.com)
[![GitHub](https://img.shields.io/badge/GitHub-akshayy718-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/akshayy718)

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-FF4B4B?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-FFD700?style=flat-square&logo=pandas&logoColor=black)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-FF8C00?style=flat-square&logo=plotly&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-FF4B4B?style=flat-square)
![Hosted](https://img.shields.io/badge/Hosted-Streamlit_Cloud-FFD700?style=flat-square&logo=streamlit&logoColor=black)

</div>

---

## 📌 Overview

A **universal AI-powered data dashboard** built with Python and Streamlit. Upload **any** Excel, CSV, PDF, or Word file — the dashboard automatically detects your columns, builds interactive charts, tracks deadlines, and lets you **chat with your data** using Groq's Llama 3.3 70B model. Zero configuration required.

> 🧠 Works with any dataset — project trackers, sales reports, HR data, finance sheets, and more.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **Multi-Format Upload** | CSV, Excel, PDF (tables), Word (tables) |
| 🔍 **Auto Column Detection** | Finds task, status, date, and category columns automatically |
| 📊 **Smart Charts** | Pie, Bar, Timeline, and Scatter — all auto-generated |
| 📈 **Key Metrics** | Total, Completed, Pending, Overdue, Due This Week |
| ⏰ **Deadline Tracker** | Upcoming deadlines in the next 30 days with urgency colour coding |
| 🤖 **Groq AI Q&A** | Ask anything about your data in plain English |
| 🔎 **General Analyzer** | Auto-discovers and charts any extra numeric or category columns |
| 💾 **Export** | Download filtered data, overdue tasks, or summary report as CSV |
| ⚙️ **Column Override** | Manually correct any auto-detected column mapping |

---

## 🔗 Live Demo

<div align="center">

| | Link | Description |
|--|------|-------------|
| 🚀 | [**ai-universal-data-dashboard.streamlit.app**](https://ai-universal-data-dashboard.streamlit.app/) | Upload your file and explore instantly |

</div>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      STREAMLIT CLOUD                     │
│                                                          │
│   Sidebar                      Main Panel                │
│   ┌────────────────┐          ┌──────────────────────┐  │
│   │ 🔑 Groq Key    │          │  📈 Metrics Row       │  │
│   │ 📁 File Upload │  ──────▶ │  📊 Auto Charts       │  │
│   │ 🔍 Filters     │          │  📋 Task Detail View  │  │
│   │ 🏷️ Category    │          │  ⏰ Upcoming Deadlines │  │
│   │ 🔄 Status      │          │  🤖 Groq AI Chat      │  │
│   └────────────────┘          │  💾 Export Buttons    │  │
│                               └──────────────────────┘  │
└──────────────────────────┬──────────────────────────────┘
                           │
           ┌───────────────┼──────────────────┐
           ▼               ▼                  ▼
  ┌──────────────┐ ┌──────────────┐  ┌──────────────────┐
  │  File Loader │ │ Auto Detect  │  │   Groq AI API    │
  │  CSV / Excel │ │   Columns    │  │  llama-3.3-70b   │
  │  PDF / DOCX  │ │   & Charts   │  │  (free · fast)   │
  └──────────────┘ └──────────────┘  └──────────────────┘
```

---

## 🤖 AI Pipeline

```
  User Uploads File (CSV / Excel / PDF / DOCX)
         │
         ▼
  ┌─────────────────┐
  │  File Loader     │
  │  pandas (CSV)    │
  │  pandas (Excel)  │
  │  pdfplumber (PDF)│
  │  python-docx     │
  └────────┬────────┘
           │
           ▼
  ┌──────────────────────────────────┐
  │     Auto Column Detection         │
  │  ├── Task / Description column   │
  │  ├── Status column               │
  │  ├── Due Date column             │
  │  └── Category column             │
  └────────┬─────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────┐
  │     build_summary()              │
  │  ├── Status counts               │
  │  ├── Category breakdown          │
  │  ├── Category x Status matrix    │
  │  └── Overdue task names          │
  └────────┬─────────────────────────┘
           │
           ▼
  ┌──────────────────────────────────┐
  │       Groq API                   │
  │   Model: llama-3.3-70b           │
  │   ├── 📊 5-point summary         │
  │   ├── 🚨 Top 3 priorities        │
  │   └── 💬 Free-text Q&A           │
  └────────┬─────────────────────────┘
           │
           ▼
  Answer displayed in the app
```

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | Streamlit | Python-native web app UI |
| **Data** | Pandas | DataFrame loading and manipulation |
| **Charts** | Plotly Express | Interactive pie, bar, scatter, timeline |
| **AI Model** | Groq llama-3.3-70b-versatile | Insight summary + free-text Q&A |
| **PDF Parser** | pdfplumber | Table extraction from PDF files |
| **DOCX Parser** | python-docx | Table extraction from Word documents |
| **Excel Parser** | openpyxl | Excel file reading |
| **Hosting** | Streamlit Cloud | Auto-deploy from GitHub |

</div>

---

## 📁 Project Structure

```
AI-Universal-Data-Dashboard/
├── 📄 universal_dashboard.py   → Main Streamlit app (all logic)
├── 📄 requirements.txt     → Python dependencies
└── 📄 README.md            → This file
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Free Groq API Key → [console.groq.com](https://console.groq.com)

### Setup

```bash
# Clone the repo
git clone https://github.com/akshayy718/AI-Universal-Data-Dashboard.git
cd AI-Universal-Data-Dashboard

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run universal_dashboard.py
```

Open → `http://localhost:8501`

---

## 🔮 Future Improvements

- [ ] **Claude API support** — multi-model AI switching
- [ ] **Persistent chat history** — multi-turn conversations
- [ ] **AI-suggested charts** — model recommends best visualisation
- [ ] **Natural language filters** — "show me overdue tasks in Marketing"
- [ ] **Multi-file merge** — upload and compare multiple datasets
- [ ] **Dark mode UI** — custom Streamlit theming

---

## 👨‍💻 Author

<div align="center">

**Akshay Santhosh** — AI/ML Engineer · Dashboard & Data App Builder

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Akshay%20Santhosh-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/akshay-santhosh-435499208/)
[![GitHub](https://img.shields.io/badge/GitHub-akshayy718-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/akshayy718)
[![Email](https://img.shields.io/badge/Gmail-akshaysanthosh718-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:akshaysanthosh718@gmail.com)

</div>

---

<div align="center">

*Built with ❤️ using Python · Streamlit · Plotly · Groq AI*

<img src="https://capsule-render.vercel.app/api?type=waving&color=0,FFD700,FF8C00,FF4B4B&height=130&section=footer&animation=fadeIn" width="100%"/>

</div>
