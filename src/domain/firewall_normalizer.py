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
            "rd": "Remove-Item",
            "rmdir": "Remove-Item",
            "iex": "Invoke-Expression",
            "iwr": "Invoke-WebRequest",
            "icm": "Invoke-Command",
            "gci": "Get-ChildItem",
            "dir": "Get-ChildItem",
            "gc": "Get-Content",
            "sc": "Set-Content",
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

            # Run up to 2 passes to resolve nested obfuscations
            # (e.g. subcommand unpacking revealing aliases/encoded strings)
            for _pass in range(2):
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
                if stripped != cand:
                    new_candidates.append(stripped)
        return new_candidates

    def _stage2_decode_base64(self, candidates: list[str]) -> list[str]:
        """Stage 2: Decode Base64 payloads (-enc, EncodedCommand, FromBase64String)."""
        new_candidates = list(candidates)
        b64_args_re = re.compile(
            r"(?:-enc|-encodedcommand|-e)\s+([A-Za-z0-9+/=]{8,})",
            re.IGNORECASE,
        )
        b64_func_re = re.compile(
            r"FromBase64String\(\s*['\"]([A-Za-z0-9+/=]{8,})['\"]\s*\)",
            re.IGNORECASE,
        )
        b64_pipe_re = re.compile(
            r"echo\s+['\"]?([A-Za-z0-9+/=]{8,})['\"]?\s*\|\s*base64\s+-d",
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
                    if decoded_text:
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
                if decoded != cand:
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
                if decoded != cand:
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

            if res != cand:
                new_candidates.append(res)

        return new_candidates

    def _stage6_interpolate_strings(self, candidates: list[str]) -> list[str]:
        """Stage 6: String Interpolation.

        Example: "Invoke-$('Expres'+'sion')" → Invoke-Expression.
        """
        new_candidates = list(candidates)
        concat_re = re.compile(r"(['\"])(.*?)\1\s*\+\s*(['\"])(.*?)\3")
        subexpr_re = re.compile(r"\$\((.*?)\)")

        for cand in candidates:
            res = cand
            prev = None
            while prev != res:
                prev = res
                res = concat_re.sub(r"\1\2\4\1", res)

            def _replace_subexpr(m: re.Match[str]) -> str:
                inner = m.group(1).strip()
                if (inner.startswith("'") and inner.endswith("'")) or (
                    inner.startswith('"') and inner.endswith('"')
                ):
                    return inner[1:-1]
                return inner

            res = subexpr_re.sub(_replace_subexpr, res)

            if res.startswith('"') and res.endswith('"'):
                res = res[1:-1]

            if res != cand:
                new_candidates.append(res)
        return new_candidates

    def _stage7_assemble_char_codes(self, candidates: list[str]) -> list[str]:
        """Stage 7: Char Code Assembly ([char]82+[char]101+[char]109 → Rem)."""
        new_candidates = list(candidates)
        char_seq_re = re.compile(r"(?:\[char\]\s*(?:0x[0-9a-fA-F]+|\d+)\s*\+?\s*)+")
        char_single_re = re.compile(r"\[char\]\s*(0x[0-9a-fA-F]+|\d+)")

        for cand in candidates:
            for match in char_seq_re.finditer(cand):
                seq_str = match.group(0)
                codes = char_single_re.findall(seq_str)
                decoded_chars = []
                for code_str in codes:
                    base = 16 if code_str.startswith("0x") else 10
                    decoded_chars.append(chr(int(code_str, base)))
                assembled = "".join(decoded_chars)
                cand_replaced = cand.replace(seq_str, assembled)
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
            r"(?:powershell|pwsh|cmd|bash|sh|zsh|python|python3)"
            r"\s+(?:-[a-zA-Z/]+\s+)*['\"]([^'\"]+)['\"]",
            re.IGNORECASE,
        )

        for cand in candidates:
            for match in subcmd_re.finditer(cand):
                inner_cmd = match.group(1).strip()
                if inner_cmd:
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
                    if clean_part:
                        new_candidates.append(clean_part)
        return new_candidates
