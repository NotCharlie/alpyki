import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from alpyki.cli import (
    _cli,
    _get_workflows_directory,
    link,
    new,
    package,
    show_link,
    vendor,
)
from alpyki.model import Data, Icon, Key, OutputItem, ScriptFilterOutput, Text, Type


def test_new(tmpdir):
    tmpdir = Path(tmpdir)
    sync_dir = tmpdir / "sync"
    workflows = sync_dir / "Alfred.alfredpreferences/workflows"
    workflows.mkdir(parents=True)

    args = MagicMock(
        sprc=argparse.Namespace,
        keyword="test",
        bundle_id="com.example.test",
        author=None,
        website=None,
        description=None,
        actions="github",
        git=True,
        link=True,
        vendor=True,
    )
    args.name = "test_wf"

    expected_git_call = call(["git", "init", "test_wf"])
    expected_vendor_call = call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            f"{tmpdir/'test_wf'/'requirements.txt'}",
            f"--target={tmpdir/'test_wf'/'Workflow'/'vendored'}",
        ]
    )

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._get_sync_directory", return_value=sync_dir):
            with patch("subprocess.call", return_value=0) as mock_sub:
                new(args)
                assert mock_sub.call_count == 2
                mock_sub.assert_has_calls([expected_git_call, expected_vendor_call])

    assert (tmpdir / "test_wf/Workflow/workflow.py").exists()
    installed_workflows = list(workflows.iterdir())
    assert len(installed_workflows) == 1
    assert installed_workflows[0].is_symlink()
    assert installed_workflows[0].readlink() == tmpdir / "test_wf" / "Workflow"


def test_get_workflows_directory():
    expected = Path.home() / "Library/Application Support/Alfred/Alfred.alfredpreferences/workflows"

    with patch("alpyki.cli._get_sync_directory", return_value=None):
        assert _get_workflows_directory() == expected


def test_full_model_serialises_to_json():
    output = ScriptFilterOutput(
        rerun=4.2,
        items=[
            OutputItem(
                title="Hello Alfred!",
                subtitle="a string",
                uid="fake_uid",
                icon=Icon.uti("public.jpeg"),
                valid=True,
                match="Hi",
                autocomplete="Hello Alfred!",
                mods={
                    Key.Cmd: Data(
                        subtitle="My new subtitle",
                        arg="An overridden argument",
                        icon=Icon.file_icon("/System/Applications/Calendar.app"),
                        valid=True,
                    )
                },
                text=Text(large_type="Large type this", copy="Copy that"),
                quicklookurl="https://example.com",
                type=Type.Default,
            ),
            OutputItem(title="A minimal item"),
        ],
        variables={"key": 42},
    )

    assert json.dumps(output, default=vars)


def test_show_link_with_link(tmpdir):
    tmpdir = Path(tmpdir)
    wf_dir = tmpdir / "Workflow"
    wf_dir.mkdir(parents=True)
    link_path = Path("/path/to/workflow/link")

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._info_plist_path") as mock_info_plist_path:
            mock_info_plist_path.return_value.exists.return_value = True
            with patch("alpyki.cli.find_workflow_link", return_value=link_path) as mock_find:
                with patch("builtins.print") as mock_print:
                    show_link(MagicMock(spec=argparse.Namespace))
                    mock_find.assert_called_once_with(wf_dir)
                    mock_print.assert_called_once_with(link_path)


def test_show_link_without_link(tmpdir):
    tmpdir = Path(tmpdir)
    wf_dir = tmpdir / "Workflow"
    wf_dir.mkdir(parents=True)

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._info_plist_path") as mock_info_plist_path:
            mock_info_plist_path.return_value.exists.return_value = True
            with patch("alpyki.cli.find_workflow_link", return_value=None) as mock_find:
                with patch("logging.error") as mock_error:
                    with pytest.raises(SystemExit) as excinfo:
                        show_link(MagicMock(spec=argparse.Namespace))
                    assert excinfo.value.code == 1
                    mock_find.assert_called_once_with(wf_dir)
                    mock_error.assert_called_once_with("No workflow link found. Use 'alpyki link' to create one.")


def test_exits_if_not_in_workflow_dir(tmpdir):
    with patch("pathlib.Path.cwd", return_value=tmpdir):
        for func in (link, package, vendor, show_link):
            with pytest.raises(SystemExit) as excinfo:
                func(MagicMock(spec=argparse.Namespace))
            assert excinfo.value.code == 1


def test_new_actions_github(tmpdir):
    """Default actions='github' creates .github workflow files."""
    tmpdir = Path(tmpdir)
    sync_dir = tmpdir / "sync"
    workflows = sync_dir / "Alfred.alfredpreferences/workflows"
    workflows.mkdir(parents=True)

    args = MagicMock(
        sprc=argparse.Namespace,
        keyword="test",
        bundle_id="com.example.test",
        author=None,
        website=None,
        description=None,
        actions="github",
        git=True,
        link=True,
        vendor=True,
    )
    args.name = "test_wf"

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._get_sync_directory", return_value=sync_dir):
            with patch("subprocess.call", return_value=0):
                new(args)

    assert (tmpdir / "test_wf/.github/workflows/build_and_release.yaml").exists()
    assert not (tmpdir / "test_wf/.gitea").exists()
    assert not (tmpdir / "test_wf/.gitlab-ci.yml").exists()


def test_new_actions_gitea(tmpdir):
    """With actions='gitea', .gitea workflow files are created."""
    tmpdir = Path(tmpdir)
    sync_dir = tmpdir / "sync"
    workflows = sync_dir / "Alfred.alfredpreferences/workflows"
    workflows.mkdir(parents=True)

    args = MagicMock(
        sprc=argparse.Namespace,
        keyword="test",
        bundle_id="com.example.test",
        author=None,
        website=None,
        description=None,
        actions="gitea",
        git=True,
        link=True,
        vendor=True,
    )
    args.name = "test_wf"

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._get_sync_directory", return_value=sync_dir):
            with patch("subprocess.call", return_value=0):
                new(args)

    assert (tmpdir / "test_wf/.gitea/workflows/build_and_release.yaml").exists()
    assert not (tmpdir / "test_wf/.github").exists()
    assert not (tmpdir / "test_wf/.gitlab-ci.yml").exists()


def test_new_actions_gitlab(tmpdir):
    """With actions='gitlab', .gitlab-ci.yml is created."""
    tmpdir = Path(tmpdir)
    sync_dir = tmpdir / "sync"
    workflows = sync_dir / "Alfred.alfredpreferences/workflows"
    workflows.mkdir(parents=True)

    args = MagicMock(
        sprc=argparse.Namespace,
        keyword="test",
        bundle_id="com.example.test",
        author=None,
        website=None,
        description=None,
        actions="gitlab",
        git=True,
        link=True,
        vendor=True,
    )
    args.name = "test_wf"

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._get_sync_directory", return_value=sync_dir):
            with patch("subprocess.call", return_value=0):
                new(args)

    assert (tmpdir / "test_wf/.gitlab-ci.yml").exists()
    assert not (tmpdir / "test_wf/.github").exists()
    assert not (tmpdir / "test_wf/.gitea").exists()


def test_new_actions_none(tmpdir):
    """With actions='none', no CI workflow files are created."""
    tmpdir = Path(tmpdir)
    sync_dir = tmpdir / "sync"
    workflows = sync_dir / "Alfred.alfredpreferences/workflows"
    workflows.mkdir(parents=True)

    args = MagicMock(
        sprc=argparse.Namespace,
        keyword="test",
        bundle_id="com.example.test",
        author=None,
        website=None,
        description=None,
        actions="none",
        git=True,
        link=True,
        vendor=True,
    )
    args.name = "test_wf"

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._get_sync_directory", return_value=sync_dir):
            with patch("subprocess.call", return_value=0):
                new(args)

    assert not (tmpdir / "test_wf/.github").exists()
    assert not (tmpdir / "test_wf/.gitea").exists()
    assert not (tmpdir / "test_wf/.gitlab-ci.yml").exists()


def test_new_requirements_txt_has_version(tmpdir):
    """Generated requirements.txt pins the installed alpyki version."""
    tmpdir = Path(tmpdir)
    sync_dir = tmpdir / "sync"
    workflows = sync_dir / "Alfred.alfredpreferences/workflows"
    workflows.mkdir(parents=True)

    args = MagicMock(
        sprc=argparse.Namespace,
        keyword="test",
        bundle_id="com.example.test",
        author=None,
        website=None,
        description=None,
        actions="none",
        git=False,
        link=False,
        vendor=False,
    )
    args.name = "test_wf"

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._get_sync_directory", return_value=sync_dir):
            with patch("subprocess.call", return_value=0):
                with patch("alpyki.cli.get_version", return_value="1.2.3"):
                    new(args)

    requirements = (tmpdir / "test_wf/requirements.txt").read_text()
    assert "alpyki==1.2.3" in requirements


def test_new_fails_when_not_installed(tmpdir):
    """new() raises PackageNotFoundError when alpyki is not installed."""
    tmpdir = Path(tmpdir)
    sync_dir = tmpdir / "sync"
    workflows = sync_dir / "Alfred.alfredpreferences/workflows"
    workflows.mkdir(parents=True)

    args = MagicMock(
        sprc=argparse.Namespace,
        keyword="test",
        bundle_id="com.example.test",
        author=None,
        website=None,
        description=None,
        actions="none",
        git=False,
        link=False,
        vendor=False,
    )
    args.name = "test_wf"

    with patch("pathlib.Path.cwd", return_value=tmpdir):
        with patch("alpyki.cli._get_sync_directory", return_value=sync_dir):
            with patch("alpyki.cli.get_version", side_effect=PackageNotFoundError("alpyki")):
                with pytest.raises(PackageNotFoundError):
                    new(args)


def test_cli_version(capsys):
    """--version prints the installed alpyki version and exits."""
    with patch("alpyki.cli.get_version", return_value="1.2.3"):
        with patch("sys.argv", ["alpyki", "--version"]):
            with pytest.raises(SystemExit) as excinfo:
                _cli()
            assert excinfo.value.code == 0

    out = capsys.readouterr()
    assert "1.2.3" in out.out


def test_completion_zsh(capsys):
    """completion with --shell zsh generates a zsh completion script."""
    with patch("sys.argv", ["alpyki", "completion", "--shell", "zsh"]):
        _cli()

    out = capsys.readouterr()
    assert "alpyki" in out.out
    assert "zsh" in out.out


def test_completion_bash(capsys):
    """completion with --shell bash generates a bash completion script."""
    with patch("sys.argv", ["alpyki", "completion", "--shell", "bash"]):
        _cli()

    out = capsys.readouterr()
    assert "alpyki" in out.out


def test_completion_fish(capsys):
    """completion with --shell fish generates a fish completion script."""
    with patch("sys.argv", ["alpyki", "completion", "--shell", "fish"]):
        _cli()

    out = capsys.readouterr()
    assert "alpyki" in out.out


def test_completion_invalid_shell(capsys):
    """completion with unsupported shell exits with error."""
    with patch("sys.argv", ["alpyki", "completion", "--shell", "powershell"]):
        with pytest.raises(SystemExit) as excinfo:
            _cli()
        assert excinfo.value.code != 0
