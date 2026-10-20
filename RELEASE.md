# Release guide

## Setting up PyPI access

Before publishing, you need to configure PyPI API tokens as Gitea repository secrets.

### Production PyPI

1. Create an [API token](https://pypi.org/manage/account/token/) with full access to the `alpyki` project
2. In the Gitea repository settings, navigate to **Settings > Actions > Secrets**
3. Add a new secret named `PYPI_TOKEN` with the API token value

### TestPyPI (for testing releases)

1. Create an [API token](https://test.pypi.org/manage/account/token/)
2. In the Gitea repository settings, navigate to **Settings > Actions > Secrets**
3. Add a new secret named `TESTPYPI_TOKEN` with the API token value

## Automated release

The CI workflow triggers automatically on tag push:

```bash
# Test release to TestPyPI
git tag test-v0.1.7
git push origin test-v0.1.7

# Production release to PyPI
git tag v0.1.7
git push origin v0.1.7
```

The workflow will:

1. Build the sdist and wheel using `python -m build`
2. Validate the package version matches the tag
3. Upload to PyPI (or TestPyPI for `test-v*` tags)

## Manual release

If you need to publish manually (e.g., CI is unavailable):

```bash
# Build the distribution packages
python -m build

# Upload to PyPI (requires twine)
python -m twine upload dist/ --username __token__ --token $PYPI_TOKEN

# Or upload to TestPyPI for testing
python -m twine upload dist/ --repository testpypi --username __token__ --token $TESTPYPI_TOKEN
```

Install build tools if needed:

```bash
pip install build twine
```

## Version management

The package version is automatically derived from git tags using `setuptools-scm`. The `v` prefix is stripped
automatically (e.g., tag `v0.1.7` produces version `0.1.7`).

No manual version editing is required. Simply push the appropriately formatted tag.
