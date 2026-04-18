# DoScript Regressions

This folder contains lightweight regression checks for parser, control-flow,
and recently added language features.

Run them with:

```bash
py regressions/run_regressions.py
```

The runner uses temporary files and a loopback HTTP server. It does not
require internet access.
