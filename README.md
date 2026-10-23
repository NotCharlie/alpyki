# alpyki - *Al*fred *Py*thon *Ki*t

`alpyki` helps you create [Alfred](https://www.alfredapp.com/) workflows in Python. It started as a personal extension
of [`pyfred`](https://github.com/muffix/pyfred-cli.git)

It comes with a CLI that helps bootstrapping, maintaining and packaging the workflow.

Dependencies are vendored and packaged with the workflow so that they don't need to be installed into the system Python.
See the [section on adding dependencies](#adding-dependencies) for details.

## Installation

You can install directly from PyPI:

```shell
pip install alpyki
```

## Using the CLI

The CLI knows the following commands: `new`, `link`, `vendor`, `package`, `release`, `version`, `name`, `show-link`, `completion`.

See `alpyki <command> -h` for detailed help.

The CLI also supports a top-level `--version` flag to display the installed version of alpyki.

### New

Bootstraps a new workflow with a single script filter and links it into Alfred.

It creates a new directory with the given name and copies a "Hello Alfred" workflow there.
The workflow can be used immediately by invoking Alfred with the specified keyword.

The following example creates a `hello` directory containing a workflow that can be triggered with the `hi` keyword. The
result of the selected action is copied to the clipboard.

```shell
alpyki new hello -k hi -b de.muffix.helloalfred --author=Muffix --description="Hello Alfred"
```

By default, a GitHub Actions workflow for releases is included. Use `--actions gitea` to generate a Gitea Actions
workflow instead, `--actions gitlab` for GitLab CI, or `--actions none` to omit CI files entirely. The `--ci` flag
is an alias for `--actions`.

### Link

Executed from a directory bootstrapped by this CLI, it links or relinks the workflow into Alfred.

```shell
alpyki link
```

### Vendor

Downloads the dependencies listed in the `requirements.txt` file and vendors them into the `Workflow/vendored`
directory. Doing this avoids having to install them into the system Python interpreter.

```shell
alpyki vendor
```

### Package

Packages the workflow into a `*.alfredworkflow` file in the `dist` directory. The file contains the entire workflow and
all dependencies. It can be distributed and imported.

```shell
alpyki package
```

### Release

Updates the workflow version in `info.plist`, commits the change, creates an annotated git tag, and pushes both to the
remote. Use it to prepare a release for distribution through CI.

```shell
alpyki release --version 1.0.0
```

### Version

Prints the current version of the workflow as defined in `info.plist`.

```shell
alpyki version
```

### Name

Prints the name of the workflow as defined in `info.plist`.

```shell
alpyki name
```

### Show Link

Prints the path to the symbolic link in Alfred's installed workflows directory.

```shell
alpyki show-link
```

### Completion

Generates a shell completion script for auto-completion of commands and arguments. Add the appropriate
line to your shell's configuration file to enable completions:

#### Bash

Add to `~/.bashrc`:

```shell
eval "$(alpyki completion --shell bash)"
```

#### Zsh

Add to `~/.zshrc`:

```shell
eval "$(alpyki completion --shell zsh)"
```

#### Fish

Add to `~/.config/fish/config.fish`, or run `alpyki completion --shell fish > ~/.config/fish/completions/alpyki.fish`:

```shell
alpyki completion --shell fish | source
```

### Debug output

The CLI will log debug output if the `--debug` flag is passed before the command. Pass `--no-debug` to explicitly
disable it. Use `--version` to display the installed version of alpyki.

## Creating a workflow

The classes from the `alpyki.model` module represent the output expected by Alfred from a script filter.

`alpyki.workflow` provides a decorator for the entry point of a filter. It preprocesses the input and serialises the
response to stdout, where it is being picked up by the next input.

A minimal example for a script filter workflow looks like this:

```python
from alpyki.model import Environment, OutputItem, ScriptFilterOutput
from alpyki.workflow import script_filter

@script_filter
def main(script_path: Path, args_from_alfred: list[str], env: Optional[Environment]) -> ScriptFilterOutput:
    return ScriptFilterOutput(items=[OutputItem(title="Hello Alfred!")])
```

## Adding dependencies

When running the workflow, Alfred will use the system Python interpreter to run the script. Third-party libraries are
not available in the interpreter unless explicitly installed. In order to not pollute the system Python, dependencies
can be vendored with the workflow using the `alpyki vendor` command. It is also automatically run with `alpyki package`.

If you add dependencies to your `requirements.txt` file, you need to run `alpyki vendor` to download them. You do *not*
need to prefix the import with `vendored` because the template adds that directory to the `PYTHONPATH` variable when the
workflow runs.

## IDE setup

If you're using an IDE like PyCharm, you'll want to open the generated directory and set up the `Workflow` subdirectory
as the content root. Additionally, you should add the `Workflow/vendored` directory as source directory in the PyCharm
project settings. This helps it resolve the imports correctly.

## Adding icons

You can add an icon for your workflow to the `Workflow` directory in the generated skeleton.
The file name must be `icon.png`

You can assign individual icons to your output items. See the `alpyki.model.Icon` class for more details.

## Distribution through CI releases

The skeleton created by `alpyki new` comes with a CI action that creates a draft release whenever a tag starting
like `#.#.#` is pushed. To create a tag, run `git tag 1.0.0` and push it with `git push origin 1.0.0`. When the action
has finished, go to the Releases page of your repository and publish the new release.

By default, a GitHub Actions workflow is generated. Use `alpyki new ... --actions gitea` to generate a Gitea Actions
workflow, `--actions gitlab` for GitLab CI, or `--actions none` to skip CI files. The `--ci` flag is an alias for
`--actions`.
