from __future__ import annotations

import contextlib
import os
import shutil
import tempfile
from pathlib import Path

import yaml

from .models import (
    APICredentials,
    ConfigurationPaths,
    ConfigurationState,
    UserConfiguration,
    ValidationResult,
)


class ConfigurationManager:
    def __init__(self, paths: ConfigurationPaths | None = None):
        self.paths = paths or ConfigurationPaths.default()
        self.paths.config_dir.mkdir(parents=True, exist_ok=True)
        self.paths.backup_dir.mkdir(parents=True, exist_ok=True)

    def load_configuration(self) -> ConfigurationState:
        # If config yaml doesn't exist, return defaults
        if not self.paths.config_file.exists():
            return ConfigurationState()

        # Load YAML (with graceful fallback on parse errors)
        try:
            with open(self.paths.config_file, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            # Move the corrupted file to backups with a timestamp and return
            # defaults if the YAML is unreadable.
            try:
                import time

                ts = time.strftime("%Y%m%d-%H%M%S")
                bak_name = f"config.yaml.corrupted.{ts}"
                bak_path = self.paths.backup_dir / bak_name
                self.paths.backup_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.paths.config_file, bak_path)
            except OSError:
                # Best-effort: ignore backup failures
                pass
            return ConfigurationState()

        # Load env credentials using robust parser
        creds = self._parse_env_file()

        # Build ConfigurationState
        config = UserConfiguration(**data)
        return ConfigurationState(config=config, credentials=creds)

    def _parse_env_file(self) -> APICredentials:
        """Parse the .env file into an APICredentials object.

        Handles quoted values, extra spaces, and ignores malformed lines.
        """
        creds = APICredentials()
        if not self.paths.env_file.exists():
            return creds

        key_mapping = {
            "OPENAI_API_KEY": "openai_api_key",
            "GOOGLE_API_KEY": "google_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "OPENROUTER_API_KEY": "openrouter_api_key",
            "GROQ_API_KEY": "groq_api_key",
            "DEEPSEEK_API_KEY": "deepseek_api_key",
            "GLM_API_KEY": "glm_api_key",
            "COHERE_API_KEY": "cohere_api_key",
            "MISTRAL_API_KEY": "mistral_api_key",
        }

        try:
            with open(self.paths.env_file, encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip().upper()
                    # Remove surrounding quotes if present and strip spaces
                    val = value.strip()
                    if (val.startswith('"') and val.endswith('"')) or (
                        val.startswith("'") and val.endswith("'")
                    ):
                        val = val[1:-1]
                    val = val.strip()
                    if key in key_mapping:
                        setattr(creds, key_mapping[key], val or None)
        except (OSError, UnicodeDecodeError):
            # Best-effort: return whatever we parsed so far
            pass

        return creds

    def is_first_run(self) -> bool:
        """Return True if no configuration has been created yet."""
        return not (self.paths.config_file.exists() or self.paths.env_file.exists())

    def backup_config(self) -> Path | None:
        """Create a timestamped backup of the current config file(s).

        Returns the backup dir path or None when there was nothing to back up.
        """
        if not self.paths.config_file.exists() and not self.paths.env_file.exists():
            return None
        import time

        ts = time.strftime("%Y%m%d-%H%M%S")
        backup_subdir = self.paths.backup_dir / ts
        backup_subdir.mkdir(parents=True, exist_ok=True)
        try:
            if self.paths.config_file.exists():
                shutil.copy2(self.paths.config_file, backup_subdir / "config.yaml")
            if self.paths.env_file.exists():
                shutil.copy2(self.paths.env_file, backup_subdir / ".env")
                with contextlib.suppress(OSError):
                    os.chmod(backup_subdir / ".env", 0o600)
            return backup_subdir
        except OSError:
            return None

    def restore_backup(self, backup_subdir: Path) -> bool:
        """Restore files from a backup directory. Returns True on success."""
        try:
            cfg = backup_subdir / "config.yaml"
            env = backup_subdir / ".env"
            if cfg.exists():
                shutil.copy2(cfg, self.paths.config_file)
            if env.exists():
                shutil.copy2(env, self.paths.env_file)
            return True
        except OSError:
            return False

    def validate_configuration(
        self,
        state: ConfigurationState | None = None,
    ) -> ValidationResult:
        """Validate configuration state and return ValidationResult."""
        if state is None:
            try:
                state = self.load_configuration()
            except (OSError, yaml.YAMLError) as exc:
                return ValidationResult(is_valid=False, errors=[str(exc)])

        errors: list[str] = []
        # Check provider
        try:
            _ = state.config.default_provider
        except (AttributeError, ValueError) as exc:  # pragma: no cover - defensive
            errors.append(f"Invalid provider: {exc}")

        # Temperature and max tokens are validated by Pydantic on assignment
        if errors:
            return ValidationResult(is_valid=False, errors=errors)
        return ValidationResult(is_valid=True)

    def _atomic_write(self, path: Path, data: str) -> None:
        dirpath = path.parent
        fd, tmp_path = tempfile.mkstemp(dir=dirpath)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(data)
            # Preserve mode if exists
            if path.exists():
                shutil.copymode(path, tmp_path)
            os.replace(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                with contextlib.suppress(OSError):
                    os.remove(tmp_path)

    def _generate_yaml_text(self, safe_obj: dict) -> str:
        """Return YAML text for saving configuration, prefer template on first run."""
        try:
            from hlpr.config import defaults as _defaults
            from hlpr.config import templates

            if not self.paths.config_file.exists():
                # Build a minimal defaults mapping for the template
                dp = safe_obj.get("default_provider", _defaults.DEFAULT_PROVIDER)
                df = safe_obj.get("default_format", _defaults.DEFAULT_FORMAT)
                dt = safe_obj.get("default_temperature", _defaults.DEFAULT_TEMPERATURE)
                dm = safe_obj.get("default_max_tokens", _defaults.DEFAULT_MAX_TOKENS)
                defaults_map = {
                    "default_provider": dp,
                    "default_format": df,
                    "default_temperature": dt,
                    "default_max_tokens": dm,
                }
                return templates.default_config_yaml(defaults_map)
            return yaml.safe_dump(safe_obj, sort_keys=False)
        except ImportError:
            return yaml.safe_dump(safe_obj, sort_keys=False)

    def _generate_env_text(self, creds: APICredentials) -> str:
        """Return .env contents for provided credentials.

        If no credentials present and file missing, prefer the default template.
        """

        def _build_env_content(credentials: APICredentials) -> str:
            lines: list[str] = []
            lines.append(f"OPENAI_API_KEY={credentials.openai_api_key or ''}\n")
            lines.append(f"GOOGLE_API_KEY={credentials.google_api_key or ''}\n")
            lines.append(f"ANTHROPIC_API_KEY={credentials.anthropic_api_key or ''}\n")
            lines.append(f"OPENROUTER_API_KEY={credentials.openrouter_api_key or ''}\n")
            lines.append(f"GROQ_API_KEY={credentials.groq_api_key or ''}\n")
            lines.append(f"DEEPSEEK_API_KEY={credentials.deepseek_api_key or ''}\n")
            lines.append(f"GLM_API_KEY={credentials.glm_api_key or ''}\n")
            lines.append(f"COHERE_API_KEY={credentials.cohere_api_key or ''}\n")
            lines.append(f"MISTRAL_API_KEY={credentials.mistral_api_key or ''}\n")
            return "".join(lines)

        try:
            from hlpr.config import templates

            if not self.paths.env_file.exists() and all(
                getattr(creds, k) in (None, "")
                for k in (
                    "openai_api_key",
                    "google_api_key",
                    "anthropic_api_key",
                    "openrouter_api_key",
                    "groq_api_key",
                )
            ):
                return templates.default_env_template()
            return _build_env_content(creds)
        except ImportError:
            return _build_env_content(creds)

    def save_configuration(self, state: ConfigurationState) -> None:
        # Ensure directory
        self.paths.config_dir.mkdir(parents=True, exist_ok=True)

        # Save YAML config.
        # Convert Pydantic model to primitives. Use model_dump() for v2,
        # fall back to dict().
        if hasattr(state.config, "model_dump"):
            data_obj = state.config.model_dump()
        else:
            data_obj = state.config.dict()

        # Recursive convert enums, Paths, and other non-primitive types to primitives
        def _to_primitives(o):
            from enum import Enum

            if isinstance(o, Enum):
                return o.value
            if isinstance(o, Path):
                return str(o)
            if isinstance(o, dict):
                return {k: _to_primitives(v) for k, v in o.items()}
            if isinstance(o, list):
                return [_to_primitives(i) for i in o]
            return o

        safe_obj = _to_primitives(data_obj)

        yaml_text = self._generate_yaml_text(safe_obj)
        self._atomic_write(self.paths.config_file, yaml_text)

        # Save .env file with API keys
        creds = state.credentials
        env_text = self._generate_env_text(creds)
        self._atomic_write(self.paths.env_file, env_text)

        # Ensure .env permissions are restrictive
        with contextlib.suppress(OSError):
            os.chmod(self.paths.env_file, 0o600)
