# leifwind-stream-client

Python client for the Leifwind Stream metadata-driven REST API.

The source lives at
[github.com/leifwind-io/leifwind-python](https://github.com/leifwind-io/leifwind-python),
a read-only mirror of a private monorepo; see `CONTRIBUTING.md`.

## Install

Each [release](https://github.com/leifwind-io/leifwind-python/releases) carries
the wheel and the sdist. Install the wheel of the release you want, with
`<version>` such as `0.10.0`:

```
pip install https://github.com/leifwind-io/leifwind-python/releases/download/v<version>/leifwind_stream_client-<version>-py3-none-any.whl
```

## Build from source

The version comes from the monorepo's release tags, which the mirror does not
carry, so a build from a clone names it explicitly (the mirror's tag without
the `v`):

```
SETUPTOOLS_SCM_PRETEND_VERSION=<version> uv build
uv run --group dev pytest
```

## Usage

```python
from leifwind.stream.client import Leifwind

async with Leifwind("https://leifwind.example.com", auth="<token>") as lw:
    async for project in lw.metadata.iter_projects():
        print(project.name)
```

Licensed under MPL-2.0 (see LICENSE).
