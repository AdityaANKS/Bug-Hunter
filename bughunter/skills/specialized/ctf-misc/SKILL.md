---
name: ctf-misc
description: CTFMiscellaneous Knowledge Base — Python Jailescape、Bash Jailescape、Coding chain identification and decoding、QR/Audio/image steganography、gameVMReverse、CTFd APInavigation、LinuxElevate privileges
---

# CTF Miscellaneous Knowledge Base

against CTF Misc Practical knowledge base of the topic, covering**sandbox escape、Coding chain identification、Steganography、Game reverse**Other miscellaneous questions.

## scene routing

| scene | Reference documentation | core content |
|------|---------|---------|
| Python sandbox escape | `python-jail-escape.md` | `__import__`/func\_globals/evalchain |
| Bash sandbox escape | `bash-jail-escape.md` | HISTFILE/ctypes.sh/viEditor escape |
| Coding chain identification and decoding | `encoding-chain-reference.md` | Base64→Hex→ROT13 Multiple levels of nesting |
| game/Customize VM Reverse | `game-and-vm-reverse.md` | WASM/Brainfuck/Z3 Constraint solving |
| CTFd Platform operation | `ctfd-platform-guide.md` | API Download attachment/submit flag |
| Linux Elevate privileges | `linux-privesc-quick.md` | SUID/sudo/cron/kernel vulnerability |

## Quick question judgment

| Question characteristics | Possible test points | Recommended reference |
|---------|---------|---------|
| Python exec/eval Input box | PyJail escape | python-jail-escape.md |
| command line restricted bash | BashJail escape | bash-jail-escape.md |
| Weirdly encoded string | Coding chain decoding | encoding-chain-reference.md |
| QR code/audio file | Steganography | encoding-chain-reference.md |
| game binary/WASM | Customize VM Reverse | game-and-vm-reverse.md |
| CTFtime / CTFd platform | platform API | ctfd-platform-guide.md |
| gave one shell | Linux Elevate privileges | linux-privesc-quick.md |
