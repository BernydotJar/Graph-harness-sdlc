from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .bootstrap import run_preflight
from .model import ValidationError
from .policy import PolicyLayer
from .profiles import DeveloperProfile
from .skills import SkillRegistry
from .telemetry import AttributionContext
from .validation import sha256_file


@dataclass(frozen=True)
class DoctorFinding:
    level: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


@dataclass(frozen=True)
class DoctorReport:
    root: str
    findings: tuple[DoctorFinding, ...]

    @property
    def ok(self) -> bool:
        return not any(finding.level == "error" for finding in self.findings)

    def as_dict(self) -> dict[str, Any]:
        counts = {level: sum(1 for item in self.findings if item.level == level) for level in ("error", "warn", "info")}
        return {
            "schema_version": "graph-harness.doctor.v1",
            "root": self.root,
            "ok": self.ok,
            "counts": counts,
            "findings": [finding.as_dict() for finding in self.findings],
        }


def run_doctor(root: str | Path, *, expectations_path: str | Path | None = None) -> DoctorReport:
    candidate = Path(root).expanduser().resolve(strict=False)
    findings: list[DoctorFinding] = []
    preflight = run_preflight(candidate, expectations_path=expectations_path)
    for item in preflight.findings:
        level = item.level if item.level in {"error", "warn"} else "info"
        findings.append(DoctorFinding(level, f"preflight-{item.code}", item.message))

    control = candidate / ".graph-harness"
    if not control.is_dir():
        findings.append(DoctorFinding("warn", "control-dir-missing", ".graph-harness is not initialized; run bootstrap first"))
    else:
        _validate_optional(control / "policy.json", "policy", PolicyLayer.from_path, findings)
        _validate_optional(control / "developer.json", "developer-profile", DeveloperProfile.from_path, findings)
        _validate_optional(control / "attribution.json", "attribution", AttributionContext.from_path, findings)
        manifest = control / "provider-manifest.json"
        if manifest.exists():
            _check_provider_manifest(candidate, manifest, findings)
        else:
            findings.append(DoctorFinding("info", "provider-manifest-absent", "no provider projections have been applied"))

    registry = candidate / "skills" / "registry.json"
    if registry.exists():
        _validate_optional(registry, "skill-registry", SkillRegistry.from_path, findings)
    else:
        findings.append(DoctorFinding("warn", "skill-registry-missing", "skills/registry.json is missing"))

    if not findings:
        findings.append(DoctorFinding("info", "doctor-clean", "no drift or contract problems detected"))
    return DoctorReport(str(candidate), tuple(findings))


def _validate_optional(path: Path, code: str, loader, findings: list[DoctorFinding]) -> None:
    if not path.exists():
        findings.append(DoctorFinding("warn", f"{code}-missing", f"optional control file is missing: {path}"))
        return
    try:
        loader(path)
    except ValidationError as error:
        findings.append(DoctorFinding("error", f"{code}-invalid", str(error)))
    else:
        findings.append(DoctorFinding("info", f"{code}-ok", f"validated {path}"))


def _check_provider_manifest(root: Path, manifest_path: Path, findings: list[DoctorFinding]) -> None:
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        findings.append(DoctorFinding("error", "provider-manifest-invalid", f"cannot read provider manifest: {error}"))
        return
    if not isinstance(raw, dict) or raw.get("schema_version") != "graph-harness.provider-manifest.v1":
        findings.append(DoctorFinding("error", "provider-manifest-invalid", "unsupported provider manifest schema"))
        return
    projections = raw.get("projections")
    if not isinstance(projections, dict):
        findings.append(DoctorFinding("error", "provider-manifest-invalid", "provider manifest projections must be an object"))
        return
    for provider, entry in sorted(projections.items()):
        if not isinstance(entry, dict):
            findings.append(DoctorFinding("error", "provider-entry-invalid", f"provider {provider!r} manifest entry must be an object"))
            continue
        target_root_raw = entry.get("target_root")
        target_raw = entry.get("target")
        expected_hash = entry.get("rendered_sha256")
        if not all(isinstance(value, str) and value for value in (target_root_raw, target_raw, expected_hash)):
            findings.append(DoctorFinding("error", "provider-entry-invalid", f"provider {provider!r} target metadata is incomplete"))
            continue
        target_root = Path(target_root_raw).expanduser().resolve(strict=False)
        target = Path(target_raw)
        if not target.is_absolute():
            target = target_root / target
        if not target.is_file():
            findings.append(DoctorFinding("warn", "provider-target-missing", f"{provider}: generated target is missing: {target}"))
        else:
            actual_hash = sha256_file(target)
            if actual_hash != expected_hash:
                findings.append(DoctorFinding("warn", "provider-target-drift", f"{provider}: generated target differs from recorded projection"))
            else:
                findings.append(DoctorFinding("info", "provider-target-current", f"{provider}: generated target matches manifest"))
        sources = entry.get("sources", {})
        if not isinstance(sources, dict):
            findings.append(DoctorFinding("error", "provider-sources-invalid", f"{provider}: sources must be an object"))
            continue
        for label, source_entry in sorted(sources.items()):
            if not isinstance(source_entry, dict):
                findings.append(DoctorFinding("error", "provider-source-invalid", f"{provider}:{label}: source entry must be an object"))
                continue
            path_raw = source_entry.get("path")
            recorded_hash = source_entry.get("sha256")
            if not isinstance(path_raw, str) or not path_raw:
                findings.append(DoctorFinding("error", "provider-source-invalid", f"{provider}:{label}: source path is missing"))
                continue
            source = Path(path_raw).expanduser()
            if not source.is_absolute():
                source = root / source
            if not source.is_file():
                findings.append(DoctorFinding("warn", "provider-source-missing", f"{provider}:{label}: source is missing: {source}"))
                continue
            actual = sha256_file(source)
            if not isinstance(recorded_hash, str) or actual != recorded_hash:
                findings.append(DoctorFinding("warn", "provider-source-drift", f"{provider}:{label}: source changed since projection"))
            else:
                findings.append(DoctorFinding("info", "provider-source-current", f"{provider}:{label}: source matches manifest"))
