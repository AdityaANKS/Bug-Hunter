# Android Signature Reverse Template

Use this template for Android sign, token, encrypt, decrypt, JNI, interceptor, and replay tasks.

## Template

```markdown
# Android Signature reverse record

## Basic information

- APK / Package name:
- Target function:
- Target request:
- Target field:
- Current stage:static / dynamic / native / replay
- Current status:🟡 in progress / ✅ Closed loop / ⛔ block
- Target:
- constraint:

## static overview

| project | content |
| --- | --- |
| Manifest Entrance |  |
| Application |  |
| host Activity / target component |  |
| Main package structure |  |
| web framework |  |
| DI frame |  |
| current conclusion |  |

## Request call chain

```text
Activity / Fragment / Service
-> ViewModel / Presenter / UseCase
-> Repository / DataSource
-> ApiService / RequestBuilder / Interceptor
-> Signer / Encryptor / Serializer
```

- Real call chain:
- ask Method / Path:
- Header Writing point:
- Body Writing point:
- Sign Enter the meeting point:
- sequence / Prerequisites:

## Sign / Crypto position

| project | content |
| --- | --- |
| Sign kind / method |  |
| Encrypt kind / method |  |
| Key constants |  |
| key Header |  |
| key Token / Device value |  |
| Java-only / Java+JNI / Native-first |  |

## Dynamic verification

| Hook point | reason | capture content | result |
| --- | --- | --- | --- |
| Hook1 |  |  |  |

- URL:
- Headers:
- Body:
- Sign enter:
- Sign Output:
- Proxy verification:

## JNI / SO analyze

| project | content |
| --- | --- |
| Java native Entrance |  |
| SO name |  |
| JNI type | static / dynamic |
| input parameters |  |
| Output role | final sign / middle token / other |
| Is it necessary deeper RE |  |

## Burp replay baseline

- Method:
- Path:
- Query:
- Headers:
- Body:
- Required fields:
- Mutable fields:
- Prerequisite status:
- Do you need equipment? / Hook / App assist:

## in conclusion

- Current degree of closed loop:
- Residual blocking:
- Suggestions for next steps:
```

## Minimum Required Fields

Even in a compact record, keep:

- APK or package
- target request
- real call-flow summary
- network stack
- sign or crypto location
- Java versus JNI conclusion
- one runtime hook or explicit reason why runtime is not needed
- Burp replay baseline or explicit blocker
