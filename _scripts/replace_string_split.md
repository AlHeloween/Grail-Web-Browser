---
TurnID: 5
SourceFile: replace_string_split.md
ProjectRoot: .
SVM: "#svm: Replace deprecated string.split with str.split"
BlockUpdates:
  - RelativePath: grail.py
    FindFromRegex: "string.split(e.args[0])"
    FindToRegex: ")"
    ContentBlockName: replace_split
    SemanticDominant: "Replace deprecated string.split with str.split"
---

```python replace_split
e.args[0].split()
```
