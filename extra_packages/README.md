# Extra Packages

This is a holding place for packages which were altered but have not been hosted on PyPI.

To install these:

1. Get into venv
2. easy_install extra_packages/<package_name>
3. Verify its contents in venv/Lib/site-packages/

## Rationale for SQLAlchemy-Continuum

https://github.com/kvesteri/sqlalchemy-continuum/issues/123

You can see my commented-out lines in `fetcher.py`.

---

Wasn't having luck with the above method for flask-bootstrap. It was install .egg/ folder in site-packages, but the egg-info/ and package/ folders weren't extracted correctly.
Would have had to manually moved them. Decided easier to just point to extra_packages/ on import.