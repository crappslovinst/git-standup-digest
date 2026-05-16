# git-standup-digest

> Generates a readable daily standup summary from your git commit history across multiple local repositories.

---

## Installation

```bash
pip install git-standup-digest
```

Or install from source:

```bash
git clone https://github.com/yourname/git-standup-digest.git
cd git-standup-digest
pip install .
```

---

## Usage

Run from any directory, pointing to one or more local repo paths:

```bash
git-standup-digest --repos ~/projects/api ~/projects/frontend
```

**Example output:**

```
📋 Standup Digest — 2024-01-15

[api]
  • fix: resolve null pointer in auth middleware
  • refactor: extract token validation logic

[frontend]
  • feat: add dark mode toggle to settings page
  • chore: update dependencies
```

### Options

| Flag | Description |
|------|-------------|
| `--repos` | Space-separated list of local repo paths |
| `--author` | Filter commits by author name (default: current git user) |
| `--since` | Date range, e.g. `yesterday`, `2024-01-14` (default: today) |
| `--format` | Output format: `text`, `markdown`, `slack` |

```bash
# Summarize the last 2 days, formatted for Slack
git-standup-digest --repos ~/projects/* --since "2 days ago" --format slack
```

---

## Requirements

- Python 3.8+
- Git installed and available in `PATH`

---

## License

MIT © [yourname](https://github.com/yourname)