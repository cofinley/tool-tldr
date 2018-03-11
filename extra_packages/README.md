# Extra Packages

This is a holding place for packages which were altered but have not been hosted on PyPI.

To install these:

1. Get into venv
2. easy_install extra_packages/<package_name>
3. Verify its contents in venv/Lib/site-packages/

---

Wasn't having luck with the above method. It was install .egg/ folder in site-packages, but the egg-info/ and package/ folders weren't extracted correctly.
Would have had to manually moved them. Decided easier to just point to extra_packages/ on import.