# GitHub Todoist Sync

A Python tool that synchronizes your GitHub issues and pull requests (PRs) with Todoist tasks. It creates Todoist tasks for issues and PRs assigned to you, created by you, or where you're mentioned, and updates tasks when items are closed on GitHub.

## Features

- **Sync GitHub Issues and PRs:** Automatically create Todoist tasks for GitHub issues and PRs that are relevant to you.
- **Repository to Project Mapping:** Map specific GitHub repositories to Todoist projects for organized task management.
- **Automatic Labeling:** Add labels to tasks based on item type (`issue` or `pr`) and your relation (`assigned`, `mentioned`, `created`, `review`).
- **Closed Item Tracking:** When an issue or PR is closed on GitHub, the corresponding Todoist task is updated with a `"Closed"` label.
- **Cross-Platform Configuration:** Uses a configuration directory in the user's home folder, compatible with Windows, Linux, and macOS.

## Installation

### Prerequisites

- **Python 3.6 or higher** installed on your system.
- **GitHub Personal Access Token:**
  - Go to your GitHub account settings.
  - Navigate to **Developer settings** > **Personal access tokens**.
  - Generate a new token with the **`repo`** scope to access repository issues and PRs.
- **Todoist API Token:**
  - Log in to your Todoist account.
  - Go to **Settings** > **Integrations**.
  - Copy your API token.

### Install via pip

```bash
pip install github-todoist-sync
```

## Configuration

### Initialize Configuration

After installation, run the following command to create the default configuration files:

```bash
github-todoist-sync-init
```

This command creates the configuration directory and default config files in your home directory:

- **Windows:** `C:\Users\YourUsername\AppData\Roaming\github_todoist_sync\`
- **Linux/macOS:** `/home/yourusername/.config/github_todoist_sync/`

### Update `config.json`

Navigate to the configuration directory and open `config.json`. Update it with your actual GitHub and Todoist API tokens, GitHub username, and repository-to-project mappings.

**Example `config.json`:**

```json
{
    "GITHUB_TOKEN": "your_actual_github_token",
    "TODOIST_TOKEN": "your_actual_todoist_token",
    "USERNAME": "your_github_username",
    "REPO_PROJECT_MAPPING": {
        "owner1/repo1": "Todoist Project 1",
        "owner2/repo2": "Todoist Project 2"
    }
}
```

- **`GITHUB_TOKEN`**: Your GitHub personal access token.
- **`TODOIST_TOKEN`**: Your Todoist API token.
- **`USERNAME`**: Your GitHub username.
- **`REPO_PROJECT_MAPPING`**: A mapping of GitHub repositories to Todoist project names.

### Permissions

Ensure that the configuration files are secure:

- On Unix systems, you can set the config file permissions to be readable and writable only by you:

  ```bash
  chmod 600 config.json
  ```

## Usage

After configuring the tool, you can run the synchronization script:

```bash
github-todoist-sync
```

- The script fetches your GitHub issues and PRs.
- Creates Todoist tasks for new items.
- Updates tasks for closed items by adding a `"Closed"` label.
- Tasks are added to the specified Todoist projects and labeled accordingly.

## Labels Added to Tasks

- **For Issues:**
  - `issue:assigned`
  - `issue:mentioned`
  - `issue:created`
- **For Pull Requests:**
  - `pr:assigned`
  - `pr:mentioned`
  - `pr:created`
  - `pr:review`
- **When Closed:**
  - `Closed`

## Project Structure

```
github_todoist_sync/
├── github_todoist_sync/
│   ├── __init__.py
│   └── sync.py
├── pyproject.toml
└── README.md
```

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository** on GitHub.
2. **Clone your fork**:

   ```bash
   git clone https://github.com/yourusername/github-todoist-sync.git
   ```

3. **Create a new branch** for your feature or bugfix:

   ```bash
   git checkout -b feature-or-bugfix-name
   ```

4. **Make your changes** and commit them:

   ```bash
   git commit -am "Description of changes"
   ```

5. **Push to your fork**:

   ```bash
   git push origin feature-or-bugfix-name
   ```

6. **Submit a pull request** to the main repository.

## Troubleshooting

- **Authentication Errors:**
  - Ensure your API tokens are correct and have the necessary permissions.
  - Double-check that you copied the entire token without extra spaces.

- **Permission Issues:**
  - If the script can't read or write configuration files, check the file permissions.
  - Ensure the config directory is writable by your user account.

- **Label or Project Not Found:**
  - Verify that the Todoist project names in `REPO_PROJECT_MAPPING` match exactly with those in your Todoist account.
  - Labels are created automatically; ensure your Todoist account allows label creation.

- **API Rate Limits:**
  - Be aware of GitHub and Todoist API rate limits.
  - If you encounter rate limit issues, consider running the script less frequently.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or support, please open an issue on the [GitHub repository](https://github.com/yourusername/github-todoist-sync/issues).

## Acknowledgements

- [PyGithub](https://github.com/PyGithub/PyGithub) - A Python library to access the GitHub API.
- [Todoist API Python](https://github.com/Doist/todoist-api-python) - Official Todoist Python SDK.

---

*Happy task management!*