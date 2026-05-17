# Git & PR Guidelines

## 1. Branching & Commits

Follow the format: `type/description` for branches and `type: description` for commits.

| Type         | Description         | Example                         |
| :----------- | :------------------ | :------------------------------ |
| **feat**     | New features        | `feat: add biometric login`     |
| **fix**      | Bug fixes           | `fix: resolve crash on startup` |
| **ui**       | UI/UX & styling     | `ui: update hero section`       |
| **docs**     | Documentation       | `docs: update setup guide`      |
| **refactor** | Code improvements   | `refactor: rename fetchUser`    |
| **style**    | Formatting/Linting  | `style: fix indentation`        |
| **test**     | Adding/fixing tests | `test: add login unit tests`    |
| **chore**    | Config/Variables    | `chore: update API_URL`         |

---

## 3. Pull Request (PR) Template

When opening a PR, please use the following structure to help reviewers understand your changes.

### Description

Provide a brief summary of the changes and the motivation behind them.
**Fixes:** # (link the issue number if applicable)

### Type of Change

- [ ] New feature (feat)
- [ ] Bug fix (fix)
- [ ] UI/UX update (ui)
- [ ] Refactor (refactor)
- [ ] Documentation (docs)
- [ ] Formatting/Linting (style)
- [ ] Adding/fixing tests (test)
- [ ] Config/Variables (chore)

### Screenshots / Recordings

_If this change affects the UI, please include screenshots or a short screen recording._

### Testing Done

Describe the tests you ran to verify your changes (e.g., manual UI testing, unit tests).

---

## 4. The Standard Workflow

1. **Sync:** `git pull origin main`
2. **Branch:** `git checkout -b type/your-task-name`
3. **Work:** Make your changes and test them.
4. **Stage:** `git add .`
5. **Commit:** `git commit -m "prefix: description of work"`
6. **Push:** `git push origin type/your-task-name`
7. **PR:** Open a Pull Request on GitHub using the template above.
