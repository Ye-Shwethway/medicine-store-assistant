from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ActorType(StrEnum):
    OWNER = "OWNER"
    USER = "USER"
    INTERNAL_AGENT = "INTERNAL_AGENT"
    EXTERNAL_MCP_AGENT = "EXTERNAL_MCP_AGENT"
    SYSTEM = "SYSTEM"


class WorkStatus(StrEnum):
    DRAFT = "DRAFT"
    REVIEWING = "REVIEWING"
    WAITING_EXTERNAL = "WAITING_EXTERNAL"
    WAITING_OWNER = "WAITING_OWNER"
    APPROVED = "APPROVED"
    COMMITTABLE = "COMMITTABLE"
    COMMITTED = "COMMITTED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReviewVerdict(StrEnum):
    APPROVE = "APPROVE"
    NEEDS_FIX = "NEEDS_FIX"
    REJECT = "REJECT"
    COMMENT = "COMMENT"


class AttentionCategory(StrEnum):
    WAITING_EXTERNAL = "WAITING_EXTERNAL"
    WAITING_OWNER = "WAITING_OWNER"
    WORKFLOW_FAILURE = "WORKFLOW_FAILURE"
    DISAGREEMENT = "DISAGREEMENT"
    COMPLETED = "COMPLETED"


class AttentionStatus(StrEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


REVIEW_TRANSITIONS: dict[WorkStatus, frozenset[WorkStatus]] = {
    WorkStatus.DRAFT: frozenset({WorkStatus.REVIEWING, WorkStatus.CANCELLED}),
    WorkStatus.REVIEWING: frozenset(
        {
            WorkStatus.REVIEWING,
            WorkStatus.WAITING_EXTERNAL,
            WorkStatus.WAITING_OWNER,
            WorkStatus.DRAFT,
            WorkStatus.FAILED,
            WorkStatus.CANCELLED,
        }
    ),
    WorkStatus.WAITING_EXTERNAL: frozenset(
        {WorkStatus.REVIEWING, WorkStatus.WAITING_OWNER, WorkStatus.FAILED, WorkStatus.CANCELLED}
    ),
    WorkStatus.WAITING_OWNER: frozenset(
        {WorkStatus.REVIEWING, WorkStatus.DRAFT, WorkStatus.APPROVED, WorkStatus.CANCELLED}
    ),
    WorkStatus.APPROVED: frozenset(
        {WorkStatus.REVIEWING, WorkStatus.COMMITTABLE, WorkStatus.CANCELLED}
    ),
    WorkStatus.COMMITTABLE: frozenset(
        {WorkStatus.COMMITTED, WorkStatus.REVIEWING, WorkStatus.FAILED, WorkStatus.CANCELLED}
    ),
    WorkStatus.COMMITTED: frozenset(),
    WorkStatus.FAILED: frozenset({WorkStatus.REVIEWING, WorkStatus.DRAFT, WorkStatus.CANCELLED}),
    WorkStatus.CANCELLED: frozenset(),
}


def can_transition(current: WorkStatus, target: WorkStatus) -> bool:
    return target in REVIEW_TRANSITIONS[current]


def require_transition(current: WorkStatus, target: WorkStatus) -> None:
    if not can_transition(current, target):
        raise ValueError(f"Invalid review lifecycle transition: {current.value} -> {target.value}")


@dataclass(frozen=True, slots=True)
class ActorRef:
    actor_type: ActorType
    actor_id: str | None = None


@dataclass(frozen=True, slots=True)
class WorkItemDraft:
    work_type: str
    title: str
    objective: str | None
    created_by: ActorRef
    source_channel: str
    session_id: str | None = None
    correlation_id: str | None = None


@dataclass(frozen=True, slots=True)
class ArtifactDraft:
    work_item_id: str
    artifact_type: str
    version: int
    created_by: ActorRef
    payload: dict[str, Any] = field(default_factory=dict)
    content_hash: str | None = None
    supersedes_artifact_id: str | None = None

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("Artifact version must be >= 1")


@dataclass(frozen=True, slots=True)
class ReviewDraft:
    work_item_id: str
    artifact_id: str
    artifact_version: int
    reviewer: ActorRef
    verdict: ReviewVerdict
    notes: str | None = None
    findings: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        if self.artifact_version < 1:
            raise ValueError("Reviewed artifact version must be >= 1")


@dataclass(frozen=True, slots=True)
class WorkflowEventDraft:
    work_item_id: str
    event_type: str
    actor: ActorRef
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None


@dataclass(frozen=True, slots=True)
class AttentionItemDraft:
    work_item_id: str
    category: AttentionCategory
    target: ActorRef
    summary: str
    source_event_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# Security invariant: these contracts describe workflow evidence/review state only.
# They intentionally expose no inventory mutation primitive. APPROVED is review state;
# real store mutation remains a separate typed operation gated before COMMITTABLE/COMMITTED.
