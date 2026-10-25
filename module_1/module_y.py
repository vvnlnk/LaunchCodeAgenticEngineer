"""
Formatting and reporting utilities for the parallel agent-session example.

This module is intentionally small and deterministic. It is designed for
the "Session B" agent task: improve docstrings in this file and update README.md,
without modifying any test files.
"""

from __future__ import annotations


def format_currency(amount: float) -> str:
    """Format a number as a US-dollar string with thousands separators.

    The value is rounded to two decimal places. Negative amounts place the
    minus sign before the dollar sign.

    Examples:
        >>> format_currency(1234.5)
        '$1,234.50'
        >>> format_currency(-42)
        '-$42.00'
    """
    if amount < 0:
        return f"-${abs(amount):,.2f}"
    return f"${amount:,.2f}"


def build_report_title(project_name: str, version: str) -> str:
    """Build a report title in the form ``"<project> — <version>"``.

    Internal runs of whitespace in ``project_name`` are collapsed to single
    spaces, and both values are stripped. A blank project name falls back to
    ``"Untitled Project"`` and a blank version falls back to ``"draft"``.

    Examples:
        >>> build_report_title("  Apollo   Launch ", " v1.2 ")
        'Apollo Launch — v1.2'
        >>> build_report_title("", "")
        'Untitled Project — draft'
    """
    clean_project = " ".join(project_name.strip().split())
    clean_version = version.strip()

    if not clean_project:
        clean_project = "Untitled Project"
    if not clean_version:
        clean_version = "draft"

    return f"{clean_project} — {clean_version}"


def mask_email(email: str) -> str:
    """Return ``email`` with the local part masked and the domain lowercased.

    The first and last characters of the local part are kept and everything in
    between is replaced with ``*``. A one-character local part becomes ``*`` and
    a two-character local part keeps only its first character. Surrounding
    whitespace is stripped; only the first ``@`` separates local part and domain.

    Raises:
        ValueError: If ``email`` has no ``@``, or the local part or domain is empty.

    Examples:
        >>> mask_email("Jane.Doe@Example.COM")
        'J******e@example.com'
        >>> mask_email("ab@x.io")
        'a*@x.io'
    """
    email = email.strip()
    if "@" not in email:
        raise ValueError("email must contain @")

    local_part, domain = email.split("@", 1)
    if not local_part or not domain:
        raise ValueError("email must include a local part and domain")

    if len(local_part) == 1:
        masked_local = "*"
    elif len(local_part) == 2:
        masked_local = local_part[0] + "*"
    else:
        masked_local = local_part[0] + "*" * (len(local_part) - 2) + local_part[-1]

    return f"{masked_local}@{domain.lower()}"


def generate_summary_line(name: str, status: str, score: int) -> str:
    """Build a one-line status summary in the form ``"<Name>: <status> (<score>)"``.

    The name is whitespace-normalized and title-cased, falling back to
    ``"Unknown"`` when blank. The status is stripped, lowercased, and has
    underscores replaced with spaces. ``score`` is included as-is.

    Examples:
        >>> generate_summary_line("  ada   lovelace ", "IN_PROGRESS", 87)
        'Ada Lovelace: in progress (87)'
    """
    display_name = " ".join(name.strip().split()).title()
    display_status = status.strip().lower().replace("_", " ")

    if not display_name:
        display_name = "Unknown"

    return f"{display_name}: {display_status} ({score})"


def create_markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    """Render ``rows`` as a GitHub-flavored Markdown table.

    Columns appear in the order given by ``columns``, which also supplies the
    header text. Each cell is ``str(row[column])``; a missing key yields an
    empty cell, and keys not listed in ``columns`` are ignored. Cell values are
    not escaped, so a ``|`` inside a value will break the table layout.

    Raises:
        ValueError: If ``columns`` is empty.

    Examples:
        >>> print(create_markdown_table([{"name": "Ada", "score": 90}], ["name", "score"]))
        | name | score |
        | --- | --- |
        | Ada | 90 |
    """
    if not columns:
        raise ValueError("columns cannot be empty")

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"

    body_lines = []
    for row in rows:
        values = [str(row.get(column, "")) for column in columns]
        body_lines.append("| " + " | ".join(values) + " |")

    return "\n".join([header, separator, *body_lines])


def truncate_text(text: str, max_length: int = 80) -> str:
    """Collapse whitespace in ``text`` and shorten it to at most ``max_length`` characters.

    Text that already fits after whitespace normalization is returned unchanged.
    Longer text is cut to ``max_length - 3`` characters, trailing whitespace is
    removed, and ``"..."`` is appended, so the result never exceeds
    ``max_length``.

    Raises:
        ValueError: If ``max_length`` is less than 4.

    Examples:
        >>> truncate_text("The quick brown fox jumps", max_length=12)
        'The quick...'
    """
    if max_length < 4:
        raise ValueError("max_length must be at least 4")

    clean_text = " ".join(text.strip().split())
    if len(clean_text) <= max_length:
        return clean_text

    return clean_text[: max_length - 3].rstrip() + "..."
