import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import requests

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(page_title="Universal Data Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# ALL HELPER FUNCTIONS (defined at top)
# ─────────────────────────────────────────

def general_analysis(df, exclude_cols):
    """
    GENERAL ANALYZER MODE (v2).
    For any dataset, find columns worth charting:
    - Category-like columns (text with few unique values) -> pie/bar charts
    - Numeric columns -> summary stats + bar charts
    exclude_cols = columns already used (task/status/date/category) so we don't repeat them.
    Returns two lists: category_columns, numeric_columns.
    """
    category_cols = []
    numeric_cols = []

    for col in df.columns:
        # Skip helper columns and already-used columns
        if col.startswith('_') or col in exclude_cols:
            continue

        # Numeric column? (numbers we can average/sum)
        if pd.api.types.is_numeric_dtype(df[col]):
            # Skip ID-like columns (every value unique = probably an ID, not useful)
            if df[col].nunique() > 1 and df[col].nunique() < len(df):
                numeric_cols.append(col)
        else:
            # Text column with a reasonable number of unique values = chartable category.
            # We allow up to 60% unique (so big lists like Country/Industry still count),
            # but skip free-text columns where almost every value is unique (like descriptions).
            nunique = df[col].nunique()
            if 1 < nunique <= max(30, int(len(df) * 0.6)):
                # Extra guard: skip very long text (descriptions, URLs)
                avg_len = df[col].dropna().astype(str).str.len().mean()
                if avg_len < 50:
                    category_cols.append(col)

    return category_cols, numeric_cols


def call_groq(api_key, prompt):
    """Call Groq API and return response text."""
    try:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a helpful data analyst. Be concise and practical."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.3
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Groq API error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


def build_summary(df, status_col, date_col, category_col, task_col):
    """Build a small but information-rich summary to send to Groq (saves tokens).

    We include a category-by-status cross-tab so the AI can answer specific
    questions like 'which category has the most pending tasks' directly,
    instead of guessing or writing code.
    """
    lines = [f"Dataset: {len(df)} rows, {len(df.columns)} columns."]

    if status_col:
        lines.append(f"Status counts: {df[status_col].value_counts().to_dict()}")

    if category_col:
        lines.append(f"Category counts: {df[category_col].value_counts().head(10).to_dict()}")

    # Cross-tab: how many of each status per category (the key detail for Q&A)
    if status_col and category_col:
        try:
            cross = df.groupby([category_col, status_col]).size().unstack(fill_value=0)
            lines.append(f"Category x Status table: {cross.to_dict()}")
        except Exception:
            pass

    if date_col:
        today = pd.Timestamp(datetime.now().date())
        has_date = df[date_col].notna().sum()
        if status_col:
            overdue = df[(df[date_col].notna()) & (df[date_col] < today) & (~df[status_col].apply(is_done))]
            lines.append(f"Tasks with dates: {has_date}, Overdue: {len(overdue)}")
            # List the actual overdue task names (up to 10) so AI can name them
            if len(overdue) > 0 and task_col:
                overdue_names = overdue[task_col].dropna().astype(str).head(10).tolist()
                lines.append(f"Overdue task names: {overdue_names}")
        else:
            lines.append(f"Tasks with dates: {has_date}")

    if task_col:
        lines.append(f"Sample tasks: {df[task_col].dropna().head(3).tolist()}")

    return " | ".join(lines)


def is_done(value):
    """Check if a status value means completed."""
    done_kw = ['done', 'complete', 'completed', 'closed', 'finished', 'resolved', 'approved']
    return any(k in str(value).lower() for k in done_kw)


def get_date_status(due_date, status_value):
    """Return overdue / due_soon / on_track / completed / no_date."""
    if pd.isna(due_date):
        return 'no_date'
    today = pd.Timestamp(datetime.now().date())
    try:
        due = pd.Timestamp(due_date.date())
    except Exception:
        return 'no_date'
    if is_done(status_value):
        return 'completed'
    days_diff = (due - today).days
    if days_diff < 0:
        return 'overdue'
    elif days_diff <= 7:
        return 'due_soon'
    else:
        return 'on_track'


def detect_columns(df):
    """Auto-detect task, status, date, category columns."""
    cols_lower = {col: col.lower() for col in df.columns}

    # Task column
    task_col = None
    for col, cl in cols_lower.items():
        if any(k in cl for k in ['task', 'description', 'name', 'activity', 'work', 'item', 'subject']):
            task_col = col
            break
    if not task_col:
        text_cols = df.select_dtypes(include='object').columns
        if len(text_cols) > 0:
            task_col = max(text_cols, key=lambda c: df[c].dropna().astype(str).str.len().mean())

    # Status column
    status_col = None
    for col, cl in cols_lower.items():
        if any(k in cl for k in ['status', 'state', 'progress', 'completion', 'stage']):
            status_col = col
            break

    # Date column
    date_col = None
    date_priority = ['due', 'deadline', 'end', 'edd', 'delivery', 'target', 'finish', 'complete']
    for priority in date_priority:
        for col, cl in cols_lower.items():
            if priority in cl:
                test = pd.to_datetime(df[col], errors='coerce')
                if test.notna().sum() > 0:
                    date_col = col
                    break
        if date_col:
            break
    if not date_col:
        for col, cl in cols_lower.items():
            if 'date' in cl:
                test = pd.to_datetime(df[col], errors='coerce')
                if test.notna().sum() > 0:
                    date_col = col
                    break

    # Category column
    category_col = None
    for col, cl in cols_lower.items():
        if any(k in cl for k in ['category', 'type', 'department', 'module', 'group', 'section', 'area', 'team']):
            if df[col].nunique() <= 30:
                category_col = col
                break

    return task_col, status_col, date_col, category_col


def clean_status(df, status_col):
    """Convert NaN/empty statuses to Pending."""
    df[status_col] = df[status_col].replace('', 'Pending')
    df[status_col] = df[status_col].fillna('Pending')
    df[status_col] = df[status_col].astype(str).str.strip()
    df[status_col] = df[status_col].replace('nan', 'Pending')
    df[status_col] = df[status_col].replace('None', 'Pending')
    return df


@st.cache_data(show_spinner="Loading your file...")
def load_file(source):
    """Load CSV, Excel, PDF, or Word file into a DataFrame.

    @st.cache_data tells Streamlit to remember the result for a given file,
    so if the same file is loaded again it skips re-reading and re-processing.
    This makes the app noticeably faster on repeat loads.
    """
    try:
        name = source.name.lower() if hasattr(source, 'name') else source.lower()

        if name.endswith('.csv'):
            return pd.read_csv(source), "csv"

        elif name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(source), "excel"

        elif name.endswith('.pdf'):
            try:
                import pdfplumber
                all_tables = []
                with pdfplumber.open(source) as pdf:
                    for page in pdf.pages:
                        for table in page.extract_tables():
                            if table:
                                df_t = pd.DataFrame(table[1:], columns=table[0])
                                all_tables.append(df_t)
                if all_tables:
                    return pd.concat(all_tables, ignore_index=True), "pdf"
                else:
                    st.warning("No tables found in PDF.")
                    return None, "pdf_no_table"
            except ImportError:
                st.error("Install pdfplumber: pip install pdfplumber")
                return None, "error"

        elif name.endswith('.docx'):
            try:
                from docx import Document
                doc = Document(source)
                all_tables = []
                for table in doc.tables:
                    data = [[cell.text.strip() for cell in row.cells] for row in table.rows]
                    if data:
                        df_t = pd.DataFrame(data[1:], columns=data[0])
                        all_tables.append(df_t)
                if all_tables:
                    return pd.concat(all_tables, ignore_index=True), "docx"
                else:
                    st.warning("No tables found in Word document.")
                    return None, "docx_no_table"
            except ImportError:
                st.error("Install python-docx: pip install python-docx")
                return None, "error"

        else:
            st.error("Unsupported file type.")
            return None, "unsupported"

    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None, "error"


def render_tasks(data, task_col, status_col, date_col, today):
    """Render individual task rows."""
    for _, row in data.iterrows():
        cols = st.columns([3, 1.5, 1.5])

        with cols[0]:
            if task_col:
                txt = str(row[task_col])
                if row.get('_is_done', False):
                    st.markdown(f"~~{txt}~~")
                else:
                    st.write(txt)
            else:
                st.write("—")

        with cols[1]:
            if status_col:
                sv = str(row[status_col])
                if is_done(sv):
                    st.success(f"✅ {sv}")
                elif any(k in sv.lower() for k in ['overdue', 'late']):
                    st.error(f"🚨 {sv}")
                else:
                    st.warning(f"⏳ {sv}")

        with cols[2]:
            if date_col and pd.notna(row.get(date_col)):
                d = pd.to_datetime(row[date_col])
                days_diff = (d.date() - today.date()).days
                if row.get('_is_done', False):
                    st.success(f"📅 {d.strftime('%d-%b-%Y')}")
                elif days_diff < 0:
                    st.error(f"🚨 {d.strftime('%d-%b-%Y')} ({abs(days_diff)}d overdue)")
                elif days_diff <= 7:
                    st.warning(f"⚠️ {d.strftime('%d-%b-%Y')} ({days_diff}d left)")
                else:
                    st.info(f"📅 {d.strftime('%d-%b-%Y')} ({days_diff}d left)")
            else:
                st.caption("No due date")

        st.divider()


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.markdown("## 📊 Universal Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Groq AI (Optional)")
groq_api_key = st.sidebar.text_input("Groq API Key:", type="password", placeholder="gsk_...")
if groq_api_key:
    st.sidebar.success("✅ Groq AI ready!")
else:
    st.sidebar.info("Add Groq key to enable AI insights")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 Upload Your File")
uploaded_file = st.sidebar.file_uploader(
    "Drag & drop any file",
    type=['csv', 'xlsx', 'xls', 'pdf', 'docx'],
    help="Supports: CSV, Excel, PDF (with tables), Word (with tables)"
)
file_path = st.sidebar.text_input("Or enter file path:", placeholder="C:/Users/.../file.csv")

# ─────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────
st.markdown("# 📊 Universal Data Dashboard")
st.caption("Upload any Excel, CSV, PDF or Word file — automatic insights, charts, and AI analysis")
st.markdown("---")

# ─────────────────────────────────────────
# LOAD FILE
# ─────────────────────────────────────────
df_raw = None
file_type = None

if uploaded_file:
    df_raw, file_type = load_file(uploaded_file)
elif file_path:
    df_raw, file_type = load_file(file_path)

# ─────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────
if df_raw is not None:

    df = df_raw.copy()
    df.dropna(how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    df.reset_index(drop=True, inplace=True)

    st.success(f"✅ File loaded! **{len(df)} rows × {len(df.columns)} columns** | Type: **{file_type.upper()}**")

    # Auto-detect columns
    task_col, status_col, date_col, category_col = detect_columns(df)

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    if status_col:
        df = clean_status(df, status_col)
        df['_is_done'] = df[status_col].apply(is_done)
    else:
        df['_is_done'] = False

    if date_col and status_col:
        df['_date_status'] = df.apply(lambda r: get_date_status(r[date_col], r[status_col]), axis=1)
    elif date_col:
        df['_date_status'] = df[date_col].apply(lambda d: get_date_status(d, ''))

    # Column override
    with st.expander("⚙️ Auto-Detected Columns — Click to Override", expanded=False):
        st.info("The dashboard auto-detected these columns from your file. You can change them.")
        all_cols = ['(None)'] + df.columns.tolist()
        co1, co2, co3, co4 = st.columns(4)
        with co1:
            task_col = st.selectbox("📝 Task Column", all_cols,
                index=all_cols.index(task_col) if task_col in all_cols else 0)
        with co2:
            status_col = st.selectbox("🔄 Status Column", all_cols,
                index=all_cols.index(status_col) if status_col in all_cols else 0)
        with co3:
            date_col = st.selectbox("📅 Due Date Column", all_cols,
                index=all_cols.index(date_col) if date_col in all_cols else 0)
        with co4:
            category_col = st.selectbox("🏷️ Category Column", all_cols,
                index=all_cols.index(category_col) if category_col in all_cols else 0)

        task_col = None if task_col == '(None)' else task_col
        status_col = None if status_col == '(None)' else status_col
        date_col = None if date_col == '(None)' else date_col
        category_col = None if category_col == '(None)' else category_col

        if status_col:
            df = clean_status(df, status_col)
            df['_is_done'] = df[status_col].apply(is_done)
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if date_col and status_col:
            df['_date_status'] = df.apply(lambda r: get_date_status(r[date_col], r[status_col]), axis=1)

    with st.expander("📋 View Raw Data"):
        st.dataframe(
            df.drop(columns=[c for c in ['_is_done', '_date_status'] if c in df.columns]),
            use_container_width=True
        )

    # Sidebar filters
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filters")
    df_filtered = df.copy()

    if category_col:
        cat_opts = ['All'] + sorted(df[category_col].dropna().astype(str).unique().tolist())
        sel_cat = st.sidebar.selectbox("Category", cat_opts)
        if sel_cat != 'All':
            df_filtered = df_filtered[df_filtered[category_col].astype(str) == sel_cat]

    if status_col:
        stat_opts = ['All'] + sorted(df[status_col].dropna().unique().tolist())
        sel_stat = st.sidebar.selectbox("Status", stat_opts)
        if sel_stat != 'All':
            df_filtered = df_filtered[df_filtered[status_col] == sel_stat]

    today = pd.Timestamp(datetime.now().date())

    if date_col:
        st.sidebar.markdown("#### 📅 Due Date")
        date_filter = st.sidebar.radio("Show:", [
            "All Tasks", "With Due Dates Only",
            "Overdue Only", "Due This Week", "No Due Date"
        ])
        if date_filter == "With Due Dates Only":
            df_filtered = df_filtered[df_filtered[date_col].notna()]
        elif date_filter == "Overdue Only" and '_date_status' in df_filtered:
            df_filtered = df_filtered[df_filtered['_date_status'] == 'overdue']
        elif date_filter == "Due This Week" and '_date_status' in df_filtered:
            df_filtered = df_filtered[df_filtered['_date_status'].isin(['due_soon', 'overdue'])]
        elif date_filter == "No Due Date":
            df_filtered = df_filtered[df_filtered[date_col].isna()]

    if task_col:
        search = st.sidebar.text_input("🔎 Search tasks:")
        if search:
            df_filtered = df_filtered[
                df_filtered[task_col].astype(str).str.contains(search, case=False, na=False)
            ]

    # ── METRICS ──
    st.markdown("## 📈 Key Metrics")
    total = len(df_filtered)
    m1, m2, m3, m4, m5, m6 = st.columns(6)

    with m1:
        st.metric("📋 Total Rows", total)
    with m2:
        if status_col and '_is_done' in df_filtered:
            done_count = int(df_filtered['_is_done'].sum())
            pct = f"{done_count/total*100:.1f}%" if total > 0 else "0%"
            st.metric("✅ Completed", done_count, pct)
        else:
            st.metric("✅ Completed", "N/A")
    with m3:
        if status_col and '_is_done' in df_filtered:
            pending_count = int((~df_filtered['_is_done']).sum())
            st.metric("⏳ Pending", pending_count)
        else:
            st.metric("⏳ Pending", "N/A")
    with m4:
        if '_date_status' in df_filtered.columns:
            overdue_count = int((df_filtered['_date_status'] == 'overdue').sum())
            st.metric("🚨 Overdue", overdue_count)
        else:
            st.metric("🚨 Overdue", "N/A")
    with m5:
        if '_date_status' in df_filtered.columns:
            due_soon = int((df_filtered['_date_status'] == 'due_soon').sum())
            st.metric("⚠️ Due This Week", due_soon)
        else:
            st.metric("⚠️ Due This Week", "N/A")
    with m6:
        if date_col:
            no_date = int(df_filtered[date_col].isna().sum())
            st.metric("📅 No Due Date", no_date)
        else:
            st.metric("📅 No Due Date", "N/A")

    if status_col and total > 0 and '_is_done' in df_filtered.columns:
        progress = float(df_filtered['_is_done'].sum() / total)
        st.progress(progress)
        st.caption(f"Overall Completion: {progress*100:.1f}%  ({int(df_filtered['_is_done'].sum())} of {total})")

    st.markdown("---")

    # ── CHARTS ──
    st.markdown("## 📊 Analytics")
    ch1, ch2 = st.columns(2)

    with ch1:
        if category_col:
            cc = df_filtered[category_col].value_counts().reset_index()
            cc.columns = ['Category', 'Count']
            fig1 = px.pie(cc, values='Count', names='Category',
                          title="Tasks by Category", hole=0.4)
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No category column found. Add a column like 'Category', 'Department', or 'Type'.")

    with ch2:
        if status_col:
            sc = df_filtered[status_col].value_counts().reset_index()
            sc.columns = ['Status', 'Count']
            color_map = {}
            for s in sc['Status']:
                if is_done(s):
                    color_map[s] = '#22c55e'
                elif any(k in s.lower() for k in ['overdue', 'late']):
                    color_map[s] = '#ef4444'
                elif any(k in s.lower() for k in ['progress', 'active', 'ongoing']):
                    color_map[s] = '#3b82f6'
                else:
                    color_map[s] = '#f59e0b'
            fig2 = px.bar(sc, x='Status', y='Count', title="Tasks by Status",
                          color='Status', color_discrete_map=color_map)
            fig2.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No status column found.")

    if '_date_status' in df_filtered.columns and df_filtered['_date_status'].notna().any():
        label_map = {
            'overdue': '🔴 Overdue', 'due_soon': '🟡 Due This Week',
            'on_track': '🟢 On Track', 'completed': '✅ Completed', 'no_date': '⚪ No Date'
        }
        color_map2 = {
            '🔴 Overdue': '#ef4444', '🟡 Due This Week': '#f59e0b',
            '🟢 On Track': '#22c55e', '✅ Completed': '#3b82f6', '⚪ No Date': '#9ca3af'
        }
        ds = df_filtered['_date_status'].value_counts().reset_index()
        ds.columns = ['status', 'count']
        ds['label'] = ds['status'].map(label_map)
        fig3 = px.pie(ds, values='count', names='label',
                      title="Due Date Status Distribution",
                      color='label', color_discrete_map=color_map2)
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig3, use_container_width=True)

    if date_col and '_date_status' in df_filtered.columns:
        tl = df_filtered[df_filtered[date_col].notna()].copy()
        if len(tl) > 0 and task_col:
            c_map = {'overdue': 'red', 'due_soon': 'orange',
                     'on_track': 'green', 'completed': 'blue', 'no_date': 'gray'}
            hover = [task_col] + ([status_col] if status_col else [])
            fig4 = px.scatter(tl, x=date_col, y=tl.index,
                              color='_date_status', color_discrete_map=c_map,
                              hover_data=hover, title="Task Timeline by Due Date")
            fig4.add_vline(x=datetime.now(), line_dash="dash",
                           line_color="red", annotation_text="Today")
            fig4.update_layout(height=450, yaxis_title="Row #")
            st.plotly_chart(fig4, use_container_width=True)

    # ── GENERAL ANALYZER MODE (v2) ──
    # For ANY dataset, auto-chart category columns and numeric columns.
    used_cols = [c for c in [task_col, status_col, date_col, category_col] if c]
    extra_cats, extra_nums = general_analysis(df_filtered, used_cols)

    if extra_cats or extra_nums:
        st.markdown("---")
        st.markdown("## 🔍 General Data Analysis")
        st.caption("Auto-generated charts from other columns in your data.")

        # Numeric summary metrics
        if extra_nums:
            st.markdown("#### 📐 Numeric Summaries")
            num_cols_display = st.columns(min(len(extra_nums), 4))
            for i, ncol in enumerate(extra_nums[:4]):
                with num_cols_display[i]:
                    avg = df_filtered[ncol].mean()
                    total = df_filtered[ncol].sum()
                    st.metric(f"Avg {ncol}", f"{avg:,.1f}")
                    st.caption(f"Total: {total:,.0f}")

        # Category charts (pie) + numeric breakdowns (bar)
        gen1, gen2 = st.columns(2)

        with gen1:
            if extra_cats:
                pick_cat = st.selectbox("📊 Chart a category column:", extra_cats, key="gen_cat")
                vc = df_filtered[pick_cat].value_counts().head(15).reset_index()
                vc.columns = [pick_cat, 'Count']
                figc = px.pie(vc, values='Count', names=pick_cat,
                              title=f"Distribution by {pick_cat}", hole=0.4)
                figc.update_traces(textposition='inside', textinfo='percent+label')
                figc.update_layout(height=400)
                st.plotly_chart(figc, use_container_width=True)

        with gen2:
            if extra_nums and extra_cats:
                pick_num = st.selectbox("📈 Sum a number by category:", extra_nums, key="gen_num")
                pick_by = st.selectbox("Grouped by:", extra_cats, key="gen_by")
                grouped = df_filtered.groupby(pick_by)[pick_num].sum().sort_values(
                    ascending=False).head(15).reset_index()
                fign = px.bar(grouped, x=pick_by, y=pick_num,
                              title=f"Total {pick_num} by {pick_by}")
                fign.update_layout(height=400)
                st.plotly_chart(fign, use_container_width=True)
            elif extra_nums:
                pick_num = st.selectbox("📈 Number column distribution:", extra_nums, key="gen_num2")
                fign = px.histogram(df_filtered, x=pick_num,
                                    title=f"Distribution of {pick_num}")
                fign.update_layout(height=400)
                st.plotly_chart(fign, use_container_width=True)

    st.markdown("---")

    # ── DETAILED TASK VIEW ──
    st.markdown("## 📋 Detailed Task View")

    if category_col:
        categories_list = sorted(df_filtered[category_col].dropna().astype(str).unique().tolist())
        for cat in categories_list:
            cat_df = df_filtered[df_filtered[category_col].astype(str) == cat].copy()
            done_in_cat = int(cat_df['_is_done'].sum()) if '_is_done' in cat_df.columns else 0
            overdue_in_cat = int((cat_df.get('_date_status', pd.Series()) == 'overdue').sum())
            with st.expander(
                f"**{cat}** — {len(cat_df)} tasks | ✅ {done_in_cat} done | 🚨 {overdue_in_cat} overdue",
                expanded=False
            ):
                render_tasks(cat_df, task_col, status_col, date_col, today)
    else:
        render_tasks(df_filtered, task_col, status_col, date_col, today)

    # ── UPCOMING DEADLINES ──
    if date_col:
        st.markdown("---")
        st.markdown("## ⏰ Upcoming Deadlines (Next 30 Days)")
        future = today + timedelta(days=30)
        upcoming = df_filtered[
            (df_filtered[date_col].notna()) &
            (df_filtered[date_col] >= today) &
            (df_filtered[date_col] <= future)
        ].copy()
        if status_col and '_is_done' in upcoming.columns:
            upcoming = upcoming[~upcoming['_is_done']]
        upcoming = upcoming.sort_values(date_col)

        if len(upcoming) > 0:
            for _, row in upcoming.iterrows():
                d = pd.to_datetime(row[date_col])
                days_left = (d.date() - today.date()).days
                uc1, uc2, uc3 = st.columns([3, 1.5, 1])
                with uc1:
                    st.write(str(row[task_col])[:80] if task_col else "—")
                with uc2:
                    if days_left <= 3:
                        st.error(f"🚨 {d.strftime('%d-%b-%Y')} ({days_left}d)")
                    elif days_left <= 7:
                        st.warning(f"⚠️ {d.strftime('%d-%b-%Y')} ({days_left}d)")
                    else:
                        st.info(f"📅 {d.strftime('%d-%b-%Y')} ({days_left}d)")
                with uc3:
                    if category_col and pd.notna(row.get(category_col)):
                        st.caption(str(row[category_col]))
        else:
            st.success("✅ No upcoming deadlines in the next 30 days!")

    # ── GROQ AI SECTION ──
    st.markdown("---")
    st.markdown("## 🤖 AI Insights (Groq)")

    if groq_api_key:
        summary_text = build_summary(df_filtered, status_col, date_col, category_col, task_col)

        ai1, ai2 = st.columns(2)
        with ai1:
            if st.button("📊 Generate Summary"):
                with st.spinner("Groq AI is analyzing..."):
                    prompt = (
                        f"Dataset summary:\n{summary_text}\n\n"
                        "Give a clear 5-point insight summary. "
                        "What needs attention? What is on track? Any risks?"
                    )
                    st.success(call_groq(groq_api_key, prompt))

        with ai2:
            if st.button("🚨 What Should I Focus On?"):
                with st.spinner("Groq AI is thinking..."):
                    prompt = (
                        f"Dataset summary:\n{summary_text}\n\n"
                        "What are the top 3 priorities the team should focus on right now? Be specific."
                    )
                    st.warning(call_groq(groq_api_key, prompt))

        st.markdown("#### 💬 Ask Anything About Your Data")
        user_q = st.text_input("Your question:", placeholder="e.g. Which category has the most overdue tasks?")
        if st.button("Ask AI") and user_q:
            with st.spinner("Thinking..."):
                prompt = (
                    f"You are analyzing a dataset. Here is the full summary with exact numbers:\n{summary_text}\n\n"
                    f"Question: {user_q}\n\n"
                    "Answer the question DIRECTLY using the numbers in the summary above. "
                    "Do NOT write code. Do NOT say you need the dataset \u2014 you already have the "
                    "numbers. Give a clear, specific answer in plain English."
                )
                st.info(call_groq(groq_api_key, prompt))
    else:
        st.info("🔑 Add your Groq API key in the sidebar to enable AI insights and chat with your data.")

    # ── EXPORT ──
    st.markdown("---")
    st.markdown("## 💾 Export")
    export_df = df_filtered.drop(columns=[c for c in ['_is_done', '_date_status'] if c in df_filtered.columns])

    ex1, ex2, ex3 = st.columns(3)
    with ex1:
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Filtered Data (CSV)", csv,
                           f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")
    with ex2:
        if '_date_status' in df_filtered.columns:
            ov = df_filtered[df_filtered['_date_status'] == 'overdue'].drop(
                columns=[c for c in ['_is_done', '_date_status'] if c in df_filtered.columns])
            csv2 = ov.to_csv(index=False).encode('utf-8')
            st.download_button("🚨 Overdue Tasks (CSV)", csv2,
                               f"overdue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")
    with ex3:
        if category_col:
            rows = []
            for cat in df_filtered[category_col].dropna().unique():
                cdf = df_filtered[df_filtered[category_col] == cat]
                rows.append({
                    'Category': cat,
                    'Total': len(cdf),
                    'Completed': int(cdf['_is_done'].sum()) if '_is_done' in cdf.columns else 0,
                    'Pending': int((~cdf['_is_done']).sum()) if '_is_done' in cdf.columns else 0,
                    'Overdue': int((cdf.get('_date_status', pd.Series()) == 'overdue').sum()),
                    'No Due Date': int(cdf[date_col].isna().sum()) if date_col else 0
                })
            csv3 = pd.DataFrame(rows).to_csv(index=False).encode('utf-8')
            st.download_button("📊 Summary Report (CSV)", csv3,
                               f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv")

# ─────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────
else:
    st.markdown("### 👋 Welcome! Upload any data file to get started.")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("#### 📊 Excel / CSV")
        st.write("Any spreadsheet — any column structure. Works automatically.")
    with c2:
        st.markdown("#### 📄 PDF")
        st.write("PDFs that contain tables. Text-only PDFs are not supported.")
    with c3:
        st.markdown("#### 📝 Word (.docx)")
        st.write("Word documents that contain data tables.")
    with c4:
        st.markdown("#### 🤖 Groq AI")
        st.write("Add your Groq API key to ask questions about your data.")

    st.markdown("---")
    st.markdown("### 📋 What the Dashboard Auto-Detects From Any File")
    st.markdown("""
    - ✅ **Task / Description column** — the main text column
    - ✅ **Status column** — Done, Pending, In Progress, Completed, Closed, etc.
    - ✅ **Due Date column** — EDD, Deadline, Due Date, Target Date, End Date, etc.
    - ✅ **Category column** — Department, Module, Type, Group, Team, etc.
    - ✅ **Overdue tasks** — automatically calculated from today's date
    - ✅ **Empty statuses** — automatically treated as Pending
    - ✅ **Column override** — you can manually correct any auto-detected column
    """)
    st.info("💡 **This works with any Excel, CSV, PDF or Word file — not just one specific format!**")

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("---")
st.caption("📊 Universal Data Dashboard | Python · Streamlit · Pandas · Plotly · Groq AI")