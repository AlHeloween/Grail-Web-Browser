---
TurnID: 4
SourceFile: enable_cache_on_windows.md
ProjectRoot: .
SVM: "#svm: Enable disk cache on Windows"
BlockUpdates:
  - RelativePath: grail.py
    FindFromRegex: "    # XXX Disable cache for NT"
    FindToRegex: "prefs.Set('disk-cache', 'size', '0')"
    ContentBlockName: empty
    SemanticDominant: "Remove code that disables disk cache on Windows"
---

```python empty

```
