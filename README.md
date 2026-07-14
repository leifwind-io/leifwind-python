# leifwind-stream-client

Python client for the Leifwind Stream metadata-driven REST API.

## Install

```
pip install leifwind-stream-client \
  --extra-index-url https://gitlab.com/api/v4/projects/internal/packages/pypi/simple
```

## Usage

```python
from leifwind.stream.client import Leifwind

async with Leifwind("https://leifwind.example.com", auth="<token>") as lw:
    async for project in lw.metadata.iter_projects():
        print(project.name)
```

Licensed under MPL-2.0 (see LICENSE).
