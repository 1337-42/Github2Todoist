import json
import os
from pathlib import Path
import platform
from github import Github
from todoist_api_python.api import TodoistAPI


def get_config_dir():
    if platform.system() == "Windows":
        config_dir = Path(os.environ.get("APPDATA")) / "github_todoist_sync"
    else:
        config_dir = Path.home() / ".config" / "github_todoist_sync"
    return config_dir


def main():
    # Determine the configuration directory
    config_dir = get_config_dir()
    config_dir.mkdir(
        parents=True, exist_ok=True
    )  # Create the directory if it doesn't exist

    # Paths to the config and mapping files
    config_file = config_dir / "config.json"
    mappings_file = config_dir / "item_task_mapping.json"

    # Load configuration from config.json
    if config_file.exists():
        with open(config_file, "r") as f:
            config = json.load(f)
    else:
        # Create a default config file if it doesn't exist
        default_config = {
            "GITHUB_TOKEN": "your_github_token",
            "TODOIST_TOKEN": "your_todoist_token",
            "USERNAME": "your_github_username",
            "REPO_PROJECT_MAPPING": {"owner/repo": "Your Todoist Project Name"},
        }
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=4)
        print(
            f"Default configuration file created at '{config_file}'. Please update it with your credentials."
        )
        return  # Exit the script after creating the default config

    github_token = config.get("GITHUB_TOKEN")
    todoist_token = config.get("TODOIST_TOKEN")
    username = config.get("USERNAME")
    repo_project_mapping = config.get("REPO_PROJECT_MAPPING", {})

    if not all([github_token, todoist_token, username]):
        raise ValueError(
            "GITHUB_TOKEN, TODOIST_TOKEN, and USERNAME must be set in the config file."
        )

    # Initialize GitHub and Todoist clients
    g = Github(github_token)
    todoist = TodoistAPI(todoist_token)

    # Load existing mapping if it exists
    if mappings_file.exists():
        with open(mappings_file, "r") as f:
            item_task_mapping = json.load(f)
    else:
        item_task_mapping = {}

    # Fetch Todoist projects and create a mapping from name to ID
    projects = todoist.get_projects()
    project_name_to_id = {project.name: project.id for project in projects}

    # Map repository full names to project IDs
    repo_to_project_id = {}
    for repo_full_name, project_name in repo_project_mapping.items():
        project_id = project_name_to_id.get(project_name)
        if project_id:
            repo_to_project_id[repo_full_name] = project_id
        else:
            print(f"Warning: Todoist project '{project_name}' not found.")

    def save_mapping():
        with open(mappings_file, "w") as f:
            json.dump(item_task_mapping, f, indent=4)

    def get_issues():
        issues = []
        # Issues assigned to me
        assigned_issues = g.search_issues(
            f"assignee:{username} is:open is:issue", sort="updated", order="desc"
        )
        # Issues created by me
        created_issues = g.search_issues(
            f"author:{username} is:open is:issue", sort="updated", order="desc"
        )
        # Issues where I am mentioned
        mentioned_issues = g.search_issues(
            f"mentions:{username} is:open is:issue", sort="updated", order="desc"
        )

        # Combine all issues, avoiding duplicates
        issue_ids = set()
        for issue in assigned_issues:
            if issue.id not in issue_ids:
                issues.append(("assigned", issue))
                issue_ids.add(issue.id)
        for issue in created_issues:
            if issue.id not in issue_ids:
                issues.append(("created", issue))
                issue_ids.add(issue.id)
        for issue in mentioned_issues:
            if issue.id not in issue_ids:
                issues.append(("mentioned", issue))
                issue_ids.add(issue.id)
        return issues

    def get_pull_requests():
        prs = []
        # PRs assigned to me
        assigned_prs = g.search_issues(
            f"assignee:{username} is:open is:pr", sort="updated", order="desc"
        )
        # PRs created by me
        created_prs = g.search_issues(
            f"author:{username} is:open is:pr", sort="updated", order="desc"
        )
        # PRs where I am mentioned
        mentioned_prs = g.search_issues(
            f"mentions:{username} is:open is:pr", sort="updated", order="desc"
        )
        # PRs where I am requested reviewer
        review_requested_prs = g.search_issues(
            f"review-requested:{username} is:open is:pr", sort="updated", order="desc"
        )

        # Combine all PRs, avoiding duplicates
        pr_ids = set()
        for pr in assigned_prs:
            if pr.id not in pr_ids:
                prs.append(("assigned", pr))
                pr_ids.add(pr.id)
        for pr in created_prs:
            if pr.id not in pr_ids:
                prs.append(("created", pr))
                pr_ids.add(pr.id)
        for pr in mentioned_prs:
            if pr.id not in pr_ids:
                prs.append(("mentioned", pr))
                pr_ids.add(pr.id)
        for pr in review_requested_prs:
            if pr.id not in pr_ids:
                prs.append(("review", pr))
                pr_ids.add(pr.id)
        return prs

    def create_todoist_task(item_type, relation, item):
        task_content = f"{item.title}"
        task_description = f"url: {item.html_url} \nid: {item.id}"

        labels = []

        if item_type == "issue":
            label_name = f"issue:{relation}"
        elif item_type == "pr":
            label_name = f"pr:{relation}"
        else:
            label_name = None

        if label_name:
            labels.append(label_name)

        # Determine the project ID
        repo_full_name = item.repository.full_name  # e.g., 'owner/repo'
        project_id = repo_to_project_id.get(repo_full_name)

        try:
            task = todoist.add_task(
                content=task_content,
                project_id=project_id,
                labels=labels,
                description=task_description,
            )
            print(
                f"Created Todoist task for {item_type} #{item.number} -- {task_description}"
            )
            # Store the mapping
            item_task_mapping[str(item.id)] = task.id
            save_mapping()
        except Exception as e:
            print(f"Error creating task for {item_type} #{item.number}: {e}")

    def update_tasks():
        # Get current open issues and PRs
        issues = get_issues()
        prs = get_pull_requests()
        items = [("issue", relation, issue) for relation, issue in issues] + [
            ("pr", relation, pr) for relation, pr in prs
        ]
        open_item_ids = set(str(item.id) for _, _, item in items)

        # For each item, create a Todoist task if not already created
        for item_type, relation, item in items:
            if str(item.id) not in item_task_mapping:
                create_todoist_task(item_type, relation, item)
        # Update tasks for closed items
        tracked_item_ids = set(item_task_mapping.keys())
        closed_item_ids = tracked_item_ids - open_item_ids
        if closed_item_ids:
            closed_label_name = "Closed"
            for item_id in closed_item_ids:
                task_id = item_task_mapping[item_id]
                try:
                    # Fetch the task
                    task = todoist.get_task(task_id)
                    if not task.is_completed:
                        # Add 'Closed' label to the task
                        labels = task.labels or []
                        if closed_label_name not in labels:
                            labels.append(closed_label_name)
                            todoist.update_task(task_id=task_id, labels=labels)
                            print(f'Added "Closed" label to task {task_id}')
                    else:
                        print(
                            f"Task {task_id} is already completed, Removing from mapping"
                        )
                        del item_task_mapping[item_id]
                        save_mapping()
                except Exception as e:
                    print(f"Error updating task {task_id}: {e}")

    update_tasks()


def init_config():
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.json"
    if not config_file.exists():
        default_config = {
            "GITHUB_TOKEN": "your_github_token",
            "TODOIST_TOKEN": "your_todoist_token",
            "USERNAME": "your_github_username",
            "REPO_PROJECT_MAPPING": {"owner/repo": "Your Todoist Project Name"},
        }
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=4)
        print(
            f"Default configuration file created at '{config_file}'. Please update it with your credentials."
        )
    else:
        print(f"Configuration file already exists at '{config_file}'.")

    mappings_file = config_dir / "item_task_mapping.json"
    if not mappings_file.exists():
        with open(mappings_file, "w") as f:
            json.dump({}, f, indent=4)
        print(f"Mapping file created at '{mappings_file}'.")
    else:
        print(f"Mapping file already exists at '{mappings_file}'.")


if __name__ == "__main__":
    main()
