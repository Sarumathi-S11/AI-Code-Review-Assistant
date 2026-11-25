# AI Code Review Assistant (AI-SD-003)

A Python static-analysis project using `ast`, PEP 8-inspired rules, code-smell heuristics, code metrics, and a small scikit-learn classifier.

## Features
- AST parsing and syntax-error reporting
- Long-line, trailing-whitespace, and multiple-statement checks
- Long functions, too many parameters, deep nesting, empty/bare `except`
- Naming and missing-docstring checks
- Unused-import heuristic and duplicate-line detection
- Cyclomatic complexity and code metrics
- Quality score and grade
- TF-IDF + Multinomial Naive Bayes issue-category prediction
- Streamlit dashboard and JSON review history
- Downloadable HTML and JSON reports

## Run on Windows (VS Code)
1. Extract the ZIP and open the project folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate it:
   ```bash
   venv\Scripts\activate
   ```
5. Install packages:
   ```bash
   python -m pip install -r requirements.txt
   ```
6. Run:
   ```bash
   python -m streamlit run app.py
   ```
7. Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Project structure
```text
AI-Code-Review-Assistant/
├── app.py
├── code_analyzer.py
├── ml_classifier.py
├── report_generator.py
├── requirements.txt
├── README.md
├── data/review_history.json
└── sample_codes/
    ├── clean_code.py
    └── sample_issues.py
```

## Workflow
1. Upload a `.py` file or edit the sample code.
2. `ast.parse()` parses the source without executing it.
3. Rule checks identify configured style and maintainability issues.
4. Metrics and a review score are calculated.
5. The ML model predicts a broad category for each finding.
6. Download an HTML or JSON report.

## Limitations
This is an educational prototype. The classifier uses a small built-in demonstration dataset, not a large production training corpus. Static checks are heuristics and can produce false positives or miss issues. Uploaded code is not executed. This tool is not a security certification.

## Future enhancements
Integrate Ruff, Pylint, Radon, Bandit, more robust duplicate-block detection, automated tests, a larger labelled ML dataset, and GitHub Actions CI.
