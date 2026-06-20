import ast
import os
import subprocess
import sys
import json
import urllib.request

violations = []

# ----------------------------

# 1. pycodestyle check

# ----------------------------

result = subprocess.run(
["pycodestyle", "."],
capture_output=True,
text=True
)

if result.stdout:
violations.append("### Pycodestyle Violations\n" + result.stdout)

# ----------------------------

# 2. File length check

# ----------------------------

for root, dirs, files in os.walk("."):
if ".git" in root:
continue

```
for file in files:
    if file.endswith(".py"):
        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) > 100:
            violations.append(
                f"{path} has {len(lines)} lines (limit: 100)"
            )
```

# ----------------------------

# 3. Docstring check

# ----------------------------

for root, dirs, files in os.walk("."):
if ".git" in root:
continue

```
for file in files:
    if file.endswith(".py"):
        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    if ast.get_docstring(node) is None:
                        violations.append(
                            f"Missing docstring in function "
                            f"'{node.name}' ({path})"
                        )

        except Exception as e:
            violations.append(
                f"AST parsing failed for {path}: {e}"
            )
```

# ----------------------------

# PR Comment

# ----------------------------

if violations:

```
body = {
    "body":
    "## Code Quality Report\n\n" +
    "\n".join(
        f"- {v}" for v in violations
    )
}

token = os.getenv("GITHUB_TOKEN")
pr_number = os.getenv("PR_NUMBER")
repo = os.getenv("REPO")

if token and pr_number:

    url = (
        f"https://api.github.com/repos/"
        f"{repo}/issues/{pr_number}/comments"
    )

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Authorization":
            f"Bearer {token}",
            "Accept":
            "application/vnd.github+json",
            "Content-Type":
            "application/json"
        },
        method="POST"
    )

    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print("Failed to create PR comment:", e)

print("\n".join(violations))
sys.exit(1)
```

print("All quality checks passed.")
