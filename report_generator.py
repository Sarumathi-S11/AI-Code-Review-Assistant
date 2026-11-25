from html import escape

def generate_html_report(result):
    rows = ""
    for item in result["issues"]:
        rows += f"<tr><td>{escape(str(item.get('line','')))}</td><td>{escape(item['severity'])}</td><td>{escape(item['name'])}</td><td>{escape(item['description'])}</td><td>{escape(item['suggestion'])}</td></tr>"
    if not rows:
        rows = '<tr><td colspan="5">No configured issues detected.</td></tr>'
    m = result["metrics"]
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Code Review Report</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;color:#172033}}h1{{color:#183b65}}.summary{{display:flex;gap:14px;flex-wrap:wrap}}.tile{{background:#edf3fb;padding:16px;border-radius:10px}}table{{border-collapse:collapse;width:100%;margin-top:20px}}th,td{{border:1px solid #d8e0ea;padding:10px;text-align:left}}th{{background:#183b65;color:white}}tr:nth-child(even){{background:#f5f7fa}}</style></head><body>
<h1>AI Code Review Report</h1><p><b>File:</b> {escape(result['filename'])}<br><b>Reviewed:</b> {escape(result['timestamp'])}</p>
<div class="summary"><div class="tile"><b>Score</b><h2>{result['review_score']}/100</h2>{escape(result['grade'])}</div><div class="tile"><b>Total issues</b><h2>{result['total_issues']}</h2></div><div class="tile"><b>Complexity</b><h2>{m['cyclomatic_complexity']}</h2></div><div class="tile"><b>Functions / Classes</b><h2>{m['functions']} / {m['classes']}</h2></div></div>
<h2>Code metrics</h2><p>Total lines: {m['total_lines']} | Code lines: {m['code_lines']} | Blank lines: {m['blank_lines']} | Comment lines: {m['comment_lines']} | Comment ratio: {m['comment_ratio']}%</p>
<h2>Findings and suggestions</h2><table><tr><th>Line</th><th>Severity</th><th>Rule</th><th>Finding</th><th>Suggestion</th></tr>{rows}</table>
<p><small>Educational static-analysis report. Findings may include false positives.</small></p></body></html>"""
