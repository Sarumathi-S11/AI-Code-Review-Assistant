import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from code_analyzer import CodeReviewAssistant
from report_generator import generate_html_report

st.set_page_config(page_title="AI Code Review Assistant", page_icon="🔍", layout="wide")
ROOT = Path(__file__).parent
HISTORY = ROOT / "data" / "review_history.json"
assistant = CodeReviewAssistant()

st.markdown("""
<style>
.main {background:#0b1220}
.block-container {padding-top:2rem; max-width:1400px}
[data-testid="stMetric"] {background:#141f33;padding:18px;border-radius:14px;border:1px solid #263650}
div.stButton>button {border-radius:10px;font-weight:600}
.hero {padding:26px;border-radius:18px;background:linear-gradient(120deg,#172b4d,#243b63);border:1px solid #36527c}
.hero h1 {color:#f8fafc;margin-bottom:5px}
.hero p {color:#cbd5e1}
</style>
""", unsafe_allow_html=True)

def load_history():
    if HISTORY.exists():
        try: return json.loads(HISTORY.read_text(encoding="utf-8"))
        except Exception: return []
    return []

def save_history(item):
    data = load_history()
    data.append(item)
    HISTORY.write_text(json.dumps(data, indent=2), encoding="utf-8")

st.markdown('<div class="hero"><h1>🔍 AI Code Review Assistant</h1><p>Analyze Python code • Detect code smells • Measure quality • Get actionable refactoring advice</p></div>', unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", ["Code Review", "Dashboard", "About"])
st.sidebar.caption("AI-SD-003 | Python Static Analysis")

if page == "Code Review":
    st.subheader("Submit Python code")
    uploaded = st.file_uploader("Upload a .py file", type=["py"])
    default_code = """def calculate_total(price, quantity, tax_rate, discount_rate, shipping_cost):
    subtotal = price * quantity
    tax = subtotal * tax_rate
    discount = subtotal * discount_rate
    total = subtotal + tax - discount + shipping_cost
    return total

class data_processor:
    def process_data(self):
        try:
            result = self.data[0] / 0
        except:
            pass
        return result
"""
    code = uploaded.getvalue().decode("utf-8", errors="replace") if uploaded else default_code
    filename = uploaded.name if uploaded else "sample_code.py"
    code = st.text_area("Code editor", value=code, height=330)
    run = st.button("🚀 Analyze Code", type="primary", use_container_width=True)
    st.caption("The analyzer parses source code without executing it.")
    if run:
        result = assistant.analyze_code(code, filename)
        if not result["success"]:
            st.error(result["error"])
        else:
            review = result["result"]
            save_history(review)
            st.session_state["last_review"] = review
            st.success("Code review completed!")
    review = st.session_state.get("last_review")
    if review:
        st.divider()
        st.subheader(f"Review results — {review['filename']}")
        m = review["metrics"]
        a,b,c,d = st.columns(4)
        a.metric("Quality score", f"{review['review_score']}/100", review["grade"])
        b.metric("Issues found", review["total_issues"])
        c.metric("Cyclomatic complexity", m["cyclomatic_complexity"])
        d.metric("Functions / Classes", f"{m['functions']} / {m['classes']}")
        left,right = st.columns(2)
        with left:
            st.markdown("#### Severity breakdown")
            sev = review["severity_summary"] or {"No issues":1}
            st.plotly_chart(px.pie(names=list(sev.keys()), values=list(sev.values()), hole=.55), use_container_width=True)
        with right:
            st.markdown("#### Code metrics")
            metric_df = pd.DataFrame({"Metric":["Code lines","Blank lines","Comment lines"],"Count":[m["code_lines"],m["blank_lines"],m["comment_lines"]]})
            st.plotly_chart(px.bar(metric_df,x="Metric",y="Count",color="Metric"), use_container_width=True)
        st.markdown("#### Findings")
        if review["issues"]:
            for issue in review["issues"]:
                color = {"HIGH":"🔴","MEDIUM":"🟠","LOW":"🟡","CRITICAL":"🚨"}.get(issue["severity"],"ℹ️")
                with st.expander(f"{color} {issue['severity']} · {issue['name']} · Line {issue.get('line','—')}"):
                    st.write(issue["description"])
                    st.info("Suggestion: " + issue["suggestion"])
                    st.caption("ML predicted category: " + issue.get("ml_category", "Not available"))
        else:
            st.success("No configured issues detected.")
        html = generate_html_report(review)
        st.download_button("⬇️ Download HTML report", html, file_name="code_review_report.html", mime="text/html")
        st.download_button("⬇️ Download JSON report", json.dumps(review, indent=2), file_name="code_review_report.json", mime="application/json")

elif page == "Dashboard":
    st.subheader("Review dashboard")
    history = load_history()
    if not history:
        st.info("No reviews yet. Run an analysis in Code Review to populate this dashboard.")
    else:
        df = pd.DataFrame(history)
        x,y,z = st.columns(3)
        x.metric("Total reviews", len(history))
        y.metric("Total issues", int(df["total_issues"].sum()))
        z.metric("Average score", f"{df['review_score'].mean():.1f}/100")
        st.plotly_chart(px.line(df.reset_index(), x="index", y="review_score", markers=True, title="Review score history"), use_container_width=True)
        st.dataframe(df[["filename","timestamp","total_issues","review_score","grade"]], use_container_width=True)
        if st.button("Clear review history"):
            HISTORY.write_text("[]", encoding="utf-8")
            st.rerun()
else:
    st.subheader("About this project")
    st.write("An educational static-analysis assistant for Python source code. It uses Python AST rules, style checks, maintainability metrics, and an optional scikit-learn classifier.")
    st.markdown("""
    **Core modules**
    - `code_analyzer.py` — AST parsing, code-smell detection, style and naming checks.
    - `ml_classifier.py` — ML issue classifier trained on a small transparent example dataset.
    - `report_generator.py` — downloadable HTML report generation.
    - `data/review_history.json` — local JSON review history; no database required.

    **Important:** This is a learning tool, not a replacement for professional security review, testing, or tools such as Ruff, Pylint, Bandit, and mypy.
    """)
