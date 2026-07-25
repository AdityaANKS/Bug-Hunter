# File vulnerabilities
English: File Vulnerabilities
- Entry Count: 7
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## File upload bypass
- ID: file-upload-bypass
- Difficulty: intermediate
- Subcategory: File upload
- Tags: upload, bypass, webshell
- Original Extracted Source: original extracted web-security-wiki source/file-upload-bypass.md
Description:
File upload limitation bypass techniques
Prerequisites:
- Target has file upload functionality
- There are upload restrictions
Execution Outline:
1. Extension bypass
2. Content-Type
3. Image Malware
4. Space Bypass
## Arbitrary file download
- ID: file-download
- Difficulty: beginner
- Subcategory: Download
- Tags: file-download, lfi, leak
- Original Extracted Source: original extracted web-security-wiki source/file-download.md
Description:
Exploiting path control flaws in the file download function to download any sensitive files on the server.
Prerequisites:
- Target has file download functionality
- File path parameters are controllable
- Server-side did not strictly filter the path
Execution Outline:
1. Identify file download interfaces
2. Path Traversal to Download Sensitive Files
3. Download source code and database configuration
4. Automated bulk sensitive file detection
## Race Condition
- ID: file-competition
- Difficulty: advanced
- Subcategory: Race Condition
- Tags: race-condition, file-upload
- Original Extracted Source: original extracted web-security-wiki source/file-competition.md
Description:
Utilize file upload/Race conditions during processing(Race Condition), perform malicious operations within the time window between security checks and file usage
Prerequisites:
- Target has file upload functionality
- Server-side upload first then check processing flow
- Can access uploaded files with high concurrency
- Understand the temporary file storage path
Execution Outline:
1. Identify Race Condition Windows
2. Exploiting race conditions - Concurrent upload and access
3. PythonConcurrent race exploitation scripts
4. .htaccessrace condition write
## Path traversal
- ID: file-traversal
- Difficulty: beginner
- Subcategory: Traversal
- Tags: traversal, file
- Original Extracted Source: original extracted web-security-wiki source/file-traversal.md
Description:
Utilizing Path Traversal(../)Sequence breakthrough to bypass directory restrictions for file access, reading or writingWebAny files outside the root directory.
Prerequisites:
- The target has file read access/Contains functionality
- File path parameters are controllable
- Server-side path filtering is not strict
Execution Outline:
1. Basic path traversal testing
2. encoding bypass path filtering
3. WindowsUnique path traversal
4. LFIToRCEUpgrade
## Zip Slip
- ID: file-zip-slip
- Difficulty: intermediate
- Subcategory: Zip
- Tags: zip-slip, file, rce
- Original Extracted Source: original extracted web-security-wiki source/file-zip-slip.md
Description:
Exploit maliciously constructed compressed package files(ZIP/TAR)Path traversal allows arbitrary file writing, overwriting critical files on the server or writing in.Webshell
Prerequisites:
- Target existsZIP/TARFile upload and automatic decompression function
- Decompression libraries did not filter path traversal in file names
- UnderstandWebPath to root directory or other critical directories
Execution Outline:
1. DetectionZIPUpload and unzip functionality
2. Construct.Zip SlipMalicious compressed package
3. Upload and validateZip Slip
4. TARPackageZip SlipVariants
## MIMEType bypass
- ID: file-mime
- Difficulty: beginner
- Subcategory: MIME
- Tags: mime, bypass
- Original Extracted Source: original extracted web-security-wiki source/file-mime.md
Description:
By ForgingMIMEType(Content-Type)Bypass File Upload Type Check, Upload Malicious Executable Files
Prerequisites:
- Target has file upload functionality
- The server only accessesContent-TypeDetermine file type
- Understanding the target's permissionsMIMEType
Execution Outline:
1. Detect file type checking mechanisms
2. MIMEType spoofing uploadWebshell
3. Magic BytesForgery
4. Validate Upload Results
## Null byte truncation
- ID: file-null-byte
- Difficulty: intermediate
- Subcategory: Null Byte
- Tags: null-byte, bypass
- Original Extracted Source: original extracted web-security-wiki source/file-null-byte.md
Description:
Exploit null bytes(%00/\x00)Validate the truncation of the file extension to bypass file upload whitelist restrictions
Prerequisites:
- The target uses whitelisting to validate file extensions
- Backend language or library affected by null byte truncation(PHP<5.3.4, JavaOld version)
- Server path concatenation has truncation points
Execution Outline:
1. Empty byte truncation principles and environmental detection
2. File upload empty byte truncation
3. File Includes Null Byte Truncation
4. Modern alternatives(PHP>=5.3.4)

