"""Firewall Normalizer (10-Stage Deobfuscation Engine).

Provides multi-stage command string normalization to detect obfuscated attacks
including caret/backtick stripping, Base64 decoding, hex/unicode escape decoding,
environment variable expansion, string interpolation, char code assembly,
alias expansion, subcommand unpacking, and command decomposition.
"""

from __future__ import annotations

import base64
import logging
import os
import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)

# Timeout per stage in seconds (500ms)
STAGE_TIMEOUT_SECONDS = 0.5


class FirewallNormalizer:
    """10-Stage Deobfuscation Engine for Firewall Command Analysis."""

    def __init__(self) -> None:
        self._alias_map: dict[str, str] = {
            "rm": "Remove-Item",
            "ri": "Remove-Item",
            "del": "Remove-Item",
            "erase": "Remove-Item",
            "rd": "Remove-Item",
            "rmdir": "Remove-Item",
            "iex": "Invoke-Expression",
            "iwr": "Invoke-WebRequest",
            "irm": "Invoke-RestMethod",
            "icm": "Invoke-Command",
            "gci": "Get-ChildItem",
            "dir": "Get-ChildItem",
            "ls": "Get-ChildItem",
            "gc": "Get-Content",
            "cat": "Get-Content",
            "type": "Get-Content",
            "sc": "Set-Content",
            "set-content": "Set-Content",
            "ac": "Add-Content",
            "add-content": "Add-Content",
            "ni": "New-Item",
            "new-item": "New-Item",
            "cp": "Copy-Item",
            "cpi": "Copy-Item",
            "copy": "Copy-Item",
            "mv": "Move-Item",
            "mi": "Move-Item",
            "move": "Move-Item",
            "ren": "Rename-Item",
            "rni": "Rename-Item",
            "rename": "Rename-Item",
            "saps": "Start-Process",
            "start": "Start-Process",
            "kill": "Stop-Process",
            "spps": "Stop-Process",
            "gps": "Get-Process",
            "ps": "Get-Process",
            "sleep": "Start-Sleep",
            "sal": "Set-Alias",
            "sv": "Set-Variable",
            "select": "Select-Object",
            "where": "Where-Object",
            "foreach": "ForEach-Object",
            "ft": "Format-Table",
            "fl": "Format-List",
            "gl": "Get-Location",
            "pwd": "Get-Location",
            "sl": "Set-Location",
            "cd": "Set-Location",
            "chdir": "Set-Location",
            "md": "New-Item",
            "mkdir": "New-Item",
            "cls": "Clear-Host",
            "clear": "Clear-Host",
            "h": "Get-History",
            "history": "Get-History",
            "ep": "ExecutionPolicy",
        }

    def normalize(self, cmd_text: str) -> list[str]:
        """Returns list of normalized candidate strings.

        Never raises. On total failure, returns [cmd_text].
        Each stage appends new candidates; original is always included.
        """
        if not cmd_text:
            return [""]

        try:
            candidates: list[str] = [cmd_text]

            stages: list[tuple[str, Callable[[list[str]], list[str]]]] = [
                (
                    "Stage 1: Caret/Backtick Stripping",
                    self._stage1_strip_carets_backticks,
                ),
                ("Stage 2: Base64 Decoding", self._stage2_decode_base64),
                ("Stage 3: Hex Escape Decoding", self._stage3_decode_hex),
                ("Stage 4: Unicode Escape Decoding", self._stage4_decode_unicode),
                ("Stage 5: Env Variable Expansion", self._stage5_expand_env_vars),
                ("Stage 6: String Interpolation", self._stage6_interpolate_strings),
                ("Stage 7: Char Code Assembly", self._stage7_assemble_char_codes),
                ("Stage 8: Alias Expansion", self._stage8_expand_aliases),
                ("Stage 9: Subcommand Unpacking", self._stage9_unpack_subcommands),
                (
                    "Stage 10: Command Decomposition",
                    self._stage10_decompose_commands,
                ),
            ]

            # Run up to 3 passes to resolve nested obfuscations
            # (e.g. subcommand unpacking revealing aliases/encoded strings)
            for _pass in range(3):
                prev_count = len(candidates)
                for stage_name, stage_func in stages:
                    candidates = self._run_stage_with_timeout(
                        stage_name, stage_func, candidates
                    )
                if len(candidates) == prev_count:
                    break

            # Deduplicate while preserving order
            unique_candidates: list[str] = []
            seen: set[str] = set()
            for cand in candidates:
                cand_clean = cand.strip()
                if cand_clean and cand_clean not in seen:
                    seen.add(cand_clean)
                    unique_candidates.append(cand_clean)

            if not unique_candidates:
                return [cmd_text]

            return unique_candidates

        except Exception as err:  # pylint: disable=broad-exception-caught
            logger.warning("Normalizer catastrophic failure: %s", err)
            return [cmd_text]

    def _run_stage_with_timeout(
        self,
        stage_name: str,
        stage_func: Callable[[list[str]], list[str]],
        candidates: list[str],
    ) -> list[str]:
        """Runs a stage with 500ms timeout.

        Fallbacks to existing candidates on error.
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(stage_func, list(candidates))
            try:
                result = future.result(timeout=STAGE_TIMEOUT_SECONDS)
                return result
            except FuturesTimeoutError:
                logger.warning("%s timed out (>500ms), skipping stage", stage_name)
                return candidates
            except Exception as err:  # pylint: disable=broad-exception-caught
                logger.warning("%s failed: %s, skipping stage", stage_name, err)
                return candidates

    # --- STAGE IMPLEMENTATIONS ---

    def _stage1_strip_carets_backticks(self, candidates: list[str]) -> list[str]:
        """Stage 1: Strip ^ and ` obfuscation."""
        new_candidates = list(candidates)
        for cand in candidates:
            if "^" in cand or "`" in cand:
                stripped = cand.replace("^", "").replace("`", "")
                if stripped != cand and stripped not in new_candidates:
                    new_candidates.append(stripped)
                cleaned_multi = re.sub(r"[`^]+", "", cand)
                if cleaned_multi not in new_candidates:
                    new_candidates.append(cleaned_multi)
        return new_candidates

    def _stage2_decode_base64(self, candidates: list[str]) -> list[str]:
        """Stage 2: Decode Base64 payloads (-enc, EncodedCommand, FromBase64String)."""
        new_candidates = list(candidates)
        b64_args_re = re.compile(
            (
                r"(?:[-/](?:e|enc|enco|encod|encode|encoded|encodedc|encodedco|"
                r"encodedcom|encodedcomm|encodedcomma|encodedcomman|encodedcommand|ec))"
                r"[:\s]+([A-Za-z0-9+/=]{4,})"
            ),
            re.IGNORECASE,
        )
        b64_func_re = re.compile(
            (
                r"(?:\[System\.Convert\]::|\[Convert\]::)?FromBase64String\("
                r"\s*['\"]([A-Za-z0-9+/=]{4,})['\"]\s*\)"
            ),
            re.IGNORECASE,
        )
        b64_pipe_re = re.compile(
            r"(?:echo|printf)\s+['\"]?([A-Za-z0-9+/=]{4,})['\"]?\s*\|\s*base64\s+-(?:d|-decode)",
            re.IGNORECASE,
        )

        for cand in candidates:
            matches: list[str] = []
            for match in b64_args_re.finditer(cand):
                matches.append(match.group(1))
            for match in b64_func_re.finditer(cand):
                matches.append(match.group(1))
            for match in b64_pipe_re.finditer(cand):
                matches.append(match.group(1))

            for b64_str in matches:
                try:
                    raw_bytes = base64.b64decode(b64_str)
                    decoded_text = ""
                    try:
                        decoded_text = raw_bytes.decode("utf-16le").strip("\x00")
                    except UnicodeDecodeError:
                        decoded_text = raw_bytes.decode("utf-8", errors="ignore")
                    if decoded_text and decoded_text not in new_candidates:
                        new_candidates.append(decoded_text)
                except Exception as err:  # pylint: disable=broad-exception-caught
                    logger.debug("Failed to decode base64: %s", err)
                    continue
        return new_candidates

    def _stage3_decode_hex(self, candidates: list[str]) -> list[str]:
        """Stage 3: Hex Escape decoding (\\x52\\x65\\x6d → Rem)."""
        new_candidates = list(candidates)
        hex_seq_re = re.compile(r"(?:\\x[0-9a-fA-F]{2})+")

        for cand in candidates:

            def _replace_hex(match: re.Match[str]) -> str:
                hex_str = match.group(0)
                hex_bytes = bytes.fromhex(hex_str.replace("\\x", ""))
                return hex_bytes.decode("utf-8", errors="ignore")

            if "\\x" in cand:
                decoded = hex_seq_re.sub(_replace_hex, cand)
                if decoded != cand and decoded not in new_candidates:
                    new_candidates.append(decoded)
        return new_candidates

    def _stage4_decode_unicode(self, candidates: list[str]) -> list[str]:
        """Stage 4: Unicode Escape decoding (\\u0052 → R)."""
        new_candidates = list(candidates)
        uni_seq_re = re.compile(r"\\u([0-9a-fA-F]{4})")
        uni_brace_re = re.compile(r"\\u\{([0-9a-fA-F]{1,6})\}")

        for cand in candidates:
            if "\\u" in cand:
                decoded = uni_seq_re.sub(
                    lambda m: chr(int(m.group(1), 16)),
                    cand,
                )
                decoded = uni_brace_re.sub(
                    lambda m: chr(int(m.group(1), 16)),
                    decoded,
                )
                if decoded != cand and decoded not in new_candidates:
                    new_candidates.append(decoded)
        return new_candidates

    def _stage5_expand_env_vars(self, candidates: list[str]) -> list[str]:
        """Stage 5: Env Variable Expansion ($env:COMSPEC, %WINDIR%, ${IFS})."""
        new_candidates = list(candidates)
        env_defaults = {
            "COMSPEC": os.environ.get("COMSPEC", "C:\\Windows\\system32\\cmd.exe"),
            "WINDIR": os.environ.get("WINDIR", "C:\\Windows"),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "IFS": " ",
        }

        for cand in candidates:
            res = cand
            res = res.replace("${IFS}", " ").replace("$IFS", " ")

            def _replace_win_env(match: re.Match[str]) -> str:
                var_name = match.group(1).upper()
                return os.environ.get(
                    match.group(1), env_defaults.get(var_name, match.group(0))
                )

            res = re.sub(r"%([A-Za-z0-9_]+)%", _replace_win_env, res)

            def _replace_ps_env(match: re.Match[str]) -> str:
                var_name = match.group(1).upper()
                return os.environ.get(
                    match.group(1), env_defaults.get(var_name, match.group(0))
                )

            res = re.sub(
                r"\$env:([A-Za-z0-9_]+)", _replace_ps_env, res, flags=re.IGNORECASE
            )

            if res != cand and res not in new_candidates:
                new_candidates.append(res)

        return new_candidates

    def _stage6_interpolate_strings(self, candidates: list[str]) -> list[str]:
        """Stage 6: String Interpolation & Format Operators.

        Examples:
        - "Invoke-$('Expres'+'sion')" → Invoke-Expression
        - "('{1}{0}' -f 'ex','i')" → iex
        - "('i','e','x') -join ''" → iex
        """
        new_candidates = list(candidates)
        concat_re = re.compile(r"(['\"])(.*?)\1\s*\+\s*(['\"])(.*?)\3")
        subexpr_re = re.compile(r"\$\((.*?)\)")

        # PowerShell -f format operator: ("{1}{0}" -f 'ex','i') or "{0}" -f 'calc'
        fmt_op_re = re.compile(
            (
                r'(?:\(\s*)?["\']([^"\'\n\r]+)["\']\s+-f\s+'
                r'((?:["\'][^"\'\n\r]*["\']|\d+)'
                r'(?:\s*,\s*(?:["\'][^"\'\n\r]*["\']|\d+))*)(?:\s*\))?'
            ),
            re.IGNORECASE,
        )

        # PowerShell join operator: ('i','e','x') -join '' or @('i','e','x') -join ""
        join_op_re = re.compile(
            (
                r'(?:@?\(\s*(?:["\']([^"\'\n\r]*)["\']\s*,\s*)+'
                r'["\']([^"\'\n\r]*)["\']\s*\)\s*-join\s*["\']["\'])'
            ),
            re.IGNORECASE,
        )

        for cand in candidates:
            res = cand

            # 1. Resolve string concatenations: 'a' + 'b'
            prev = None
            while prev != res:
                prev = res
                res = concat_re.sub(r"\1\2\4\1", res)

            # 2. Resolve PowerShell -f formatting
            def _replace_fmt(m: re.Match[str]) -> str:
                template = m.group(1)
                args_raw = m.group(2)
                arg_tokens = re.findall(r'["\']([^"\'\n\r]*)["\']|(\d+)', args_raw)
                args = [t[0] if t[0] != "" else t[1] for t in arg_tokens]
                out = template
                for idx, arg in enumerate(args):
                    out = out.replace(f"{{{idx}}}", arg)
                return out

            res_fmt = fmt_op_re.sub(_replace_fmt, res)
            if res_fmt != res:
                res = res_fmt

            # 3. Resolve PowerShell -join
            def _replace_join(m: re.Match[str]) -> str:
                full = m.group(0)
                letters = re.findall(r'["\']([^"\'\n\r]*)["\']', full)
                if letters:
                    return "".join(letters[:-1])  # Exclude the trailing delimiter
                return full

            res = join_op_re.sub(_replace_join, res)

            # 4. Resolve subexpressions $(...)
            def _replace_subexpr(m: re.Match[str]) -> str:
                inner = m.group(1).strip()
                if (inner.startswith("'") and inner.endswith("'")) or (
                    inner.startswith('"') and inner.endswith('"')
                ):
                    return inner[1:-1]
                return inner

            res = subexpr_re.sub(_replace_subexpr, res)

            if (res.startswith('"') and res.endswith('"')) or (
                res.startswith("'") and res.endswith("'")
            ):
                res = res[1:-1]

            if res != cand and res not in new_candidates:
                new_candidates.append(res)
        return new_candidates

    # pylint: disable=too-many-locals
    def _stage7_assemble_char_codes(self, candidates: list[str]) -> list[str]:
        """Stage 7: Char Code Assembly ([char]82+[char]101+[char]109 → Rem)."""
        new_candidates = list(candidates)
        char_seq_re = re.compile(
            r"(?:(?:\[string\])?\[char\]\s*(?:0x[0-9a-fA-F]+|\d+)\s*\+?\s*)+"
        )
        char_single_re = re.compile(r"\[char\]\s*(0x[0-9a-fA-F]+|\d+)")
        char_array_join_re = re.compile(
            r"\[char\[\]\]\s*@?\(\s*([0-9a-fA-Fx,\s]+)\s*\)\s*-join\s*['\"]['\"]",
            re.IGNORECASE,
        )

        for cand in candidates:
            # Pattern A: [char]82+[char]101
            for match in char_seq_re.finditer(cand):
                seq_str = match.group(0)
                codes = char_single_re.findall(seq_str)
                if codes:
                    decoded_chars = []
                    for code_str in codes:
                        base = 16 if code_str.lower().startswith("0x") else 10
                        decoded_chars.append(chr(int(code_str, base)))
                    assembled = "".join(decoded_chars)
                    cand_replaced = cand.replace(seq_str, assembled)
                    if cand_replaced not in new_candidates:
                        new_candidates.append(cand_replaced)

            # Pattern B: [char[]]@(82,101,109) -join ''
            for match in char_array_join_re.finditer(cand):
                full_m = match.group(0)
                nums_str = match.group(1)
                nums = re.findall(r"0x[0-9a-fA-F]+|\d+", nums_str)
                decoded_chars = []
                for n in nums:
                    base = 16 if n.lower().startswith("0x") else 10
                    decoded_chars.append(chr(int(n, base)))
                assembled = "".join(decoded_chars)
                cand_replaced = cand.replace(full_m, assembled)
                if cand_replaced not in new_candidates:
                    new_candidates.append(cand_replaced)

        return new_candidates

    def _stage8_expand_aliases(self, candidates: list[str]) -> list[str]:
        """Stage 8: Alias & Flag Expansion (rm→Remove-Item, -rf→-Recurse -Force)."""
        new_candidates = list(candidates)
        for cand in candidates:
            words = cand.split()
            if not words:
                continue
            first_word = words[0].lower()
            base_cand = cand
            if first_word in self._alias_map:
                base_cand = self._alias_map[first_word] + cand[len(words[0]) :]
                if base_cand not in new_candidates:
                    new_candidates.append(base_cand)

            # Flag expansion for PowerShell & git
            expanded = base_cand
            expanded = re.sub(r"(?i)(^|\s)-rf(\s|$)", r"\1-Recurse -Force\2", expanded)
            expanded = re.sub(r"(?i)(^|\s)-fr(\s|$)", r"\1-Force -Recurse\2", expanded)
            expanded = re.sub(r"(?i)(^|\s)-rec(\s|$)", r"\1-Recurse\2", expanded)
            expanded = re.sub(r"(?i)(^|\s)-r(\s|$)", r"\1-Recurse\2", expanded)
            expanded = re.sub(r"(?i)(^|\s)-nop(\s|$)", r"\1-NoProfile\2", expanded)
            expanded = re.sub(
                r"(?i)(^|\s)-(?:ep|executionpolicy)\s+bypass(\s|$)",
                r"\1Set-ExecutionPolicy Bypass\2",
                expanded,
            )
            expanded = re.sub(
                r"(?i)(^|\s)-(?:ep|executionpolicy)\s+unrestricted(\s|$)",
                r"\1Set-ExecutionPolicy Unrestricted\2",
                expanded,
            )
            expanded = re.sub(
                r"(?i)(^|\s)-(?:w|window|windowstyle)\s+hid(?:den)?(\s|$)",
                r"\1-WindowStyle Hidden\2",
                expanded,
            )

            if "git" in expanded.lower() and "push" in expanded.lower():
                git_expanded = re.sub(r"(?i)(^|\s)-f(\s|$)", r"\1--force\2", expanded)
                if git_expanded not in new_candidates:
                    new_candidates.append(git_expanded)

            if expanded != base_cand and expanded not in new_candidates:
                new_candidates.append(expanded)

        return new_candidates

    def _stage9_unpack_subcommands(self, candidates: list[str]) -> list[str]:
        """Stage 9: Subcommand Unpacking (powershell -c "...", bash -c "...")."""
        new_candidates = list(candidates)
        subcmd_re = re.compile(
            r"(?:powershell|pwsh|cmd|bash|sh|zsh|python|python3|node)"
            r"\s+(?:-[a-zA-Z0-9/]+\s+)*['\"]([^'\"]+)['\"]",
            re.IGNORECASE,
        )

        for cand in candidates:
            for match in subcmd_re.finditer(cand):
                inner_cmd = match.group(1).strip()
                if inner_cmd and inner_cmd not in new_candidates:
                    new_candidates.append(inner_cmd)
        return new_candidates

    def _stage10_decompose_commands(self, candidates: list[str]) -> list[str]:
        """Stage 10: Command Decomposition (&&, ||, ;, |, &, \\n)."""
        new_candidates = list(candidates)
        split_pattern = re.compile(r"&&|\|\||;|\||&|\n")

        for cand in candidates:
            parts = split_pattern.split(cand)
            if len(parts) > 1:
                for part in parts:
                    clean_part = part.strip()
                    if clean_part and clean_part not in new_candidates:
                        new_candidates.append(clean_part)
        return new_candidates
