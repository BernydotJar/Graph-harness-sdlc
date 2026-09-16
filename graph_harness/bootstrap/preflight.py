from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from ..model import ValidationError
from ..validation import load_json_object, reject_secret_like_keys, reject_secret_like_values


@dataclass(frozen=True)
class PreflightFinding:
    level: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


@dataclass(frozen=True)
class PreflightResult:
    ok: bool
    observed: Mapping[str, Any]
    findings: tuple[PreflightFinding, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "graph-harness.preflight-state.v1",
            "ok": self.ok,
            "observed": dict(self.observed),
            "findings": [finding.as_dict() for finding in self.findings],
        }


def run_preflight(
    root: str | Path,
    *,
    expectations_path: str | Path | None = None,
    require_commands: tuple[str, ...] = (),
) -> PreflightResult:
    work_root = Path(root).expanduser().resolve(strict=False)
    findings: list[PreflightFinding] = []
    if not work_root.is_dir():
        findings.append(PreflightFinding("error", "work-root-missing", f"work root does not exist: {work_root}"))
        return PreflightResult(False, {"work_root": str(work_root)}, tuple(findings))

    git_root = _git(work_root, "rev-parse", "--show-toplevel")
    branch = _git(work_root, "branch", "--show-current")
    origin = _git(work_root, "remote", "get-url", "origin")
    head = _git(work_root, "rev-parse", "HEAD")
    dirty_text = _git(work_root, "status", "--porcelain", allow_failure=True)
    frameworks = _detect_frameworks(work_root)
    observed: dict[str, Any] = {
        "work_root": str(work_root),
        "git_root": git_root or None,
        "branch": branch or None,
        "origin": origin or None,
        "head": head or None,
        "dirty": bool(dirty_text),
        "project_state": "git-repository" if git_root else ("empty" if not any(work_root.iterdir()) else "existing-directory"),
        "frameworks": frameworks,
        "python": {
            "version": ".".join(str(item) for item in sys.version_info[:3]),
            "executable": sys.executable,
        },
        "commands": {},
    }
    if not git_root:
        findings.append(PreflightFinding("warn", "git-root-missing", "work root is not inside a Git repository"))

    expectations: dict[str, Any] = {}
    if expectations_path is not None:
        expectations = _load_expectations(expectations_path)
        identity = expectations.get("identity", {})
        environment = expectations.get("environment", {})
        _evaluate_identity(identity, observed, findings)
        required = tuple(dict.fromkeys((*require_commands, *environment.get("require_commands", []))))
        expected_frameworks = environment.get("frameworks", [])
        missing_frameworks = sorted(set(expected_frameworks) - set(frameworks))
        if missing_frameworks:
            findings.append(
                PreflightFinding(
                    "error",
                    "framework-mismatch",
                    f"required framework markers not detected: {missing_frameworks}",
                )
            )
        python_requirement = environment.get("python")
        if python_requirement:
            if not _python_satisfies(str(python_requirement)):
                findings.append(
                    PreflightFinding(
                        "error",
                        "python-version-mismatch",
                        f"Python {observed['python']['version']} does not satisfy {python_requirement}",
                    )
                )
    else:
        required = tuple(dict.fromkeys(require_commands))

    for command in required:
        info = _command_info(command)
        observed["commands"][command] = info
        if not info["available"]:
            findings.append(PreflightFinding("error", "command-missing", f"required command is unavailable: {command}"))

    if not findings:
        findings.append(PreflightFinding("info", "preflight-clean", "identity and environment checks passed"))
    return PreflightResult(not any(item.level == "error" for item in findings), observed, tuple(findings))


def _load_expectations(path: str | Path) -> dict[str, Any]:
    raw = load_json_object(path, "preflight expectations")
    reject_secret_like_keys(raw, label="preflight expectations")
    reject_secret_like_values(raw, label="preflight expectations")
    unknown = sorted(set(raw) - {"schema_version", "identity", "environment"})
    if unknown:
        raise ValidationError(f"preflight expectations: unsupported fields {unknown}")
    if raw.get("schema_version") != "graph-harness.preflight.v1":
        raise ValidationError("preflight expectations schema_version must be graph-harness.preflight.v1")
    identity = raw.get("identity", {})
    environment = raw.get("environment", {})
    if not isinstance(identity, Mapping) or not isinstance(environment, Mapping):
        raise ValidationError("preflight identity and environment must be objects")
    unknown_identity = sorted(set(identity) - {"work_root", "git_root", "branch", "origin", "repository"})
    if unknown_identity:
        raise ValidationError(f"preflight identity: unsupported fields {unknown_identity}")
    unknown_environment = sorted(set(environment) - {"python", "require_commands", "frameworks"})
    if unknown_environment:
        raise ValidationError(f"preflight environment: unsupported fields {unknown_environment}")
    required = environment.get("require_commands", [])
    if not isinstance(required, list) or not all(isinstance(item, str) and item for item in required):
        raise ValidationError("preflight environment.require_commands must be an array of non-empty strings")
    frameworks = environment.get("frameworks", [])
    if not isinstance(frameworks, list) or not all(isinstance(item, str) and item for item in frameworks):
        raise ValidationError("preflight environment.frameworks must be an array of non-empty strings")
    return {"identity": dict(identity), "environment": dict(environment)}


def _evaluate_identity(identity: Mapping[str, Any], observed: Mapping[str, Any], findings: list[PreflightFinding]) -> None:
    for key in ("work_root", "git_root"):
        expected = identity.get(key)
        if expected is None:
            continue
        if not isinstance(expected, str) or not expected:
            raise ValidationError(f"preflight identity.{key} must be a non-empty string")
        actual = observed.get(key)
        expected_path = str(Path(expected).expanduser().resolve(strict=False))
        actual_path = str(Path(actual).resolve(strict=False)) if isinstance(actual, str) and actual else None
        if actual_path != expected_path:
            findings.append(
                PreflightFinding("error", f"identity-{key}-mismatch", f"expected {key} {expected_path!r}, observed {actual_path!r}")
            )
    for key in ("branch", "origin"):
        expected = identity.get(key)
        if expected is None:
            continue
        if not isinstance(expected, str) or not expected:
            raise ValidationError(f"preflight identity.{key} must be a non-empty string")
        actual = observed.get(key)
        if actual != expected:
            findings.append(
                PreflightFinding("error", f"identity-{key}-mismatch", f"expected {key} {expected!r}, observed {actual!r}")
            )
    repository = identity.get("repository")
    if repository is not None:
        if not isinstance(repository, str) or not repository.strip():
            raise ValidationError("preflight identity.repository must be a non-empty string")
        actual_repository = _repository_slug(str(observed.get("origin") or ""))
        if actual_repository.lower() != repository.strip().removesuffix(".git").lower():
            findings.append(
                PreflightFinding(
                    "error",
                    "identity-repository-mismatch",
                    f"expected repository {repository!r}, observed {actual_repository!r}",
                )
            )


def _repository_slug(origin: str) -> str:
    if not origin:
        return ""
    if origin.startswith("git@") and ":" in origin:
        path = origin.split(":", 1)[1]
    else:
        parsed = urlparse(origin)
        path = parsed.path if parsed.scheme else origin
    return path.strip("/").removesuffix(".git")


def _git(root: Path, *args: str, allow_failure: bool = False) -> str:
    if shutil.which("git") is None:
        return ""
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=5,
        check=False,
    )
    if completed.returncode != 0:
        if allow_failure:
            return ""
        return ""
    return completed.stdout.strip()


def _command_info(command: str) -> dict[str, Any]:
    executable = shutil.which(command)
    if executable is None:
        return {"available": False, "path": None, "version": None}
    version: str | None = None
    try:
        completed = subprocess.run(
            [executable, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=3,
            check=False,
        )
        output = (completed.stdout or completed.stderr).strip().splitlines()
        if output:
            version = output[0][:240]
    except (OSError, subprocess.SubprocessError):
        version = None
    return {"available": True, "path": executable, "version": version}



def _detect_frameworks(root: Path) -> list[str]:
    detected: set[str] = set()
    if any((root / name).is_file() for name in ("pyproject.toml", "requirements.txt", "setup.py", "setup.cfg")):
        detected.add("python")
    package_json = root / "package.json"
    if package_json.is_file():
        detected.add("node")
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            package = {}
        dependencies: dict[str, Any] = {}
        for field in ("dependencies", "devDependencies", "peerDependencies"):
            value = package.get(field, {}) if isinstance(package, dict) else {}
            if isinstance(value, dict):
                dependencies.update(value)
        if "next" in dependencies:
            detected.add("nextjs")
        if "react" in dependencies:
            detected.add("react")
    if any(root.glob("*.tf")) or (root / ".terraform").exists():
        detected.add("terraform")
    if (root / "Dockerfile").is_file() or any((root / name).is_file() for name in ("compose.yaml", "compose.yml", "docker-compose.yml", "docker-compose.yaml")):
        detected.add("docker")
    if (root / "gradlew").is_file() and any((root / name).is_file() for name in ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts")):
        detected.add("android-gradle")
    if (root / "Cargo.toml").is_file():
        detected.add("rust")
    if any(root.glob("*.sln")) or any(root.glob("*.csproj")):
        detected.add("dotnet")
    return sorted(detected)

def _python_satisfies(requirement: str) -> bool:
    match = re.fullmatch(r">=\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?", requirement.strip())
    if not match:
        raise ValidationError("preflight environment.python currently supports only >=MAJOR[.MINOR[.PATCH]]")
    required = tuple(int(part or 0) for part in match.groups())
    current = sys.version_info[:3]
    return tuple(current) >= required
