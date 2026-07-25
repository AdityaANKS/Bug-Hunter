# MCP Capability master document

## 1. Documentation Purpose

This document organizes what I can call directly in the current session MCP Capability; the goal is not just to create a "tool list," but to provide a suitable document for subsequent writing `skills` Reference Draft.  
Key coverage of the following contents:

- Each MCP Server/Namespace localization
- Calling methods for each method
- The meaning of major parameters
- What the returned results will roughly include
- Typical use cases
- and others MCP Common workflows during combination

This article is primarily aimed at Codex / Agent Class tool orchestration, not generic SDK Documentation. Hence, it will emphasize "when to use it" "write skill How to describe the call strategy at the time".

---

## 2. Generic calling conventions

### 2.1 Tool naming format

Current environment's MCP Tool names mostly follow the format below:

```text
mcp__<server_name>__<tool_name>
```

For example:

- `mcp__adb_mcp__list_devices`
- `mcp__chrome_devtools__navigate_page`
- `mcp__ida_pro_mcp__decompile`

Few and MCP Functions related to resource access without `mcp__` Prefix, but essentially also MCP Ecosystem capability:

- `list_mcp_resources`
- `list_mcp_resource_templates`
- `read_mcp_resource`

### 2.2 Call parameter format

All MCP Tools are all used JSON Style parameter object. Typical format:

```json
{
  "device_id": "emulator-5554",
  "lines": 200
}
```

Points to note:

- Only transmit necessary fields, do not meaninglessly fill empty arrays or `null`
- `optional` Parameters can generally be omitted
- Some tools require absolute paths, especially for screenshots、Save source code、Pull files、Screen recording output path, etc.
- Some tools use pagination parameters, such as `offset`、`count`、`pageIdx`、`pageSize`

### 2.3 Write skill Key points suggested in the description

If you want to write these capabilities as skill, suggesting that each skill Clearly state:

1. Trigger conditions  
2. Preferred usage MCP  
3. The order of tools  
4. Which parameters must be completed.  
5. Under what circumstances to switch to another MCP  
6. If output is empty/Failure, what should be done next to remedy

### 2.4 MCP Quick reference for selection

| Task Type | Priority MCP |
| --- | --- |
| Android Device management、Installation APK、Click and Slide、Pull file | `adb_mcp` |
| Android Visual control、UI Tree localization、Wireless ADB、Real-time Image | `scrcpy_vision` |
| Android Capture HTTP/HTTPS Traffic、Charles Session analysis | `charles` |
| Burp History、Repeater、Collaborator、Intruder | `burp` |
| Web Automation、Screenshot、Form、Network request、Console | `chrome_devtools` |
| JS Breakpoint、Source code search、XHR Initiate chain、Function tracing | `js_reverse` |
| Official Documentation Retrieval、Code example query | `context7` |
| General web scraping/Pull Web Page Content | `fetch` |
| Local file rapid search | `everything_search` |
| Android Dynamic injection、Frida attach/spawn | `frida_mcp` |
| Binary static analysis、IDA Batch rename/Decompile/Type fixing | `ida_pro_mcp` |
| APK Decompile、Manifest、Class/Method/xref Query | `jadx` |
| Memory map、Long-term structured memory | `memory` |
| Break Down Complex Problems | `sequential_thinking` |

### 2.5 Common combination workflows

#### Android App Analysis

- Static:`jadx`
- Dynamic:`frida_mcp`
- Packet capture:`charles`
- Device control:`adb_mcp`
- Visualization/UI Automation:`scrcpy_vision`

#### Web Front-end reverse engineering

- Page operation:`chrome_devtools`
- JS Breakpoints and Source Code Search:`js_reverse`
- HTTP Replay and Security Testing:`burp`

#### Native / APK So Reverse engineering

- IDA Static Analysis:`ida_pro_mcp`
- Runtime hook:`frida_mcp`
- Device-side assistance:`adb_mcp` / `scrcpy_vision`

---

## 3. MCP Resource class generic interface

These three types of functions are not specific business servers but rather "access MCP General capability of "Exposed Server Resources."

### 3.1 `list_mcp_resources`

- Function: List a certain MCP Resources open to the server or all servers
- Typical use case: Find directly readable files、Context、Database schema、Configuration snippet
- Parameters:
  - `server`: Optional, specify server name
  - `cursor`: Optional, pagination cursor
- Suitable skill Description: First enumerate resources, then decide whether to call `read_mcp_resource`

Example:

```json
{
  "server": "some_server"
}
```

### 3.2 `list_mcp_resource_templates`

- Purpose: List parameterized resource templates
- Typical use: Discovering resources for "parameterized reading," such as by table name、By primary key、Resources queried by path.
- Parameters:
  - `server`
  - `cursor`
- Suitable skill Description: When resources are not fixed URIInstead, it is "template URIPlease check this first when "

### 3.3 `read_mcp_resource`

- Function: read specific resource content
- Parameters:
  - `server`: Server Name
  - `uri`Resource URI
- Suitable scenarios:
  - Read Configuration
  - Read schema
  - Read service context
  - Read shared state

Example:

```json
{
  "server": "some_server",
  "uri": "resource://example/path"
}
```

---

## 4. `adb_mcp`:Android Device Control and File Interaction

### 4.1 Location

`adb_mcp` Is the most fundamental Android Device interaction layer, suitable for:

- Device List and Status Confirmation
- Installation/Uninstall APK
- Screenshot、Screen recording
- Input text、Click、Slide、Send key presses
- Pull/Push files
- Read logcat、Battery、Memory、Store information

If your skill Needs to "control the device itself," prioritizing it.

### 4.2 Common Workflow

1. `list_devices` Confirm device  
2. `get_device_info` / `get_battery_info` Environment Judgment  
3. `install_app` Or `list_packages`  
4. `send_tap` / `send_swipe` / `send_text` Driver Interaction  
5. `take_screenshot` / `record_screen` Leave evidence  
6. `get_logcat` Debugging  

### 4.3 Method list

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__adb_mcp__list_devices` | None | List connected Android Device | Task entry, first confirm whether the device is online |
| `mcp__adb_mcp__get_device_info` | `device_id?` | Read device details | Check model、System version、Serial number |
| `mcp__adb_mcp__get_battery_info` | `device_id?` | Read battery status | Confirm battery level before long-term testing |
| `mcp__adb_mcp__get_memory_info` | `device_id?` | Read memory information | performance/Stability investigation |
| `mcp__adb_mcp__get_storage_info` | `device_id?` | Read storage information | Check if there is enough space for installation/Screen recording |
| `mcp__adb_mcp__clear_logcat` | `device_id?` | Empty logcat | Perform a clean log capture |
| `mcp__adb_mcp__get_logcat` | `device_id?`, `filter_tag?`, `lines?` | Read logs | Crash、Network、SSL、Debugging and troubleshooting |
| `mcp__adb_mcp__install_app` | `apk_path`, `device_id?` | Installation APK | Deploy test package |
| `mcp__adb_mcp__uninstall_app` | `package_name`, `device_id?` | Uninstall Application | Cleaning environment |
| `mcp__adb_mcp__list_packages` | `device_id?`, `system_apps?` | List installation package names | Find target package name |
| `mcp__adb_mcp__list_files` | `remote_path`, `device_id?` | View device directory | Find Cache、Configuration、Export files |
| `mcp__adb_mcp__pull_file` | `remote_path`, `local_path`, `device_id?` | Pull files from the device to local | Export database、Log、Cache |
| `mcp__adb_mcp__push_file` | `local_path`, `remote_path`, `device_id?` | Push files to devices | Inference Certificate、Script、Patch |
| `mcp__adb_mcp__send_keyevent` | `keycode`, `device_id?` | Send key events | Return key、Home、Menu key |
| `mcp__adb_mcp__send_tap` | `x`, `y`, `device_id?` | Click coordinates | Automated operations |
| `mcp__adb_mcp__send_swipe` | `x1`,`y1`,`x2`,`y2`,`duration?`,`device_id?` | Slide | Scroll list、Unlock、Page turning |
| `mcp__adb_mcp__send_text` | `text`, `device_id?` | Input text | Search、Login、Form input |
| `mcp__adb_mcp__take_screenshot` | `save_path`, `device_id?` | Screenshot to local | Evidence retention、UI State confirmation |
| `mcp__adb_mcp__record_screen` | `duration?`, `save_path?`, `device_id?` | Screen recording | Documenting the reproduction process |

### 4.4 Typical call example

List devices:

```json
{}
```

Screenshot:

```json
{
  "device_id": "emulator-5554",
  "save_path": "C:\\Users\\28484\\Desktop\\screen.png"
}
```

Read recent 200 Action logs:

```json
{
  "device_id": "emulator-5554",
  "lines": 200
}
```

### 4.5 Write skill Points of attention during

- Any Android Tasks Should Almost All Be Run Once First `list_devices`
- `take_screenshot` Clearly require local absolute paths
- `get_logcat` In complex scenarios, it is recommended to `clear_logcat`
- `send_tap` / `send_swipe` Fully relies on coordinates, suitable for fixed interfaces, not suitable for highly dynamic layouts
- `push_file` With `pull_file` Installation of certificates、Log export、High-frequency tools for data retention

---

## 5. `charles`:Charles Packet capture and session analysis

### 5.1 Location

`charles` Responsible for reading and analyzing Charles Proxy Captured traffic, focusing not on "direct control" Android "Proxy," but:

- Check Charles Is it online、Is there an active packet capturing session already
- Launch or take over live captureTo obtain `capture_id`
- Structured filtering live traffic Or saved recording
- Drill down a single request to check headers、Status code、Request body/Response body preview
- Traffic by host、path、status、resource class Group analysis.
- End packet capturing and persist snapshot for future review

### 5.2 Suitable skill Type

- Android API Reverse engineering
- HTTPS Packet capture
- App Interface behavior analysis
- Parameter signature comparison before and after
- Search token、session、Encrypted fields
- Session recording、Filtering and evidence retention

### 5.3 Method list

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__charles__charles_status` | None | Check Charles Connectivity and live capture Status | Confirm whether the environment is ready |
| `mcp__charles__reset_environment` | None | Reset Charles Environment and Restore Saved Configuration | Conduct clean experiments. |
| `mcp__charles__start_live_capture` | `adopt_existing?`,`include_existing?`,`reset_session?` | Launch or take over live capture | Obtain subsequent analysis to be used `capture_id` |
| `mcp__charles__query_live_capture_entries` | `capture_id`,`cursor?`,`preset?`,`host_contains?`,`path_contains?`,`method_in?`,`status_in?`,`request_body_contains?`,`response_body_contains?`,`max_items?` | Structured filtering live Traffic | Recommended real-time retrieval entry |
| `mcp__charles__peek_live_capture` | `capture_id`,`cursor?`,`limit?` | Preview current live capture New entries in | Lightweight view of recent requests |
| `mcp__charles__read_live_capture` | `capture_id`,`cursor?`,`limit?` | Incrementally read and advance live cursor | When you need to stream new traffic |
| `mcp__charles__get_traffic_entry_detail` | `source`,`entry_id`,`capture_id?`,`recording_path?`,`include_full_body?`,`max_body_chars?` | Drill down into the details of a single flow | Lookout、body Preview、Request response details |
| `mcp__charles__group_capture_analysis` | `source`,`capture_id?`,`recording_path?`,`group_by`,`preset?`,`host_contains?`,`path_contains?`,`status_in?` | By host/path/status/resource class Grouping | Quickly find hot interfaces |
| `mcp__charles__get_capture_analysis_stats` | `source`,`capture_id?`,`recording_path?`,`preset?` | Return coarse-grained statistics | View packet capture global distribution |
| `mcp__charles__stop_live_capture` | `capture_id`,`persist?` | Stop live capture And can be persisted | End experiment and save snapshot |
| `mcp__charles__list_recordings` | None | List of saved recording files | Select historical traffic packets |
| `mcp__charles__list_sessions` | None | List history in a compatible way session | Compatibility with old naming |
| `mcp__charles__get_recording_snapshot` | `path?` | Read the metadata of the saved recorded snapshot | Offline check recording |
| `mcp__charles__analyze_recorded_traffic` | `recording_path?`,`preset?`,`host_contains?`,`path_contains?`,`method_in?`,`status_in?`,`request_body_contains?`,`response_body_contains?`,`max_items?` | Analyze historical recordings | Offline review and replay |
| `mcp__charles__query_recorded_traffic` | `host_contains?`,`http_method?`,`keyword_regex?`,`keep_request?`,`keep_response?` | Query the latest saved recording | Quick filter historical traffic |
| `mcp__charles__proxy_by_time` | `record_seconds` | Capture or read the latest historical packets for a fixed duration | Rapid time window analysis |
| `mcp__charles__filter_func` | `capture_seconds`,`host_contains?`,`http_method?`,`keyword_regex?`,`keep_request?`,`keep_response?` | Filter traffic by time window and conditions | Quickly narrow down the scope |
| `mcp__charles__throttling` | `preset` | Settings Charles Weak network/Rate limiting presets | Weak network reproduction and behavior verification |

### 5.4 Recommended workflow

1. `charles_status`  
2. Confirm Charles Listening has been enabled,Android Proxy has pointed to the packet capture machine,HTTPS Installed when needed Charles Certificate  
3. `reset_environment`(Optional, for clean experiments)  
4. `start_live_capture`  
5. Operation App  
6. `query_live_capture_entries`  
7. `get_traffic_entry_detail`  
8. `group_capture_analysis` / `get_capture_analysis_stats`  
9. `stop_live_capture`, set when necessary `persist: true`  
10. `analyze_recorded_traffic` / `query_recorded_traffic`

### 5.5 Call example

Start real-time packet capture:

```json
{
  "reset_session": true,
  "include_existing": false
}
```

Filter real-time interface traffic:

```json
{
  "capture_id": "capture-id-from-start",
  "preset": "api_focus",
  "host_contains": "api.example.com",
  "max_items": 10
}
```

### 5.6 Points to note

- `charles` MCP Will not configure for you Android System proxy; must be completed first Charles Listening、Device proxy and certificate preparation
- Prioritize real-time retrieval `query_live_capture_entries`, do not default to those that will advance the cursor `read_live_capture`
- `get_traffic_entry_detail` By default, only view previews to save context, only enable original text when truly needed `include_full_body`
- If you want to review the packet capture results, end live capture It is recommended `persist: true`
- If Charles Already running and you do not want to clear the current session, use `adopt_existing: true`

---

## 6. `burp`:Burp Suite Collaborative operation

### 6.1 Location

`burp` MCP It is aimed at Burp Suite control and data access layers, suitable for:

- Read proxy history
- Deliver the request to Repeater / Intruder
- Send HTTP/1.1、HTTP/2 Request
- Generate Collaborator Payload
- View scanner issues
- Read and write current editor content
- Adjust proxy interception、Task Execution Status
- Read and write Burp Configuration

### 6.2 Method list

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__burp__base64_encode` | `content` | Base64 Code | Construct. payload |
| `mcp__burp__base64_decode` | `content` | Base64 Decode | View encoded data |
| `mcp__burp__url_encode` | `content` | URL Code | Constructing parameters |
| `mcp__burp__url_decode` | `content` | URL Decode | Restore parameters |
| `mcp__burp__generate_random_string` | `length`,`characterSet` | Generate random strings | token、Boundary value、Probe String |
| `mcp__burp__get_active_editor_contents` | None | Get current editor content | Read manually edited requests |
| `mcp__burp__set_active_editor_contents` | `text` | Set current editor content | Auto-fill request template |
| `mcp__burp__create_repeater_tab` | `content`,`targetHostname`,`targetPort`,`usesHttps`,`tabName?` | Create new Repeater Tabs | Send requests to Repeater |
| `mcp__burp__send_to_intruder` | `content`,`targetHostname`,`targetPort`,`usesHttps`,`tabName?` | Delivered Intruder | Brute force/Batch testing |
| `mcp__burp__send_http1_request` | `content`,`targetHostname`,`targetPort`,`usesHttps` | Send HTTP/1.1 Request | Precision replay |
| `mcp__burp__send_http2_request` | `pseudoHeaders`,`headers`,`requestBody`,`targetHostname`,`targetPort`,`usesHttps` | Send HTTP/2 Request | H2 Specific scenarios |
| `mcp__burp__generate_collaborator_payload` | `customData?` | Generate OOB Domain name | SSRF / RCE / Blind XXE Testing |
| `mcp__burp__get_collaborator_interactions` | `payloadId?` | Polling OOB Interaction | Check if outbound. |
| `mcp__burp__get_proxy_http_history` | `count`,`offset` | Read proxy HTTP History | Review request |
| `mcp__burp__get_proxy_http_history_regex` | `count`,`offset`,`regex` | Filter by Regular Expression HTTP History | Precise filtering. |
| `mcp__burp__get_proxy_websocket_history` | `count`,`offset` | Read WS History | Analysis WebSocket |
| `mcp__burp__get_proxy_websocket_history_regex` | `count`,`offset`,`regex` | Regex filtering WS History | Check token、Command field |
| `mcp__burp__get_scanner_issues` | `count`,`offset` | List Scanner Findings | Vulnerability Inspection |
| `mcp__burp__output_project_options` | None | Export project-level configuration | View configuration schema |
| `mcp__burp__output_user_options` | None | Export user-level configuration | View configuration schema |
| `mcp__burp__set_project_options` | `json` | Set project-level configuration | Automated Tuning |
| `mcp__burp__set_user_options` | `json` | Set user-level configuration | User global configuration |
| `mcp__burp__set_proxy_intercept_state` | `intercepting` | Switch proxy interception | Open/Close Intercept |
| `mcp__burp__set_task_execution_engine_state` | `running` | Toggle task execution engine | Pause/Restore scanning tasks |

### 6.3 Typical call example

Create Repeater:

```json
{
  "content": "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n",
  "targetHostname": "example.com",
  "targetPort": 443,
  "usesHttps": true,
  "tabName": "home"
}
```

Generate Collaborator:

```json
{
  "customData": "ssrf-test"
}
```

### 6.4 Points to note

- `send_http2_request` The request body and header are separated, do not write the header into body
- It is recommended to `output_project_options` / `output_user_options`
- OOB Detection generally is:`generate_collaborator_payload` -> Inject business points. -> `get_collaborator_interactions`
- `get_proxy_http_history_regex` Very suitable for writing skill When doing "automatic filtering of related historical requests"

---

## 7. `chrome_devtools`: Browser Automation、Page diagnosis and performance analysis

### 7.1 Location

`chrome_devtools` Responsible for automated control of the browser page and DevTools Level observation. Core capabilities include:

- Open/Close/Select page
- Navigation、Refresh、Simulated device
- DOM Snapshot、Screenshot
- Click、Input.、Upload file
- List network requests and console information
- Execute page script
- Lighthouse Audit
- performance trace
- Heap Snapshot

If you want to "operate the page like a person in the browser," it is the preferred choice.

### 7.2 Page and context control

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__chrome_devtools__list_pages` | None | List the currently open pages |
| `mcp__chrome_devtools__new_page` | `url`,`background?`,`isolatedContext?`,`timeout?` | Open a new tab and visit URL |
| `mcp__chrome_devtools__select_page` | `pageId`,`bringToFront?` | Switch the current operation page |
| `mcp__chrome_devtools__close_page` | `pageId` | Close page |
| `mcp__chrome_devtools__navigate_page` | `type`,`url?`,`timeout?`,`ignoreCache?`,`handleBeforeUnload?`,`initScript?` | URL Navigation、Forward、Back、Refresh |
| `mcp__chrome_devtools__resize_page` | `width`,`height` | Resize browser |
| `mcp__chrome_devtools__emulate` | `viewport?`,`colorScheme?`,`geolocation?`,`networkConditions?`,`userAgent?`,`cpuThrottlingRate?` | Device/Network/UA Simulation |

### 7.3 Page structure and screenshots

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__chrome_devtools__take_snapshot` | `filePath?`,`verbose?` | Retrieve Page a11y Tree snapshot, return elements `uid` |
| `mcp__chrome_devtools__take_screenshot` | `filePath?`,`format?`,`fullPage?`,`quality?`,`uid?` | Page or Element Screenshot |
| `mcp__chrome_devtools__wait_for` | `text`,`timeout?` | Wait for certain text to appear |

Description:

- First `take_snapshot`, and then use the contents inside `uid` Go do click/fill/hover, usually the most stable
- `uid` Is the element identifier in the current snapshot context, which may change after the snapshot is updated.

### 7.4 Page interaction

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__chrome_devtools__click` | `uid`,`dblClick?`,`includeSnapshot?` | Click element |
| `mcp__chrome_devtools__hover` | `uid`,`includeSnapshot?` | Hover elements |
| `mcp__chrome_devtools__drag` | `from_uid`,`to_uid`,`includeSnapshot?` | Drag and drop |
| `mcp__chrome_devtools__fill` | `uid`,`value`,`includeSnapshot?` | Fill a single input box |
| `mcp__chrome_devtools__fill_form` | `elements`,`includeSnapshot?` | Batch fill forms |
| `mcp__chrome_devtools__type_text` | `text`,`submitKey?` | Input text to the current focus |
| `mcp__chrome_devtools__press_key` | `key`,`includeSnapshot?` | Keyboard shortcuts、Special keys |
| `mcp__chrome_devtools__upload_file` | `uid`,`filePath`,`includeSnapshot?` | Upload file |
| `mcp__chrome_devtools__handle_dialog` | `action`,`promptText?` | Processing alert/confirm/prompt |

### 7.5 Page scripts and debugging information

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__chrome_devtools__evaluate_script` | `function`,`args?` | Execute within the page JS |
| `mcp__chrome_devtools__list_console_messages` | `includePreservedMessages?`,`pageIdx?`,`pageSize?`,`types?` | Check console logs |
| `mcp__chrome_devtools__get_console_message` | `msgid` | Get details of a single console message |
| `mcp__chrome_devtools__list_network_requests` | `includePreservedRequests?`,`pageIdx?`,`pageSize?`,`resourceTypes?` | View the network request list |
| `mcp__chrome_devtools__get_network_request` | `reqid?`,`requestFilePath?`,`responseFilePath?` | View or export request details/Body |

### 7.6 Auditing and performance

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__chrome_devtools__lighthouse_audit` | `device?`,`mode?`,`outputDirPath?` | Run Lighthouse(excluding performance scores) |
| `mcp__chrome_devtools__performance_start_trace` | `autoStop?`,`filePath?`,`reload?` | Startup performance trace |
| `mcp__chrome_devtools__performance_stop_trace` | `filePath?` | Stop performance trace |
| `mcp__chrome_devtools__performance_analyze_insight` | `insightName`,`insightSetId` | Analyze certain performance insight |
| `mcp__chrome_devtools__take_memory_snapshot` | `filePath` | Export JS Heap Snapshot |

### 7.7 Recommended workflow

#### Page automation

1. `new_page`
2. `take_snapshot`
3. `click` / `fill` / `press_key`
4. `wait_for`
5. `take_screenshot`

#### Capture page requests

1. `new_page`
2. Page interaction
3. `list_network_requests`
4. `get_network_request`

#### Performance investigation

1. `navigate_page`
2. `performance_start_trace`
3. Page Operations or reload
4. `performance_stop_trace`
5. `performance_analyze_insight`

### 7.8 Points to note

- Do DOM Prior to interaction `take_snapshot`
- Old data after page refresh `uid` Not necessarily usable anymore
- Obtain request body/When responding body, if necessary use `requestFilePath` / `responseFilePath` Grounding to file
- If you are concerned about "JS Call chains and breakpoints",`js_reverse` Often more suitable than here

---

## 8. `context7`: Real-Time Document and Example Retrieval

### 8.1 Location

`context7` Suitable for querying third-party libraries、Framework、Official documentation and code examples, especially suitable for scenarios where "the latest official usage should be referenced" in skill writing.

### 8.2 Method

#### `mcp__context7__resolve_library_id`

- Function: First parse the "library name" into Context7 Recognizable documents ID
- Parameters:
  - `libraryName`
  - `query`
- Return highlights:
  - `libraryId`
  - Library Name
  - Description
  - snippets Quantity
  - source reputation
  - benchmark score

#### `mcp__context7__query_docs`

- Function: Based on already resolved `libraryId` Retrieve documents and examples
- Parameters:
  - `libraryId`
  - `query`

### 8.3 Recommended workflow

1. `resolve_library_id`
2. Choose the most suitable `libraryId`
3. `query_docs`

### 8.4 Example

First Parse:

```json
{
  "libraryName": "Next.js",
  "query": "App Router middleware authentication examples"
}
```

Re-query:

```json
{
  "libraryId": "/vercel/next.js",
  "query": "How to protect routes in App Router middleware?"
}
```

### 8.5 Write skill Notes

- If the user provides a vague library name, first `resolve_library_id`
- This is "document question answering MCP", not just browsing the web randomly
- For technical issues, treat it primarily as an "official document retriever"

---

## 9. `everything_search`: Local file rapid search

### 9.1 Location

This is Windows Local file search MCP, suitable for large directories、Full disk、Quickly find files under blurred conditions.

### 9.2 Method

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__everything_search__search` | `query`,`maxResults?`,`parentPath?`,`filesOnly?`,`foldersOnly?`,`matchPath?`,`regex?`,`caseSensitive?`,`wholeWord?`,`sortBy?`,`sortDescending?`,`showSize?`,`showDateModified?` | Search files or directories |
| `mcp__everything_search__get_file_info` | `filename` | Obtain detailed information about a specific file |

### 9.3 Example

Searching all under the specified directory `.apk`:

```json
{
  "query": "*.apk",
  "parentPath": "C:\\Users\\28484",
  "filesOnly": true,
  "maxResults": 50
}
```

### 9.4 Applicable scenarios

- Find APK / SO / Log / Export files
- To Reverse Engineering Class skill Find target file
- Find configuration in a large directory、Script、Database、Certificate

---

## 10. `fetch`: General web scraping

### 10.1 Location

`fetch` It is "crawling the web/URL General tools for "content," suitable for:

- Pull web content
- Grab document page
- Read HTML
- Perform simple webpage content extraction

### 10.2 Method

#### `mcp__fetch__fetch`

- Parameters:
  - `url`
  - `max_length?`
  - `raw?`
  - `start_index?`
- Function:
  - Retrieve webpage content
  - can return simplified markdown Type content
  - Offset can be specified to continue reading long pages

### 10.3 Example

```json
{
  "url": "https://example.com",
  "max_length": 6000
}
```

### 10.4 Points to note

- More suitable for "known URL Content scraping", not a search engine
- If the Page Is Too Long, It Can Be Done Through `start_index` Fragmented reading
- In technical documentation scenarios, if there is `context7`, usually prioritized `context7`

---

## 11. `frida_mcp`:Android Dynamic Injection and Runtime Hook

### 11.1 Location

`frida_mcp` Yes Android Dynamic Analysis Layer, Core Uses:

- Check/Start/Stop `frida-server`
- Enumerate Applications
- Get Current Foreground Application
- `spawn` Or `attach` Into target process
- Injection Frida JS Script
- Obtain script output logs

Suitable scenarios:

- SSL Pinning Bypass
- Method parameters/Return value print
- Dynamic signature grabbing、token、header
- native/Java Layer runtime observation.

### 11.2 Method list

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__frida_mcp__check_frida_status` | None | View frida-server Whether to run | Pre-Check |
| `mcp__frida_mcp__start_frida_server` | None | Start frida-server | Dynamic analysis preparation |
| `mcp__frida_mcp__stop_frida_server` | None | Stop frida-server | Cleaning environment |
| `mcp__frida_mcp__list_applications` | None | List device applications | Find package name、Check if it's running |
| `mcp__frida_mcp__get_frontmost_application` | None | Get Current Foreground Application | Confirm the package name of the current interface |
| `mcp__frida_mcp__spawn` | `package_name`,`initial_script?`,`script_file_path?`,`output_file?` | Suspend startup and attach to the target application | Early opportunity. hook |
| `mcp__frida_mcp__attach` | `target`,`initial_script?`,`script_file_path?`,`output_file?` | Attached To PID Or package name | Injection into Running Applications |
| `mcp__frida_mcp__get_messages` | `max_messages?` | Obtain hook/log Output buffer | View script print results |

### 11.3 `attach` With `spawn` Difference

- `attach`
  - For targets already in operation
  - Can be done by PID Or package name attachment
  - Suitable for temporary observation、Late stage hook

- `spawn`
  - For injecting scripts before application recovery
  - Suitable for early class loading、Launch process、Signature initialization、SSL pinning Early bypass

### 11.4 Example

Check status:

```json
{}
```

Start and inject script file by package name:

```json
{
  "package_name": "com.example.app",
  "script_file_path": "C:\\Users\\28484\\Desktop\\hook.js",
  "output_file": "C:\\Users\\28484\\Desktop\\frida.log"
}
```

Attach already running applications and directly write inline scripts:

```json
{
  "target": "com.example.app",
  "initial_script": "Java.perform(function(){ console.log('hook loaded'); });"
}
```

### 11.5 Recommended workflow

1. `check_frida_status`
2. If not running then `start_frida_server`
3. `list_applications` Or `get_frontmost_application`
4. `spawn` Or `attach`
5. `get_messages`

### 11.6 Points to note

- Requires correct deployment of device environment `frida-server`
- `script_file_path` Priority over `initial_script`
- Most signatures/Encryption location tasks are typically:`jadx` Static positioning -> `frida_mcp` Dynamic Validation

---

## 12. `ida_pro_mcp`:IDA Pro Static Analysis and Batch Reconstruction

### 12.1 Location

`ida_pro_mcp` Is the heaviest static analysis in current capabilities MCPIt is not "only looking at decompilation," but overriding:

- Open/Switch IDA Example
- Fast survey Binary
- List functions、Global、Import、Type
- Check xref / callgraph / basic block
- Decompile、Disassembly、Export function information
- Modify comments、Rename、Declare type、Create stack variable
- Read memory、Patch byte、Patch assembly
- Use Python In IDA Contextual execution script

If skill It is aimed at native Reverse engineering、Malware code analysis、Patch、Batch rename, it is almost core.

### 12.2 Strongly recommended entry tools

#### `mcp__ida_pro_mcp__survey_binary`

This is most suitable for the first step triage Tools. It can provide at once:

- File metadata
- Segment layout
- Entry point
- Statistical information
- High-frequency strings
- High-value functions
- imports Classification
- Call graph overview

Write skill It can be clearly specified:  
"Start Analysis IDB After, call first `survey_binary`, do not blindly proceed `list_funcs`."

### 12.3 Instance and session management

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__list_instances` | None | List currently connectable IDA Example |
| `mcp__ida_pro_mcp__select_instance` | `port`,`host?` | Switch current MCP Pointing to IDA Example |
| `mcp__ida_pro_mcp__open_file` | `file_path`,`autonomous?`,`new_database?`,`switch?`,`timeout?` | Open file to new IDA Example |
| `mcp__ida_pro_mcp__server_health` | None | View Current IDB/Service health status |
| `mcp__ida_pro_mcp__server_warmup` | `build_caches?`,`init_hexrays?`,`wait_auto_analysis?` | Preheat analysis environment |
| `mcp__ida_pro_mcp__idb_save` | `path?` | Save current IDB |

### 12.4 Binary Overview and Discovery

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__survey_binary` | `detail_level?` | Binary Overview |
| `mcp__ida_pro_mcp__entity_query` | Complex query objects | Check functions/globals/imports/strings/names |
| `mcp__ida_pro_mcp__find_regex` | `pattern`,`limit?`,`offset?` | Use regex in strings to check |
| `mcp__ida_pro_mcp__find` | `targets`,`type`,`limit?`,`offset?` | Check string、Immediate Number、Data/Code Reference |
| `mcp__ida_pro_mcp__find_bytes` | `patterns`,`limit?`,`offset?` | Byte pattern search. |

### 12.5 Function and Graph Analysis

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__list_funcs` | `queries` | List functions |
| `mcp__ida_pro_mcp__func_query` | Filtering Condition Set | By size/Name/Is there a type filtering function |
| `mcp__ida_pro_mcp__func_profile` | query collection | Overview Portrait of the Function |
| `mcp__ida_pro_mcp__lookup_funcs` | `queries` | Query Function by Address or Name |
| `mcp__ida_pro_mcp__callees` | `addrs`,`limit?` | Check called functions |
| `mcp__ida_pro_mcp__callgraph` | `roots`,`max_depth?`,`max_nodes?`,`max_edges?`,`max_edges_per_func?` | Building a call graph |
| `mcp__ida_pro_mcp__basic_blocks` | `addrs`,`offset?`,`max_blocks?` | Obtain CFG Basic block |
| `mcp__ida_pro_mcp__analyze_function` | `addr`,`include_asm?` | Compact single function analysis |
| `mcp__ida_pro_mcp__analyze_batch` | `queries` | Batch multi-function comprehensive analysis |
| `mcp__ida_pro_mcp__analyze_component` | `addrs` | Perform component analysis on a set of related functions |

### 12.6 Decompile、Disassembly and export

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__decompile` | `addr` | Decompile function |
| `mcp__ida_pro_mcp__disasm` | `addr`,`offset?`,`max_instructions?`,`include_total?` | Disassembled function |
| `mcp__ida_pro_mcp__export_funcs` | `addrs`,`format?` | Export function as JSON / C Header / Prototype |

### 12.7 Cross-referencing and data flow.

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__xrefs_to` | `addrs`,`limit?` | Obtain xrefs to |
| `mcp__ida_pro_mcp__xref_query` | query collection | By direction/Type batch query xref |
| `mcp__ida_pro_mcp__trace_data_flow` | `addr`,`direction?`,`max_depth?` | Tracking Multi-hop Data Flows |
| `mcp__ida_pro_mcp__xrefs_to_field` | `queries` | Check structure field references |

### 12.8 Type system and structure recovery

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__type_query` | query collection | Check local type |
| `mcp__ida_pro_mcp__type_inspect` | `queries` | View type declarations and members |
| `mcp__ida_pro_mcp__declare_type` | `decls` | Injection C Type declaration |
| `mcp__ida_pro_mcp__set_type` | `edits` | Setting function/Variables/Local variable type |
| `mcp__ida_pro_mcp__type_apply_batch` | `batch` | Batch Application Types |
| `mcp__ida_pro_mcp__infer_types` | `addrs` | Inference Type |
| `mcp__ida_pro_mcp__enum_upsert` | `queries` | Create/Supplementary Enumeration |
| `mcp__ida_pro_mcp__search_structs` | `filter` | Search structure/Consortium |
| `mcp__ida_pro_mcp__read_struct` | `queries` | Read the field value of a structure at a certain address |

### 12.9 Stack Frame and Local Variables

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__stack_frame` | `addrs` | Obtain function stack frame |
| `mcp__ida_pro_mcp__declare_stack` | `items` | Declare Stack Variables |
| `mcp__ida_pro_mcp__delete_stack` | `items` | Delete stack variables |

### 12.10 Rename、Comments and difference validation

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__rename` | `batch` | Batch Rename Function/Data/Local/Stack variables |
| `mcp__ida_pro_mcp__set_comments` | `items` | Set comments |
| `mcp__ida_pro_mcp__append_comments` | `items` | Add comments |
| `mcp__ida_pro_mcp__diff_before_after` | `addr`,`action`,`action_args` | Application rename/type/comment Compare before and after decompilation. |

### 12.11 Raw memory read and patch

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__get_bytes` | `regions` | Read bytes |
| `mcp__ida_pro_mcp__get_int` | `queries` | Read Integer |
| `mcp__ida_pro_mcp__get_string` | `addrs` | Read String |
| `mcp__ida_pro_mcp__get_global_value` | `queries` | Read Global Variable Values |
| `mcp__ida_pro_mcp__put_int` | `items` | Write integer |
| `mcp__ida_pro_mcp__patch` | `patches` | Patch byte |
| `mcp__ida_pro_mcp__patch_asm` | `items` | Patch assembly |
| `mcp__ida_pro_mcp__undefine` | `items` | Cancel definition as raw bytes |
| `mcp__ida_pro_mcp__define_code` | `items` | Define Bytes as Code |
| `mcp__ida_pro_mcp__define_func` | `items` | Define Function |

### 12.12 Import、Global、Instruction and Entity Query

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__imports` | `count`,`offset` | Column import |
| `mcp__ida_pro_mcp__imports_query` | `queries` | By module/name filtering import |
| `mcp__ida_pro_mcp__list_globals` | `queries` | List global variables |
| `mcp__ida_pro_mcp__insn_query` | `queries` | Query Command Mode |
| `mcp__ida_pro_mcp__int_convert` | `inputs` | Digital format conversion |

### 12.13 Python Expansion

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__ida_pro_mcp__py_eval` | `code` | In IDA Executed in the environment Python Fragment |
| `mcp__ida_pro_mcp__py_exec_file` | `file_path` | Execute Entire Python Script Files |

### 12.14 Recommended workflow

#### Initial triage

1. `server_health`
2. `server_warmup`
3. `survey_binary`
4. `find_regex` / `imports_query`
5. `analyze_function` / `decompile`

#### Restore semantics

1. `decompile`
2. `stack_frame`
3. `type_query` / `type_inspect`
4. `set_type` / `declare_type`
5. `rename`
6. `diff_before_after`

#### Track sensitive strings

1. `find_regex`
2. `xrefs_to`
3. `trace_data_flow`
4. `analyze_component`

### 12.15 skill Write suggestions

- Hard-coded "first" from the beginning `survey_binary`"Usually a good strategy
- If you want to do batch renaming, it is best to put `diff_before_after` Treat as a validation step
- To analyze JNI / crypto / dispatch Table,`trace_data_flow` Very valuable
- `type_apply_batch` Suitable for "automatic repair type" skill
- `py_eval` / `py_exec_file` Suitable for advanced automation, but should carefully define script boundaries

---

## 13. `jadx`:APK Static decompilation and Android Code navigation

### 13.1 Location

`jadx` MCP Yes Android Static analysis entry, suitable for:

- Read `AndroidManifest.xml`
- Find master Activity、Components、Export component
- Search category/Method/Field
- Obtain class source code、Method source code、smali
- Check Citation Relationships
- Rename classes./Method/Field/Variables/Package

It and `ida_pro_mcp` The difference lies in:

- `jadx` More biased Java/Kotlin Layer APK
- `ida_pro_mcp` More biased native Binary / so / ELF / PE

### 13.2 Entry information and Manifest

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__jadx__get_android_manifest` | None | Obtain Manifest Full text |
| `mcp__jadx__get_main_activity_class` | None | Obtain master Activity |
| `mcp__jadx__get_main_application_classes_names` | None | Obtain the main class name under the main application package |
| `mcp__jadx__get_main_application_classes_code` | `count?`,`offset?` | Get main class code |
| `mcp__jadx__get_manifest_component` | `component_type`,`only_exported?` | Obtain activity/service/provider/receiver Component information |

### 13.3 Class and source code reading

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__jadx__get_all_classes` | `count?`,`offset?` | Retrieve all class names |
| `mcp__jadx__fetch_current_class` | None | Obtain GUI Source code of the currently selected class |
| `mcp__jadx__get_class_source` | `class_name` | Acquire a certain type of Java Source code |
| `mcp__jadx__get_smali_of_class` | `class_name` | Acquire a certain type of smali |
| `mcp__jadx__get_methods_of_class` | `class_name` | Column methods |
| `mcp__jadx__get_fields_of_class` | `class_name` | Column fields |
| `mcp__jadx__get_method_by_name` | `class_name`,`method_name` | Obtain the source code of a certain method |
| `mcp__jadx__get_selected_text` | None | Get the currently selected text |

### 13.4 Resources and strings

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__jadx__get_all_resource_file_names` | `count?`,`offset?` | List resource files |
| `mcp__jadx__get_resource_file` | `resource_name` | Read resource file content |
| `mcp__jadx__get_strings` | `count?`,`offset?` | Obtain strings.xml Content |

### 13.5 searching and referencing

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__jadx__search_classes_by_keyword` | `search_term`,`package?`,`search_in?`,`offset?`,`count?` | Cross-code search class/Method/Field/Code content |
| `mcp__jadx__search_method_by_name` | `method_name` | Search method name |
| `mcp__jadx__get_xrefs_to_class` | `class_name`,`count?`,`offset?` | Check class references |
| `mcp__jadx__get_xrefs_to_field` | `class_name`,`field_name`,`count?`,`offset?` | Query field references |
| `mcp__jadx__get_xrefs_to_method` | `class_name`,`method_name`,`count?`,`offset?` | Check method references |

### 13.6 Rename

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__jadx__rename_class` | `class_name`,`new_name` | Rename classes. |
| `mcp__jadx__rename_field` | `class_name`,`field_name`,`new_name` | Rename fields |
| `mcp__jadx__rename_method` | `method_name`,`new_name` | Rename Method |
| `mcp__jadx__rename_variable` | `class_name`,`method_name`,`variable_name`,`new_name`,`reg?`,`ssa?` | Rename variables |
| `mcp__jadx__rename_package` | `old_package_name`,`new_package_name` | Rename package |

### 13.7 Debugging related

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__jadx__debug_get_threads` | None | View debugging threads |
| `mcp__jadx__debug_get_stack_frames` | None | View the current call stack |
| `mcp__jadx__debug_get_variables` | None | view current variables |

### 13.8 Recommended workflow

#### APK Preliminary analysis

1. `get_android_manifest`
2. `get_main_activity_class`
3. `get_manifest_component`
4. `search_classes_by_keyword`
5. `get_class_source`

#### Signature/Interface Positioning

1. `search_classes_by_keyword` Search `okhttp`, `retrofit`, `sign`, `token`, `encrypt`
2. `get_xrefs_to_method`
3. `get_method_by_name`
4. Switch to if necessary `frida_mcp` Dynamic Validation

### 13.9 Points to note

- `search_classes_by_keyword` Yes `jadx` A highly valuable entry tool in
- `search_in` Specifiable `class,method,field,code,comment`
- To JNI Scene, usually `jadx` Find native Registration point,`ida_pro_mcp` Deep Dig so

---

## 14. `js_reverse`:Web Front-end JavaScript Reverse Engineering and Breakpoint Debugging

### 14.1 Location

`js_reverse` It is aimed at Web Frontend Reversal Expertise MCP. It and `chrome_devtools` The difference:

- `chrome_devtools` More page operation-focused、Network、Snapshot、performance
- `js_reverse` More biased JS Source code、Breakpoint、Call chain、XHR Initiator、Function tracing、Source code preservation

Applicable Scenarios:

- Analyze signature functions
- Tracking XHR/Fetch Initiate chain
- Locate obfuscation functions
- Search JS Keywords in the Source Code
- Retrieve variables in the execution context
- Analysis WebSocket Message Mode

### 14.2 Page and context

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__js_reverse__new_page` | `url`,`timeout?` | Create New Page |
| `mcp__js_reverse__select_page` | `pageIdx?` | List or switch pages |
| `mcp__js_reverse__navigate_page` | `type`,`url?`,`timeout?`,`ignoreCache?` | Navigation/Refresh |
| `mcp__js_reverse__select_frame` | `frameIdx?` | List or switch frame/iframe |

### 14.3 Script enumeration and source code reading

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__js_reverse__list_scripts` | `filter?` | List current page scripts |
| `mcp__js_reverse__search_in_sources` | `query`,`isRegex?`,`caseSensitive?`,`excludeMinified?`,`urlFilter?`,`maxResults?`,`maxLineLength?` | Search across all scripts |
| `mcp__js_reverse__get_script_source` | `url?`,`scriptId?`,`startLine?`,`endLine?`,`offset?`,`length?` | Read small snippets of source code |
| `mcp__js_reverse__save_script_source` | `filePath`,`url?`,`scriptId?` | Save the complete script locally |

Description:

- `get_script_source` Designed to "view parts", not pull the entire file
- Large Scripts Should Use `save_script_source`

### 14.4 Breakpoint、Tracking and execution control

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__js_reverse__set_breakpoint_on_text` | `text`,`urlFilter?`,`occurrence?`,`condition?` | Automatically set breakpoints by code text |
| `mcp__js_reverse__list_breakpoints` | None | Column breakpoint |
| `mcp__js_reverse__remove_breakpoint` | `breakpointId?`,`url?` | Remove breakpoints or XHR Breakpoint |
| `mcp__js_reverse__pause_or_resume` | None | Pause or continue execution |
| `mcp__js_reverse__step` | `direction` | Step by step over/into/out |
| `mcp__js_reverse__trace_function` | `functionName`,`logArgs?`,`logThis?`,`pause?`,`traceId?`,`urlFilter?` | Track function calls |
| `mcp__js_reverse__inject_before_load` | `script?`,`identifier?` | Inject Script Before Page Load |

### 14.5 Context analysis after breakpoint hit

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__js_reverse__get_paused_info` | `frameIndex?`,`includeScopes?`,`maxScopeDepth?` | Obtain stack and scope variables when a breakpoint is hit |
| `mcp__js_reverse__evaluate_script` | `function`,`frameIndex?`,`mainWorld?` | Execute in the current page or breakpoint frame JS |

### 14.6 Network and call chain

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__js_reverse__break_on_xhr` | `url` | For those containing targets URL 's XHR/Fetch Set Breakpoint |
| `mcp__js_reverse__list_network_requests` | `reqid?`,`pageIdx?`,`pageSize?`,`resourceTypes?`,`urlFilter?`,`includePreservedRequests?` | View request list or single request details |
| `mcp__js_reverse__get_request_initiator` | `requestId` | View which segment a request is from JS Initiate |
| `mcp__js_reverse__list_console_messages` | `msgid?`,`pageIdx?`,`pageSize?`,`types?`,`includePreservedMessages?` | View console. |

### 14.7 WebSocket Analysis

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__js_reverse__get_websocket_messages` | `wsid?`,`analyze?`,`groupId?`,`frameIndex?`,`direction?`,`show_content?`,`pageIdx?`,`pageSize?`,`urlFilter?`,`includePreservedConnections?` | List WS Connection、Analyze message grouping、Look at specific frame |

### 14.8 Screenshot

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__js_reverse__take_screenshot` | `filePath?`,`format?`,`fullPage?`,`quality?` | Screenshot |

### 14.9 Recommended workflow

#### Locate Signature Functions

1. `new_page`
2. `list_scripts`
3. `search_in_sources` Search `sign` / `token` / Path Keywords
4. `set_breakpoint_on_text`
5. Trigger Request
6. `get_paused_info`
7. `step`
8. `evaluate_script`

#### Track who initiated the request

1. Operate page
2. `list_network_requests`
3. `get_request_initiator`
4. When necessary `break_on_xhr`

#### Analyze obfuscated scripts

1. `search_in_sources`
2. `save_script_source`
3. `set_breakpoint_on_text`
4. `trace_function`

### 14.10 skill Write suggestions

- Prioritize when source code keywords are present `search_in_sources`
- Has requests URL When prioritizing `break_on_xhr` Or `get_request_initiator`
- If global variables need to be obtained in page script scope, consider `mainWorld: true`
- If the page reloads frequently, prioritize by URL Check scripts, do not excessively rely on temporary `scriptId`

---

## 15. `memory`: Structured Knowledge Graph Memory

### 15.1 Location

`memory` It is a long-term structured memory layer, not ordinary notes. It maintains an "entity-Observe-The knowledge graph of "relationships."

Suitable for:

- Recording user preferences
- Record project facts
- Record devices、Objective、Package name、Interface Name、Vulnerability points and other structured knowledge.
- Save stable facts between multi-turn tasks

### 15.2 Core object

- Entity `entity`
  - Named `name`
  - Typed `entityType`
  - Multiple observations `observations`

- Relationships. `relation`
  - `from`
  - `relationType`
  - `to`

### 15.3 Method list

| Tool | main parameters | Effect |
| --- | --- | --- |
| `mcp__memory__read_graph` | None | Read the entire graph |
| `mcp__memory__search_nodes` | `query` | Search entity/Type/Observe |
| `mcp__memory__open_nodes` | `names` | open specified entity details |
| `mcp__memory__create_entities` | `entities` | Batch create entities |
| `mcp__memory__delete_entities` | `entityNames` | Delete entity |
| `mcp__memory__add_observations` | `observations` | Add observations to the entity |
| `mcp__memory__delete_observations` | `deletions` | Remove observation |
| `mcp__memory__create_relations` | `relations` | Create relationships |
| `mcp__memory__delete_relations` | `relations` | Remove relationships |

### 15.4 Example

Create entity:

```json
{
  "entities": [
    {
      "name": "com.example.app",
      "entityType": "android_app",
      "observations": [
        "Main package name",
        "Use OkHttp"
      ]
    }
  ]
}
```

Create relationship:

```json
{
  "relations": [
    {
      "from": "com.example.app",
      "relationType": "uses",
      "to": "OkHttp"
    }
  ]
}
```

### 15.5 Suitable skill The purpose of

- In reverse skill Remember the target package name、Encryption class、so Name、Key interfaces
- In penetration testing skill Remember domain names in the middle、Vulnerability points、Scan results
- In automation skill Remember account environment、Deployment Method、Agreed path

### 15.6 Points to note

- Relationship suggestions should use active voice, for example `App uses OkHttp`
- Not suitable for storing excessively long originals, more suitable for storing "retrievable facts."

---

## 16. `sequential_thinking`Step-by-step thinking assistance.

### 16.1 Location

This is a tool for "explicit multi-step thinking," used for complex problem analysis、Correction、Branch、Verify assumptions.  
It is suitable for:

- Multi-step reverse analysis planning
- Uncertain task scheme exploration
- Need to rectify the complex decisions made earlier
- Big Task Decomposition

### 16.2 Method

#### `mcp__sequential_thinking__sequentialthinking`

Main parameters:

- `thought`
- `thoughtNumber`
- `totalThoughts`
- `nextThoughtNeeded`
- `isRevision?`
- `revisesThought?`
- `branchFromThought?`
- `branchId?`
- `needsMoreThoughts?`

### 16.3 Understanding usage

This tool is not used to "check data," but to structurally submit the inference state to the system.  
You can:

- From the 1 Start Analysis
- If you find a mistake earlier, revision
- Fork from a certain step branch
- Finally form a verified solution

### 16.4 Suitable skill Scene

- Automatic triage skill
- Multi-stage vulnerability exploitation route judgment
- In reverse "first Java Or first native" Decision
- Multi-candidate signature function filtering

### 16.5 Example

```json
{
  "thought": "First confirm whether the issue is caused by frontend signing or server-side validation. 403.",
  "thoughtNumber": 1,
  "totalThoughts": 4,
  "nextThoughtNeeded": true
}
```

### 16.6 Points to note

- This is an analysis enhancer, not an executor.
- No need to use for simple tasks
- Complexity、Fuzzing、Problems that are easy to go astray are especially valuable

---

## 17. `scrcpy_vision`:Android Visual control、UI Location and wireless debugging

### 17.1 Location

`scrcpy_vision` Put ADB、scrcpy Low latency control、Screenshot/Streaming、`uiautomator` UI Tree reading integrated into a set of tools, suitable for:

- In `serial` Core-based Android Device connection and identification.
- Based on the current page element text、`resource-id`、`content-desc` 's UI Location
- Coordinate click、Drag and drop、Long Press、Slide、Keyboard input
- Screen Wake/Unlock、Front Desk Activity、Notification、Clipboard and other status confirmations
- USB Transfer WiFi ADB Debug
- Single-frame screenshots or continuous video streams for observing interface changes and automated interactions

and `adb_mcp` Compared to that, it is more inclined towards "visual control" and "UI Layer positioning";`adb_mcp` More focused on basic device management、Installation APK、logcat、Screen recording、File transfer. Write skill Both are usually complementary rather than one or the other.

### 17.2 Suitable skill Type

- Android UI automation and page regression
- App Element positioning and interface-driven in dynamic testing
- Wireless debugging switch and remote control of real device
- Packet capture/Hook Verification of the state of the pages before and after
- Need to go through UI Tree confirmation button、Input box、Tasks in popup location
- Tasks that require continuous monitoring of device screens rather than just capturing a single image

### 17.3 Method list

#### Device connection and identification.

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_devices_list` | None | List Connected Devices | Obtain `serial`Confirm USB/WiFi Check if the connection is normal |
| `mcp__scrcpy_vision__android_devices_info` | `serial` | Read device foundation `getprop` Information | Check model、System version、ABI、Device identifier |
| `mcp__scrcpy_vision__android_adb_enableTcpip` | `serial`,`port?` | In USB Enable when connected WiFi Debug | For Wireless ADB Do preparatory work |
| `mcp__scrcpy_vision__android_adb_getDeviceIp` | `serial` | Obtain device WiFi IP | Ready `connectWifi` |
| `mcp__scrcpy_vision__android_adb_connectWifi` | `ipAddress`,`port?` | Pass WiFi Connect device | Wireless debugging |
| `mcp__scrcpy_vision__android_adb_disconnectWifi` | `ipAddress?` | Disconnect specified or all WiFi ADB Connection | Clean Up Wireless Debugging Sessions |

#### Application and runtime

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_app_start` | `serial`,`packageName`,`activity?` | Launch application or specify Activity | Open target App、Direct access to specified page |
| `mcp__scrcpy_vision__android_app_stop` | `serial`,`packageName` | Force stop application | Reset application state |
| `mcp__scrcpy_vision__android_apps_list` | `serial`,`system?` | List installed packages | Find package name、Confirm if the application is installed |
| `mcp__scrcpy_vision__android_activity_current` | `serial` | Retrieve the current foreground package name and Activity | Determine whether the current page has switched successfully |
| `mcp__scrcpy_vision__android_notifications_get` | `serial` | Export current notification details | Check verification code notification、Push copy、Package name source |

#### Screen、Clipboard and Device Status

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_screen_isOn` | `serial` | Determine if the screen is lit | Automated front check device status |
| `mcp__scrcpy_vision__android_screen_wake` | `serial` | Light up the screen | Prepare operational devices |
| `mcp__scrcpy_vision__android_screen_sleep` | `serial` | Turn off the screen | Wrap up or verify lock screen behavior |
| `mcp__scrcpy_vision__android_screen_unlock` | `serial` | Try to wake and unlock the device | Quickly access the desktop without a security lock |
| `mcp__scrcpy_vision__android_clipboard_get` | `serial` | Read clipboard content | Obtain verification code、Share Link、Copy results |
| `mcp__scrcpy_vision__android_clipboard_set` | `serial`,`text` | Attempt to set clipboard | Paste prepared text into the input box |

#### File and Shell

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_file_list` | `serial`,`path` | List directory contents of devices | View Export Directory、Cache directory、Download directory |
| `mcp__scrcpy_vision__android_file_pull` | `serial`,`remotePath`,`localPath` | Pull files from the device to local | Export logs、Images、Download File |
| `mcp__scrcpy_vision__android_file_push` | `serial`,`localPath`,`remotePath` | Push local files to the device | Push configuration、Test file、Certificate |
| `mcp__scrcpy_vision__android_shell_exec` | `serial`,`command` | Execute arbitrary `adb shell` Command | Perform advanced diagnostics when necessary、Resolution Query or Device Operation |

#### UI Tree Reading and Input Control

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_ui_dump` | `serial` | Export current page's `uiautomator` XML | Get element text、Class name、Boundary、`resource-id` |
| `mcp__scrcpy_vision__android_ui_findElement` | `serial`,`text?`,`resourceId?`,`className?`,`contentDesc?` | By UI Attribute check elements and return central coordinates | Locate Button、Input box、Popup controls |
| `mcp__scrcpy_vision__android_input_tap` | `serial`,`x`,`y` | Click coordinates | Click button、List item、Menu |
| `mcp__scrcpy_vision__android_input_longPress` | `serial`,`x`,`y`,`durationMs?` | Long Press Coordinates | Call out context menu、Drag dynamic preparation |
| `mcp__scrcpy_vision__android_input_swipe` | `serial`,`x1`,`y1`,`x2`,`y2`,`durationMs?` | Swipe the screen | Scroll list、Page turning、Pull to refresh |
| `mcp__scrcpy_vision__android_input_dragDrop` | `serial`,`startX`,`startY`,`endX`,`endY`,`durationMs?` | Drag to the target location | Drag the card、Icon、Sort items |
| `mcp__scrcpy_vision__android_input_pinch` | `serial`,`centerX`,`centerY`,`startDistance`,`endDistance`,`durationMs?` | Approximate simulation of scaling gestures | Map、Image scaling verification |
| `mcp__scrcpy_vision__android_input_keyevent` | `serial`,`keycode` | Send Android Key | Home、Back、Enter、Delete、Volume key |
| `mcp__scrcpy_vision__android_input_text` | `serial`,`text` | Input text | Login、Search、Form filling |

#### Visual capability

| Tool | main parameters | Effect | Typical usage |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_vision_snapshot` | `serial` | Pass `adb exec-out screencap -p` Get the current screen PNG | Single screenshot confirmation interface |
| `mcp__scrcpy_vision__android_vision_startStream` | `serial`,`frameFps?`,`maxFps?`,`maxSize?` | Start scrcpy+ffmpeg Continuous screen flow | Continuously observe page changes, combined with rapid input control |
| `mcp__scrcpy_vision__android_vision_stopStream` | `serial` | Stop video stream and remove resources | Tidy up and release stream resources |

### 17.4 Recommended workflow

#### Page automation and positioning

1. `android_devices_list`
2. `android_screen_isOn` / `android_screen_wake` / `android_screen_unlock`
3. If you need to use coordinate clicks or swipes later, first use `android_shell_exec` Execute `wm size` Get current resolution
4. `android_vision_snapshot` Or `android_vision_startStream`
5. `android_ui_dump` Or `android_ui_findElement`
6. `android_input_tap` / `android_input_text` / `android_input_swipe`
7. `android_activity_current` Confirm if entered the target page
8. Retain for continuous observation stream, after completion `android_vision_stopStream`

#### WiFi ADB Switch

1. USB Execute after connecting devices `android_adb_enableTcpip`
2. `android_adb_getDeviceIp`
3. `android_adb_connectWifi`
4. `android_devices_list` Confirm wireless connection has occurred
5. After testing is complete, use `android_adb_disconnectWifi` Cleanup

### 17.5 Call example

Enable WiFi Debugging:

```json
{
  "serial": "R58N123456A",
  "port": 5555
}
```

Find elements by text:

```json
{
  "serial": "R58N123456A",
  "text": "Login"
}
```

Start the continuous screen stream:

```json
{
  "serial": "R58N123456A",
  "frameFps": 5,
  "maxSize": 1080
}
```

Query Current Resolution:

```json
{
  "serial": "R58N123456A",
  "command": "wm size"
}
```

### 17.6 Points to note

- Except `android_devices_list`、`android_adb_connectWifi`、`android_adb_disconnectWifi` Aside from that, most methods require first obtaining the device. `serial`
- If scrcpy The screen flow has started, click、Slide、Input operations will prioritize faster execution scrcpy Control Channel; otherwise, fall back to ADB Input.
- If you want to send coordinates click、Long Press、Slide、Drag or pinchFirst query the current resolution; different devices、Landscape and Portrait、Scaling or screenshot size assumptions may lead to coordinate offsets
- `android_ui_findElement` Static positioning suited for the current page, recommended to re-evaluate after page changes `ui_dump` or recheck elements
- Usable `android_ui_findElement` / `android_ui_dump` Try not to hard-code coordinates directly; only revert to coordinate clicks when element location is unreliable
- `android_screen_unlock` Only applicable when not PIN/Password/Device with security locks such as patterns
- `android_clipboard_set` In Android 10+ May be subject to system limitations and does not guarantee that all devices can take effect directly.
- `android_input_pinch` Is an approximate gesture, not true multi-touch
- `android_shell_exec`、`android_file_push` will directly alter the device environment, write skill It should be clear that this is a high-risk operation
- `android_vision_startStream` The output is real-time resources rather than offline files; if it's just a single screenshot, prioritize using `android_vision_snapshot`

---

## 18. Combination skill Recommended grouping written

For further writing skill, it is more recommended to organize by "task domain" rather than mechanically splitting by "tool server name."

### 18.1 Android Static analysis skill

Priority MCP:

- `jadx`
- `everything_search`

Common processes:

1. Find APK / Resources
2. Read Manifest
3. Search key classes.
4. Pull method source code
5. Chase xref

### 18.2 Android Dynamic analysis skill

Priority MCP:

- `adb_mcp`
- `scrcpy_vision`
- `frida_mcp`
- `charles`

Common processes:

1. Confirm device
2. Install applications
3. Start as needed scrcpy Screen Flow or Read UI Tree
4. Start Charles live capture
5. Injection hook
6. View Requests、Interface and logs

### 18.3 Native Reverse engineering skill

Priority MCP:

- `ida_pro_mcp`
- `everything_search`

Common processes:

1. Find so / exe
2. `survey_binary`
3. Check string/Import
4. Decompile key functions
5. Rename、Fix Type、Trace data flow

### 18.4 Web Page automation skill

Priority MCP:

- `chrome_devtools`

Common processes:

1. Open page
2. Obtain snapshots
3. Interactive forms
4. Capture requests
5. Screenshot for evidence

### 18.5 Web JS Reverse engineering skill

Priority MCP:

- `js_reverse`
- `chrome_devtools`
- `burp`

Common processes:

1. Search source code
2. For requests URL Breakpoint
3. Trace calling chain
4. Export scripts
5. Burp Replay

### 18.6 Document retrieval skill

Priority MCP:

- `context7`
- `fetch`

Common processes:

1. `resolve_library_id`
2. `query_docs`
3. If additional page content is needed, then use `fetch`

---

## 19. Write skill Prompt templates that can be directly reused

Here are a few suitable for direct rewriting into skill The template.

### 19.1 Android Reverse engineering skill Template Fragment

```text
When users request analysis Android APK At:
1. If the task is authorized Android App Perform penetration testing, do not conduct static analysis first APK; First confirm whether the target is installed on the connected device App.
2. Prepare first burp Or charles The visibility of packet capturing, then use scrcpy_vision Open App、Drive real business clicks、Input and navigation.
3. Check first after each key action burp Or charles Has it already appeared HTTP/HTTPS Or WebSocket Packets, and combine with adb_mcp View logs、Interface anomalies and runtime status.
4. If packets are already visible and replayable, go directly to Web/API/WebSocket Security testing, by "interface action" -> Data packet -> Web The cycle of "security analysis" continues to advance different business functions.
5. Only when no packets can be captured、The package is encrypted、Plain text unavailable、The protocol remains opaque、Only Use When Unable to Replay Stably, or When It Clearly Points to Client Logic Blocking jadx Read AndroidManifest.xml、Master Activity、Export components and search okhttp/retrofit/sign/token/encrypt and keywords.
6. If Java Layer is still insufficient, using frida_mcp hook Java Or native Recover plaintext at the boundary; if found native Clue (System.loadLibrary、JNI、so File) and Java With hook Still unable to resolve, then switch to ida_pro_mcp Analysis dump Produced so.
7. If control of the device is needed、By UI Element positioning、Observe real-time footage or switch to WiFi Debugging, using scrcpy_vision; if application installation is needed、Screen recording、logcat、Basic file transfer, using adb_mcp.
```

### 19.2 Web JS Reverse engineering skill Template Fragment

```text
When users request to locate front-end signatures、When obfuscating functions or interface call chains:
1. Prioritize using js_reverse List scripts and use search_in_sources Search sign/token/hash/encode/api path And other keywords.
2. If the request is known URL, prefer to use break_on_xhr Or get_request_initiator Identify the initiation location.
3. Use on key functions set_breakpoint_on_text、trace_function、get_paused_info、step and evaluate_script Obtain runtime context.
4. If you need to save the complete script for offline analysis, use save_script_source.
5. If replication or replay of requests is necessary, coordinate with burp 's create_repeater_tab、send_http1_request、send_http2_request.
6. If page-level interaction or screenshots are needed, in conjunction chrome_devtools.
```

### 19.3 Native Binary analysis skill Template Fragment

```text
When users request binary analysis、so、Malicious samples or patch At the point:
1. Open IDA Call after. ida_pro_mcp.survey_binary Do an overview, do not proceed blindly list_funcs.
2. Prioritize from strings、imports、callgraph、Key constants、Sensitive API Start by narrowing down the scope.
3. Use on suspicious functions analyze_function / decompile / xref_query / trace_data_flow.
4. If the function's readability is poor, use rename、set_type、declare_type、stack_frame、diff_before_after Gradually restore semantics.
5. To modify the sample, use patch / patch_asm / put_int, and save if necessary IDB.
```

---

## 20. Summary of Common Considerations

### 20.1 Absolute path requirement

The following types of tools often require absolute paths:

- `adb_mcp.take_screenshot`
- `adb_mcp.record_screen`
- `adb_mcp.pull_file` / `push_file`
- `scrcpy_vision.android_file_pull` / `android_file_push`
- `frida_mcp` 's `script_file_path`、`output_file`
- `js_reverse.save_script_source`
- `chrome_devtools.take_screenshot`
- `chrome_devtools.take_memory_snapshot`
- `ida_pro_mcp.open_file`

### 20.2 Paging Parameters

Common pagination/Fragmentation parameters:

- `offset`
- `count`
- `limit`
- `pageIdx`
- `pageSize`
- `start_index`
- `length`

Write skill It is recommended to explicitly state:

- By default, take a small batch sample first
- If there are too many results, increase further limit / count

### 20.3 Discover first, then delve deeper

Many MCP There are obvious "discovery phase tools", do not dive deep right away:

- `ida_pro_mcp`: `survey_binary`
- `jadx`: `get_android_manifest` / `search_classes_by_keyword`
- `js_reverse`: `list_scripts` / `search_in_sources`
- `chrome_devtools`: `take_snapshot`
- `charles`: `query_live_capture_entries`

### 20.4 Evidence retention

Suitable for evidence retention MCP:

- `adb_mcp.take_screenshot`
- `adb_mcp.record_screen`
- `scrcpy_vision.android_vision_snapshot`
- `chrome_devtools.take_screenshot`
- `js_reverse.take_screenshot`
- `charles.get_traffic_entry_detail`
- `burp` History and Repeater

### 20.5 Most common combinations

- Android Static + Dynamic:`jadx` + `frida_mcp`
- Android Dynamic + Traffic:`adb_mcp` + `charles`
- Android Dynamic + UI Automation:`scrcpy_vision` + `frida_mcp`
- Android Packet capture + Page driven:`scrcpy_vision` + `charles`
- Web Automation + JS Reverse:`chrome_devtools` + `js_reverse`
- Web Security replay:`js_reverse` + `burp`
- Native Static + Dynamic:`ida_pro_mcp` + `frida_mcp`

---

## 21. Summary

If your goal is to "Facilitate Subsequent Writing skills", the most practical approach is not to create for each MCP Write one separately skillRather split by task domain:

- Android Static analysis
- Android Dynamic analysis and packet capture
- Web Automation
- Web JS Reverse engineering
- Native Binary analysis
- Document retrieval
- Memory and task state management

which is most worthy of prioritizing its design skill 's MCP Is:

1. `jadx`
2. `ida_pro_mcp`
3. `js_reverse`
4. `chrome_devtools`
5. `frida_mcp`
6. `charles`
7. `adb_mcp`

If you need later, I can also help you do two more things based on this document:

1. Regenerate a version "suitable for skills Simplified version MCP Quick reference table"
2. directly split this document into multiple `SKILL.md` Template skeleton
