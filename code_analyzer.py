import ast
import re
from datetime import datetime
from collections import Counter
from ml_classifier import IssueClassifier

class CodeReviewAssistant:
    """Analyze Python source using AST and lightweight static rules."""
    def __init__(self):
        self.classifier = IssueClassifier()

    def _issue(self, name, description, severity, category, line, suggestion, issue_type="static"):
        return {"type": issue_type, "name": name, "description": description,
                "severity": severity, "category": category, "line": line,
                "suggestion": suggestion}

    def analyze_code(self, code, filename="code.py"):
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return {"success": False, "error": f"Syntax error at line {exc.lineno}: {exc.msg}", "line": exc.lineno}
        lines = code.splitlines()
        issues = []
        for number, line in enumerate(lines, 1):
            if len(line) > 79:
                issues.append(self._issue("line_too_long", f"Line {number} has {len(line)} characters (limit: 79).", "LOW", "Style", number, "Break the expression across multiple lines."))
            if line.rstrip(" \t") != line:
                issues.append(self._issue("trailing_whitespace", f"Trailing whitespace on line {number}.", "LOW", "Style", number, "Remove spaces or tabs at the end of the line."))
            if ";" in line and not line.lstrip().startswith("#"):
                issues.append(self._issue("multiple_statements", f"Possible multiple statements on line {number}.", "LOW", "Style", number, "Place each statement on its own line."))

        imports = []
        used_names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    imports.append((alias.asname or alias.name.split(".")[0], node.lineno))
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = getattr(node, "end_lineno", node.lineno)
                length = end - node.lineno + 1
                if length > 50:
                    issues.append(self._issue("long_function", f'Function "{node.name}" spans {length} lines.', "HIGH", "Maintainability", node.lineno, "Split the function into smaller, single-purpose functions."))
                args = node.args
                count = len(args.posonlyargs) + len(args.args) + len(args.kwonlyargs)
                if args.vararg: count += 1
                if args.kwarg: count += 1
                if count > 5:
                    issues.append(self._issue("too_many_parameters", f'Function "{node.name}" has {count} parameters.', "MEDIUM", "Maintainability", node.lineno, "Group related values into a dataclass or configuration object."))
                if not ast.get_docstring(node):
                    issues.append(self._issue("missing_docstring", f'Function "{node.name}" has no docstring.', "MEDIUM", "Documentation", node.lineno, "Add a concise docstring describing purpose, parameters, and return value."))
                if not re.match(r"^[a-z_][a-z0-9_]*$", node.name) and not (node.name.startswith("__") and node.name.endswith("__")):
                    issues.append(self._issue("function_naming", f'Function "{node.name}" is not snake_case.', "LOW", "Naming", node.lineno, "Rename the function using snake_case."))
            elif isinstance(node, ast.ClassDef):
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                    issues.append(self._issue("class_naming", f'Class "{node.name}" is not PascalCase.', "LOW", "Naming", node.lineno, "Rename the class using PascalCase."))
                methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                if len(methods) > 20:
                    issues.append(self._issue("god_class", f'Class "{node.name}" has {len(methods)} methods.', "HIGH", "Maintainability", node.lineno, "Split responsibilities across smaller classes."))
            elif isinstance(node, ast.ExceptHandler):
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    issues.append(self._issue("empty_except", "An except block silently ignores an exception.", "MEDIUM", "Error Handling", node.lineno, "Handle the exception explicitly or log it; avoid a bare except."))
                if node.type is None:
                    issues.append(self._issue("bare_except", "A bare except catches all exception types.", "MEDIUM", "Error Handling", node.lineno, "Catch the specific exception types expected."))
            elif isinstance(node, ast.If):
                depth = self._nesting_depth(node)
                if depth > 4:
                    issues.append(self._issue("deep_nesting", f"Conditional nesting depth is {depth}.", "HIGH", "Maintainability", node.lineno, "Use guard clauses, early returns, or extract nested logic."))

        for name, line_no in imports:
            if name not in used_names:
                issues.append(self._issue("unused_import", f'Imported name "{name}" does not appear to be used.', "LOW", "Style", line_no, "Remove the unused import or use it in the module."))

        seen = {}
        for number, line in enumerate(lines, 1):
            normalized = line.strip()
            if len(normalized) >= 12 and not normalized.startswith("#"):
                if normalized in seen:
                    issues.append(self._issue("duplicate_line", f"Line duplicates line {seen[normalized]}.", "LOW", "Maintainability", number, "Consider extracting repeated logic into a reusable function."))
                else:
                    seen[normalized] = number

        metrics = self.calculate_metrics(tree, code)
        for issue in issues:
            issue["ml_category"] = self.classifier.predict(issue["description"])
        score = self.calculate_score(issues, metrics)
        severity = Counter(i["severity"] for i in issues)
        categories = Counter(i["category"] for i in issues)
        result = {"filename": filename, "timestamp": datetime.now().isoformat(timespec="seconds"),
                  "total_issues": len(issues), "issues": issues, "metrics": metrics,
                  "review_score": score, "grade": self.grade(score),
                  "severity_summary": dict(severity), "category_summary": dict(categories)}
        return {"success": True, "result": result}

    def _nesting_depth(self, node, depth=1):
        children = [n for n in ast.iter_child_nodes(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With))]
        return max([depth] + [self._nesting_depth(child, depth + 1) for child in children])

    def calculate_metrics(self, tree, code):
        lines = code.splitlines()
        blank = sum(not line.strip() for line in lines)
        comments = sum(line.strip().startswith("#") for line in lines)
        functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
        classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.With, ast.Assert, ast.comprehension)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += max(0, len(node.values) - 1)
        total = len(lines)
        return {"total_lines": total, "code_lines": max(0, total - blank - comments),
                "blank_lines": blank, "comment_lines": comments,
                "comment_ratio": round(comments / max(total, 1) * 100, 1),
                "functions": functions, "classes": classes, "cyclomatic_complexity": complexity}

    def calculate_score(self, issues, metrics):
        deductions = {"CRITICAL": 15, "HIGH": 10, "MEDIUM": 5, "LOW": 2}
        score = 100 - sum(deductions.get(i["severity"], 0) for i in issues)
        if metrics["cyclomatic_complexity"] > 20: score -= 10
        elif metrics["cyclomatic_complexity"] > 10: score -= 5
        return max(0, min(100, score))

    def grade(self, score):
        if score >= 90: return "A — Excellent"
        if score >= 80: return "B — Good"
        if score >= 70: return "C — Fair"
        if score >= 60: return "D — Needs improvement"
        return "F — Poor"
