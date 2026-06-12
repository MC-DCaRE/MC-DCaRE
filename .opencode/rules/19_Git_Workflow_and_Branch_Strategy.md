# Git Workflow & Branch Strategy

## Branch Naming
- Feature: `develop-{bounded-context}-{feature-name}`
- Sub-task: `develop-{context}-{feature}-{sub-task}`
- Hotfix: `main-hotfix-{issue-description}`

## Workflow
```
main (stable releases)
└── develop (integration branch)
    ├── develop-{context}-{feature}
    │   └── develop-{context}-{feature}-{sub-task}
    └── develop-{context}-{feature2}
```

## Commit Format
```
type(scope): description

[Optional body]
[Optional footer: Closes #123]
```
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Rules
- Base branch is `develop`; `main` is for stable releases only
- Keep branches short-lived (1-3 days)
- Run full tests before any merge
- Hotfixes merge to both `main` and `develop`
- Always reference the active plan in `.opencode/plans/`
