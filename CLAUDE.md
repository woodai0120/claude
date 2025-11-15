# CLAUDE.md

**AI Assistant Guide for the Claude Repository**

Last Updated: 2025-11-15

---

## Table of Contents

1. [Overview](#overview)
2. [Repository Status](#repository-status)
3. [Codebase Analysis Guidelines](#codebase-analysis-guidelines)
4. [Development Workflow](#development-workflow)
5. [Git Conventions](#git-conventions)
6. [Code Quality Standards](#code-quality-standards)
7. [Documentation Standards](#documentation-standards)
8. [Testing Guidelines](#testing-guidelines)
9. [AI Assistant Best Practices](#ai-assistant-best-practices)
10. [Common Patterns](#common-patterns)

---

## Overview

This document serves as a comprehensive guide for AI assistants (like Claude) working in this repository. It outlines the codebase structure, development workflows, conventions, and best practices to ensure consistent, high-quality contributions.

---

## Repository Status

**Current State:** This repository is in its initial state with no existing codebase.

**Repository Details:**
- **Owner:** woodai0120
- **Repository:** claude
- **Main Branch:** TBD (to be determined on first commit)
- **Current Branch:** claude/claude-md-mhzxihpr5l68m6fj-01XpsHzkBGbmX5frTjbcKSc9

---

## Codebase Analysis Guidelines

### Initial Repository Exploration

When first encountering this or any repository, follow these steps:

1. **Check for Configuration Files**
   ```bash
   # Look for package managers
   ls -la package.json  # Node.js
   ls -la requirements.txt  # Python
   ls -la Cargo.toml  # Rust
   ls -la go.mod  # Go
   ls -la pom.xml  # Java/Maven
   ls -la build.gradle  # Java/Gradle
   ```

2. **Identify Project Type**
   - Check README.md for project description
   - Examine configuration files for framework/language
   - Look for docker-compose.yml or Dockerfile
   - Check for CI/CD configurations (.github/workflows, .gitlab-ci.yml)

3. **Understand Directory Structure**
   - Locate source code directories (src/, lib/, app/, etc.)
   - Find test directories (test/, tests/, __tests__/, spec/)
   - Identify configuration directories (config/, .config/)
   - Check for documentation (docs/, wiki/)

4. **Review Dependencies**
   - Examine dependency files for project stack
   - Check for monorepo structures (lerna.json, nx.json, workspace)
   - Identify build tools and task runners

### Code Exploration Strategy

Use the **Task tool with Explore agent** for:
- Understanding overall architecture
- Finding where specific functionality is implemented
- Identifying patterns and conventions
- Mapping out module relationships

Use **direct Grep/Glob** only for:
- Specific file or class lookups
- Known patterns or keywords
- Quick verification of small details

---

## Development Workflow

### Branch Strategy

**Feature Branches:**
- All development happens on feature branches
- Branch naming: `claude/<description>-<session-id>`
- Example: `claude/claude-md-mhzxihpr5l68m6fj-01XpsHzkBGbmX5frTjbcKSc9`

**Important Rules:**
- ✅ ALWAYS develop on the designated feature branch
- ✅ NEVER push to main/master without explicit permission
- ✅ CREATE feature branch locally if it doesn't exist
- ✅ PUSH changes with `git push -u origin <branch-name>`

### Task Planning

**Use TodoWrite tool for:**
- Multi-step tasks (3+ steps)
- Complex implementations
- Bug fixes requiring investigation
- Feature development

**Todo Management:**
- Mark tasks as `in_progress` before starting
- Mark tasks as `completed` immediately after finishing
- Keep only ONE task in_progress at a time
- Remove irrelevant tasks from the list

### Code Changes

**Before Making Changes:**
1. Read existing files to understand current implementation
2. Plan changes using TodoWrite for complex tasks
3. Consider impact on tests and documentation

**When Implementing:**
1. Use Edit tool for modifying existing files
2. Use Write tool only for new files when absolutely necessary
3. Prefer editing over creating new files
4. Follow existing code style and patterns

**After Making Changes:**
1. Verify changes work as expected
2. Run tests if available
3. Update documentation if needed
4. Prepare clear commit messages

---

## Git Conventions

### Commit Messages

**Format:**
```
<type>: <short description>

<optional longer description>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `chore`: Maintenance tasks
- `style`: Code style/formatting changes

**Best Practices:**
- Use imperative mood ("add" not "added")
- Keep first line under 72 characters
- Focus on WHY, not just WHAT
- Reference issues/PRs when relevant

### Git Safety

**NEVER:**
- Run git commands with `--force` unless explicitly requested
- Skip hooks with `--no-verify` without permission
- Modify git config
- Amend commits by other developers
- Force push to main/master branches

**ALWAYS:**
- Check git status before committing
- Review git diff before committing
- Use heredoc format for commit messages
- Verify authorship before amending commits

### Push/Pull Retry Logic

**Network failures:**
- Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)
- Use `git push -u origin <branch-name>`
- Fetch specific branches: `git fetch origin <branch-name>`

---

## Code Quality Standards

### Security Best Practices

**Prevent Common Vulnerabilities:**
- ❌ SQL Injection
- ❌ Cross-Site Scripting (XSS)
- ❌ Command Injection
- ❌ Path Traversal
- ❌ Insecure Deserialization
- ❌ Authentication/Authorization flaws

**Input Validation:**
- Always validate and sanitize user input
- Use parameterized queries for database operations
- Escape output appropriately for context
- Implement proper authentication and authorization

**Secrets Management:**
- NEVER commit secrets, API keys, or credentials
- Use environment variables for sensitive data
- Keep .env files in .gitignore
- Warn users before committing sensitive files

### Code Style

**General Principles:**
- Follow existing patterns in the codebase
- Maintain consistency with surrounding code
- Use meaningful variable and function names
- Keep functions small and focused
- Add comments for complex logic, not obvious code

**Language-Specific:**
- Respect language idioms and conventions
- Follow community standards (PEP 8, ESLint rules, etc.)
- Use linters and formatters when available

---

## Documentation Standards

### Code Documentation

**Functions/Methods:**
- Document purpose, parameters, return values
- Include examples for complex functionality
- Note side effects and exceptions

**Classes/Modules:**
- Explain responsibility and relationships
- Document public APIs
- Include usage examples

### File References

When referencing code locations, use the pattern:
```
file_path:line_number
```

Example: "The error handling is in src/utils/errors.ts:142"

### Documentation Files

**Only create documentation when:**
- Explicitly requested by the user
- Essential for understanding complex features
- Required by project standards

**NEVER:**
- Proactively create README or markdown files
- Add unnecessary documentation
- Use emojis unless explicitly requested

---

## Testing Guidelines

### Test Strategy

**When Tests Exist:**
1. Run tests before making changes (baseline)
2. Make code changes
3. Run tests again to verify
4. Fix any broken tests
5. Add new tests for new functionality

**Running Tests:**
- Follow project's test commands (in package.json, Makefile, etc.)
- Run relevant test suites, not always full suite
- Check for test configuration files

### Test Quality

**Good Tests:**
- Test behavior, not implementation
- Are independent and isolated
- Have clear, descriptive names
- Cover edge cases and error conditions
- Are maintainable and readable

---

## AI Assistant Best Practices

### Communication

**Tone and Style:**
- Be concise and direct
- Focus on facts and technical accuracy
- Avoid unnecessary emojis (unless requested)
- Provide objective guidance over validation
- Disagree when necessary with respectful correction

**Output Format:**
- Use GitHub-flavored markdown
- Format for command line display
- Keep responses short and actionable
- Use code blocks appropriately

### Tool Usage

**Efficiency:**
- Use parallel tool calls when possible
- Avoid sequential calls for independent operations
- Don't use placeholders in tool parameters
- Use specialized tools over bash commands

**File Operations:**
- Read: Use Read tool (not cat/head/tail)
- Edit: Use Edit tool (not sed/awk)
- Write: Use Write tool (not echo/redirection)
- Search: Use Grep tool (not grep command)
- Find: Use Glob tool (not find command)

### Problem Solving

**Approach:**
1. Understand the problem fully
2. Research existing code and patterns
3. Plan the solution (use TodoWrite for complex tasks)
4. Implement incrementally
5. Test and verify
6. Document if necessary

**When Blocked:**
- Investigate root cause
- Search for similar patterns in codebase
- Ask clarifying questions
- Propose alternative approaches

---

## Common Patterns

### Feature Development

```
1. Create/switch to feature branch
2. Plan implementation with TodoWrite
3. Research existing code
4. Implement incrementally
5. Test each component
6. Update documentation
7. Commit with clear message
8. Push to feature branch
```

### Bug Fixing

```
1. Reproduce the bug
2. Locate the problematic code
3. Understand root cause
4. Plan the fix
5. Implement fix
6. Verify bug is resolved
7. Check for regression
8. Commit and push
```

### Code Refactoring

```
1. Understand current implementation
2. Identify improvement opportunities
3. Plan refactoring steps
4. Make small, incremental changes
5. Run tests after each change
6. Ensure no behavior changes
7. Commit logical chunks
```

---

## Project-Specific Notes

*This section will be updated as the project evolves with:*
- Specific architectural patterns used
- Custom conventions and standards
- Important gotchas or quirks
- Team preferences and style guides
- Build and deployment processes

---

## Updating This Document

This CLAUDE.md file should be updated when:
- Major architectural changes occur
- New conventions are established
- Significant dependencies are added
- Development workflows change
- Important patterns emerge

**Update Process:**
1. Make changes to this document
2. Review with team (if applicable)
3. Commit with message: `docs: update CLAUDE.md`
4. Keep "Last Updated" date current

---

## Quick Reference

### Essential Commands

```bash
# Check repository status
git status
git branch
git log --oneline -10

# Create and switch to feature branch
git checkout -b claude/feature-name-session-id

# Stage and commit changes
git add <files>
git commit -m "$(cat <<'EOF'
type: description

Details here
EOF
)"

# Push to remote
git push -u origin <branch-name>

# Run tests (project-specific - update when known)
npm test       # Node.js
pytest         # Python
cargo test     # Rust
go test        # Go
```

### Key Principles

1. **Read before Write**: Always read files before editing
2. **Plan Complex Tasks**: Use TodoWrite for multi-step work
3. **Commit Incrementally**: Small, logical commits
4. **Test Thoroughly**: Verify changes work
5. **Stay Consistent**: Follow existing patterns
6. **Communicate Clearly**: Concise, technical, accurate
7. **Security First**: Never commit secrets, prevent vulnerabilities
8. **Use Right Tools**: Specialized tools over bash commands

---

**End of CLAUDE.md**

*For questions or updates, modify this document as the project evolves.*
