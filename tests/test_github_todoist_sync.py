# test_tool.py
import pytest
import json
import os
from pathlib import Path
from unittest import mock

# test_tool.py
from github_todoist_sync.sync import (
    get_config_dir,
    init_config,
    get_issues,
    get_pull_requests,
    create_todoist_task,
)


# Test get_config_dir function
def test_get_config_dir():
    config_dir = get_config_dir()
    assert config_dir.exists(), "Config directory should exist"
    assert config_dir.name == "github_todoist_sync", "Directory name mismatch"


# Test init_config function
def test_init_config(tmp_path):
    with mock.patch("github_todoist_sync.sync.get_config_dir", return_value=tmp_path):
        init_config()
        config_file = tmp_path / "config.json"
        mappings_file = tmp_path / "item_task_mapping.json"
        assert config_file.exists(), "Config file was not created"
        assert mappings_file.exists(), "Mappings file was not created"


# Mock GitHub and Todoist API initialization
@pytest.fixture
def mock_github():
    with mock.patch("github_todoist_sync.sync.Github") as MockGithub:
        yield MockGithub


@pytest.fixture
def mock_todoist():
    with mock.patch("github_todoist_sync.sync.TodoistAPI") as MockTodoist:
        yield MockTodoist


# Test for fetching issues and PRs
def test_get_issues(mock_github):
    mock_issue_1 = mock.Mock()
    mock_issue_1.id = 1
    mock_issue_1.title = "Assigned issue"

    mock_issue_2 = mock.Mock()
    mock_issue_2.id = 2
    mock_issue_2.title = "Created issue"

    mock_issue_3 = mock.Mock()
    mock_issue_3.id = 3
    mock_issue_3.title = "Mentioned issue"

    mock_github.return_value.search_issues.side_effect = [
        [mock_issue_1],
        [mock_issue_2],
        [mock_issue_3],
    ]

    issues = get_issues(github=mock_github.return_value, username="testuser")
    assert len(issues) == 3, "Should fetch three types of issues"
    assert issues[0][1].title == "Assigned issue"
    assert issues[1][1].title == "Created issue"
    assert issues[2][1].title == "Mentioned issue"


def test_get_pull_requests(mock_github):
    mock_pr_1 = mock.Mock()
    mock_pr_1.id = 1
    mock_pr_1.title = "Assigned PR"

    mock_pr_2 = mock.Mock()
    mock_pr_2.id = 2
    mock_pr_2.title = "Created PR"

    mock_pr_3 = mock.Mock()
    mock_pr_3.id = 3
    mock_pr_3.title = "Mentioned PR"

    mock_pr_4 = mock.Mock()
    mock_pr_4.id = 4
    mock_pr_4.title = "Review requested PR"

    mock_github.return_value.search_issues.side_effect = [
        [mock_pr_1],
        [mock_pr_2],
        [mock_pr_3],
        [mock_pr_4],
    ]

    prs = get_pull_requests(github=mock_github.return_value, username="testuser")
    assert len(prs) == 4, "Should fetch four types of PRs"
    assert prs[0][1].title == "Assigned PR"
    assert prs[1][1].title == "Created PR"
    assert prs[2][1].title == "Mentioned PR"
    assert prs[3][1].title == "Review requested PR"


# Mock Todoist task creation
def test_create_todoist_task(mock_todoist):
    mock_todoist.return_value.add_task.return_value = {"id": 123}
    item = mock.Mock()
    item.title = "Sample Issue"
    item.html_url = "http://example.com"
    item.id = 1
    item.repository.full_name = "owner/repo"
    create_todoist_task(
        "issue",
        "created",
        item,
        {2: 2},
        "mappings_file",
        {},
        mock_todoist.return_value,
    )
    mock_todoist.return_value.add_task.assert_called_once()


# Additional tests
def test_create_todoist_task_with_different_item(mock_todoist):
    item_a = mock.Mock()
    item_a.title = "Another Issue"
    item_a.html_url = "http://example.com/another"
    item_a.id = 2
    item_a.repository.full_name = "owner/another_repo"
    mock_todoist.return_value.add_task.return_value = item_a
    item_b = mock.Mock()
    item_b.title = "Another Issue"
    item_b.html_url = "http://example.com/another"
    item_b.id = 2
    item_b.repository.full_name = "owner/another_repo"
    with mock.patch("github_todoist_sync.sync.save_mapping"):
        create_todoist_task(
            "issue",
            "created",
            item_b,
            {"owner/another_repo": 2},
            "mappings_file",
            {2: 2},
            mock_todoist.return_value,
        )
        mock_todoist.return_value.add_task.assert_called_once_with(
            content="Another Issue",
            project_id=2,
            labels=["issue:created"],
            description="url: http://example.com/another \nid: 2",
        )


def test_get_issues_no_issues(mock_github):
    mock_github.return_value.search_issues.return_value = []
    issues = get_issues(github=mock_github.return_value, username="testuser")
    assert len(issues) == 0, "Should fetch no issues when none are returned"


def test_get_pull_requests_no_prs(mock_github):
    mock_github.return_value.search_issues.return_value = []
    prs = get_pull_requests(github=mock_github.return_value, username="testuser")
    assert len(prs) == 0, "Should fetch no PRs when none are returned"
