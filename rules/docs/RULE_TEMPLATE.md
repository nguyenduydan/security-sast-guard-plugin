# CUSTOM_RULE_TEMPLATE — My Custom Security Rule

## Description
Mô tả ngắn gọn về lỗ hổng bảo mật mà rule này phát hiện.
Ví dụ: Phát hiện sử dụng hàm `eval()` với đầu vào từ người dùng, có nguy cơ RCE.

## Severity
High

<!-- Các giá trị hợp lệ: Critical | High | Medium | Low | Info -->

## Category
Nêu category phù hợp: owasp-api-2023 | owasp-web-2021 | web-app-specific | cwe-sans-top25 | nist-800-53

## Patterns

Thêm các regex patterns để phát hiện lỗ hổng. Mỗi pattern trên 1 dòng:

```regex
# Phát hiện eval() với biến động
eval\s*\(\s*[a-zA-Z_$][a-zA-Z0-9_$]*

# Phát hiện exec() với input không validate
exec\s*\(\s*request\.(GET|POST|params)
```

## References
- OWASP: https://owasp.org/
- CWE: https://cwe.mitre.org/

---
<!-- Sau khi thêm xong, chạy lệnh để convert sang JSON:
     /sast-rules add <path/to/MY_RULE.md>
-->
