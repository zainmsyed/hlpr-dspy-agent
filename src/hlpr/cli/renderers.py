"""Output renderers for CLI TUI feature.

This module provides different output formatters for CLI results, supporting
rich terminal output, JSON, Markdown, and plain text formats.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

# sentinel to detect explicit None vs omitted kwargs
# rich imports for renderer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

_UNSET = object()

__all__ = [
    "BaseRenderer",
    "JsonRenderer",
    "MarkdownRenderer",
    "PlainTextRenderer",
    "RichRenderer",
]


class BaseRenderer(ABC):
    @abstractmethod
    def render(self, data: Any) -> str:
        raise NotImplementedError


class RichRenderer(BaseRenderer):
    """Renderer for rich terminal output using Rich library.

    Formats results with panels, tables, and styled text for an enhanced
    terminal experience.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render(self, data: Any) -> str:
        """Render data using Rich formatting and return as string.

        Args:
            data: ProcessingResult, list of results, or dict-like object

        Returns:
            Formatted string suitable for terminal display
        """
        # Capture Rich output to string
        console = Console(record=True, width=self.console.options.max_width)

        if hasattr(data, "model_dump"):  # Pydantic model
            self._render_processing_result(console, data)
        elif isinstance(data, list):
            self._render_result_list(console, data)
        elif isinstance(data, dict):
            self._render_dict(console, data)
        else:
            console.print(f"[yellow]Unsupported data type: {type(data)}[/yellow]")
            console.print(str(data))

        return console.export_text()

    def _render_processing_result(self, console: Console, result: Any) -> None:
        """Render a ProcessingResult model."""
        data = result.model_dump() if hasattr(result, "model_dump") else result

        # File information panel (always shown)
        file_info = data.get("file", {})
        file_path = file_info.get("path", "Unknown File")

        # Show file info first
        file_details = f"Path: {file_path}"
        if file_info.get("size_bytes"):
            size_mb = file_info["size_bytes"] / (1024 * 1024)
            file_details += f"\nSize: {size_mb:.2f} MB"
        if file_info.get("mime_type"):
            file_details += f"\nType: {file_info['mime_type']}"

        file_panel = Panel(
            file_details,
            title=f"[bold cyan]File: {file_path}[/bold cyan]",
            border_style="cyan",
        )
        console.print(file_panel)

        # Main summary panel
        if data.get("summary"):
            summary_panel = Panel(
                data["summary"],
                title="[bold green]Summary[/bold green]",
                border_style="green",
            )
            console.print(summary_panel)

        # Error panel if present
        if data.get("error"):
            error_info = data["error"]
            error_text = f"Code: {error_info.get('code', 'Unknown')}\n"
            error_text += f"Message: {error_info.get('message', 'No message')}"
            if error_info.get("details"):
                error_text += f"\nDetails: {error_info['details']}"

            error_panel = Panel(
                error_text,
                title="[bold red]Error[/bold red]",
                border_style="red",
            )
            console.print(error_panel)

        # Metadata table if present
        if data.get("metadata"):
            self._render_metadata_table(console, data["metadata"])

    def _render_result_list(self, console: Console, results: list) -> None:
        """Render a list of processing results."""
        title = f"[bold blue]Processing Results ({len(results)} files)[/bold blue]"
        console.print(title)
        console.print()

        for i, result in enumerate(results, 1):
            console.print(f"[bold]Result {i}:[/bold]")
            self._render_processing_result(console, result)
            if i < len(results):  # Add separator except for last item
                console.print("─" * 50)

    def _render_dict(self, console: Console, data: dict) -> None:
        """Render a generic dictionary."""
        panel = Panel(
            "\n".join(f"[bold]{k}:[/bold] {v}" for k, v in data.items()),
            title="[bold blue]Results[/bold blue]",
            border_style="blue",
        )
        console.print(panel)

    def _render_metadata_table(self, console: Console, metadata: dict) -> None:
        """Render metadata as a styled table."""
        table = Table(title="Processing Metadata", show_header=True)
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        for key, value in metadata.items():
            if value is not None:
                if isinstance(value, datetime):
                    value_str = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    value_str = str(value)
                table.add_row(key.replace("_", " ").title(), value_str)

        console.print(table)


@dataclass
class JsonFormattingOptions:
    indent: int | None = 2
    sort_keys: bool = True
    ensure_ascii: bool = False


class JsonRenderer(BaseRenderer):
    """Renderer for JSON output.

    Converts processing results to structured JSON format suitable for
    programmatic consumption or further processing.
    """

    def __init__(
        self,
        options: JsonFormattingOptions | None = None,
        *,
        indent: object = _UNSET,
        sort_keys: object = _UNSET,
        ensure_ascii: object = _UNSET,
    ) -> None:
        # Backwards-compatible constructor: callers may pass `indent` and
        # `sort_keys` kwargs (older API). Prefer explicit `options` if given.
        if options is not None:
            self.options = options
        else:
            # Build options from provided kwargs or defaults. Use sentinel to
            # distinguish between omitted args and explicit `None`.
            opts = JsonFormattingOptions()
            if indent is not _UNSET:
                opts.indent = indent
            if sort_keys is not _UNSET:
                opts.sort_keys = sort_keys
            if ensure_ascii is not _UNSET:
                opts.ensure_ascii = ensure_ascii
            self.options = opts

    def render(self, data: Any) -> str:
        """Render data as formatted JSON string.

        Args:
            data: ProcessingResult, list of results, or serializable object

        Returns:
            JSON formatted string
        """
        # Convert pydantic models to dict
        if hasattr(data, "model_dump"):
            json_data = data.model_dump(mode="json")
        elif isinstance(data, list):
            json_data = [
                item.model_dump(mode="json") if hasattr(item, "model_dump") else item
                for item in data
            ]
        else:
            # We only support pydantic models or list-of-models here
            raise NotImplementedError(
                "JsonRenderer does not support raw dict input yet"
            )

        # Add metadata about the rendering
        output = {
            "data": json_data,
            "meta": {
                "renderer": "JsonRenderer",
                "timestamp": datetime.now(UTC).isoformat(),
                "format_version": "1.0",
            },
        }

        return json.dumps(
            output,
            indent=self.options.indent,
            sort_keys=self.options.sort_keys,
            default=str,  # Convert non-serializable objects to strings
            ensure_ascii=self.options.ensure_ascii,
        )


class MarkdownRenderer(BaseRenderer):
    """Renderer for Markdown output.

    Formats processing results as Markdown with proper headers, lists,
    and code blocks for documentation or sharing purposes.
    """

    def render(self, data: Any) -> str:
        """Render data as Markdown formatted string.

        Args:
            data: ProcessingResult, list of results, or dict-like object

        Returns:
            Markdown formatted string
        """
        if hasattr(data, "model_dump"):  # Pydantic model
            return self._render_processing_result(data)
        if isinstance(data, list):
            return self._render_result_list(data)
        if isinstance(data, dict):
            return self._render_dict(data)
        return f"# Results\n\n```\n{data!s}\n```\n"

    def _render_processing_result(self, result: Any) -> str:
        """Render a ProcessingResult as Markdown by composing sections.

        This method extracts smaller helpers to reduce cyclomatic complexity
        and improve readability.
        """
        data = result.model_dump() if hasattr(result, "model_dump") else result
        sections = [
            self._md_title_section(data),
            self._md_summary_section(data),
            self._md_error_section(data),
            self._md_file_info_section(data),
            self._md_metadata_section(data),
            self._md_footer_section(),
        ]
        return "\n".join(s for s in sections if s)

    def _md_title_section(self, data: dict) -> str:
        file_path = data.get("file", {}).get("path", "Unknown File")
        return f"# Document Summary: {file_path}\n"

    def _md_summary_section(self, data: dict) -> str | None:
        if not data.get("summary"):
            return None
        return "## Summary\n\n" + data["summary"] + "\n"

    def _md_error_section(self, data: dict) -> str | None:
        if not data.get("error"):
            return None
        error_info = data["error"]
        parts = [
            "## ⚠️ Error\n",
            f"**Code:** `{error_info.get('code', 'Unknown')}`\n",
            f"**Message:** {error_info.get('message', 'No message')}\n",
        ]
        if error_info.get("details"):
            details_json = json.dumps(error_info["details"], indent=2)
            parts.append("\n**Details:**\n")
            parts.append(f"```json\n{details_json}\n```\n")
        return "".join(parts)

    def _md_file_info_section(self, data: dict) -> str | None:
        file_info = data.get("file", {})
        if not file_info:
            return None
        lines = ["## File Information\n"]
        lines.append(
            f"- **Path:** `{file_info.get('path', 'Unknown')}`\n",
        )
        if file_info.get("size_bytes"):
            size_mb = file_info["size_bytes"] / (1024 * 1024)
            lines.append(f"- **Size:** {size_mb:.2f} MB\n")
        if file_info.get("mime_type"):
            lines.append(f"- **Type:** `{file_info['mime_type']}`\n")
        return "".join(lines) + "\n"

    def _md_metadata_section(self, data: dict) -> str | None:
        if not data.get("metadata"):
            return None
        parts = ["## Processing Metadata\n\n"]
        metadata = data["metadata"]
        for key, value in metadata.items():
            if value is not None:
                key_formatted = key.replace("_", " ").title()
                if isinstance(value, datetime):
                    value_formatted = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    value_formatted = str(value)
                parts.append(f"- **{key_formatted}:** {value_formatted}\n")
        parts.append("\n")
        return "".join(parts)

    def _md_footer_section(self) -> str:
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        return f"---\n*Generated by hlpr CLI on {timestamp}*"

    def _render_result_list(self, results: list) -> str:
        """Render a list of processing results as Markdown."""
        output = []
        output.append(f"# Processing Results ({len(results)} files)")
        output.append("")

        for i, result in enumerate(results, 1):
            output.append(f"## Result {i}")
            output.append("")
            result_md = self._render_processing_result(result)
            # Remove the main title from individual results
            result_lines = result_md.split("\n")[2:]
            output.extend(result_lines)
            output.append("")

        return "\n".join(output)

    def _render_dict(self, data: dict) -> str:
        """Render a generic dictionary as Markdown."""
        output = []
        output.append("# Results")
        output.append("")

        for key, value in data.items():
            output.append(f"## {key.replace('_', ' ').title()}")
            output.append("")
            if isinstance(value, (dict, list)):
                output.append(f"```json\n{json.dumps(value, indent=2)}\n```")
            else:
                output.append(str(value))
            output.append("")

        return "\n".join(output)


class PlainTextRenderer(BaseRenderer):
    """Renderer for plain text output.

    Provides simple, unformatted text output suitable for basic terminals,
    logging, or when rich formatting is not desired.
    """

    def render(self, data: Any) -> str:
        """Render data as plain text string.

        Args:
            data: ProcessingResult, list of results, or any object

        Returns:
            Plain text formatted string
        """
        if hasattr(data, "model_dump"):  # Pydantic model
            return self._render_processing_result(data)
        if isinstance(data, list):
            return self._render_result_list(data)
        if isinstance(data, dict):
            return self._render_dict(data)
        return f"Results:\n{data!s}"

    def _render_processing_result(self, result: Any) -> str:
        """Render a ProcessingResult as plain text by composing smaller blocks."""
        data = result.model_dump() if hasattr(result, "model_dump") else result
        parts = [
            self._txt_header(data),
            self._txt_summary(data),
            self._txt_error(data),
            self._txt_file_info(data),
            self._txt_metadata(data),
            self._txt_footer(),
        ]
        return "\n".join(p for p in parts if p)

    def _txt_header(self, data: dict) -> str:
        file_path = data.get("file", {}).get("path", "Unknown File")
        header = f"Document Summary: {file_path}"
        return header + "\n" + ("=" * len(header)) + "\n"

    def _txt_summary(self, data: dict) -> str | None:
        if not data.get("summary"):
            return None
        return "SUMMARY:\n" + data["summary"] + "\n"

    def _txt_error(self, data: dict) -> str | None:
        if not data.get("error"):
            return None
        error_info = data["error"]
        lines = ["ERROR:"]
        lines.append(f"  Code: {error_info.get('code', 'Unknown')}")
        lines.append(f"  Message: {error_info.get('message', 'No message')}")
        if error_info.get("details"):
            lines.append(f"  Details: {error_info['details']}")
        return "\n".join(lines) + "\n"

    def _txt_file_info(self, data: dict) -> str | None:
        file_info = data.get("file", {})
        if not file_info:
            return None
        lines = ["FILE INFO:", f"  Path: {file_info.get('path', 'Unknown')}"]
        if file_info.get("size_bytes"):
            size_mb = file_info["size_bytes"] / (1024 * 1024)
            lines.append(f"  Size: {size_mb:.2f} MB")
        if file_info.get("mime_type"):
            lines.append(f"  Type: {file_info['mime_type']}")
        return "\n".join(lines) + "\n"

    def _txt_metadata(self, data: dict) -> str | None:
        if not data.get("metadata"):
            return None
        metadata = data["metadata"]
        lines = ["METADATA:"]
        for key, value in metadata.items():
            if value is not None:
                key_formatted = key.replace("_", " ").title()
                if isinstance(value, datetime):
                    value_formatted = value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    value_formatted = str(value)
                lines.append(f"  {key_formatted}: {value_formatted}")
        return "\n".join(lines) + "\n"

    def _txt_footer(self) -> str:
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        return f"Generated: {timestamp}"

    def _render_result_list(self, results: list) -> str:
        """Render a list of processing results as plain text."""
        output = []
        output.append(f"Processing Results ({len(results)} files)")
        output.append("=" * len(output[-1]))
        output.append("")

        for i, result in enumerate(results, 1):
            output.append(f"--- Result {i} ---")
            result_text = self._render_processing_result(result)
            # Remove the header from individual results to avoid duplication
            result_lines = result_text.split("\n")[3:]
            output.extend(result_lines)
            output.append("")

        return "\n".join(output)

    def _render_dict(self, data: dict) -> str:
        """Render a generic dictionary as plain text."""
        output = []
        output.append("Results")
        output.append("=" * len(output[-1]))
        output.append("")

        for key, value in data.items():
            output.append(f"{key.replace('_', ' ').title()}:")
            if isinstance(value, (dict, list)):
                output.append(f"  {json.dumps(value, indent=2)}")
            else:
                output.append(f"  {value}")
            output.append("")

        return "\n".join(output)
