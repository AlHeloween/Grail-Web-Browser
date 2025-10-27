---
TurnID: 6
SourceFile: fix_browser_docstring.md
ProjectRoot: .
SVM: "#svm: Fix duplicated docstring in Browser.py"
BlockUpdates:
  - RelativePath: Browser.py
    FindFromRegex: '"""The Browser class provides the top-level GUI.'
    FindToRegex: '"""'
    ContentBlockName: empty
    SemanticDominant: "Remove old docstring from Browser class"
---

```python empty

```
