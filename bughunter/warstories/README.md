# 🦞 War Stories — BugHunter Practical experience database

Stored here BugHunter Real penetration testing/CTF Problem-solving battle report.

Each battle report records a complete attack chain: from information gathering to the final. flagIncluding the detours taken、Where the key breakthrough point is.

## File naming rules

```
YYYY-MM-DD_Question type_Keywords.md
```

For example:`2026-04-19_php-deserialization_regex-bypass.md`

## Battle Report Template

Each battle report should include:

| Block | Content |
|------|------|
| **Metadata** | Date、Objective、Type、Keywords、Rounds、Toolchain |
| **Attack chain** | What was done at each step、Found something |
| **Key breakthrough** | Which step is decisive, and why |
| **The path taken is a detour** | Which attempts failed and why |
| **Payload** | Reproducible exploit code |
| **Experience summary** | Methodology transferable to similar topics |

## Battle Report Index

| Date | Title | Type | Rounds | Link |
|------|------|------|------|------|
| 2026-04-19 | NSSCTF PHP Regex bypass | Web / PHP / Regex bypass | 14 | [→](./2026-04-19_php-deserialization_regex-bypass.md) |
