from __future__ import annotations

from app.work_review_contracts import (
    ActorRef,
    ActorType,
    ArtifactDraft,
    AttentionCategory,
    AttentionItemDraft,
    ReviewDraft,
    ReviewVerdict,
    WorkItemDraft,
    WorkStatus,
    can_transition,
    require_transition,
)


def main() -> None:
    owner = ActorRef(ActorType.OWNER, "owner-test")
    analyst = ActorRef(ActorType.INTERNAL_AGENT, "analyst-test")
    external = ActorRef(ActorType.EXTERNAL_MCP_AGENT, "sol-test")

    WorkItemDraft(
        work_type="RECONCILIATION_REVIEW",
        title="Test review work item",
        objective="Verify D4.8 substrate contracts",
        created_by=owner,
        source_channel="WEB",
    )
    ArtifactDraft(
        work_item_id="wi-test",
        artifact_type="ANALYST_REPORT",
        version=1,
        created_by=analyst,
        payload={"proposal": "no mutation"},
    )
    ReviewDraft(
        work_item_id="wi-test",
        artifact_id="artifact-test",
        artifact_version=1,
        reviewer=external,
        verdict=ReviewVerdict.COMMENT,
    )
    AttentionItemDraft(
        work_item_id="wi-test",
        category=AttentionCategory.WAITING_EXTERNAL,
        target=external,
        summary="External review requested",
    )

    assert can_transition(WorkStatus.DRAFT, WorkStatus.REVIEWING)
    assert can_transition(WorkStatus.REVIEWING, WorkStatus.WAITING_OWNER)
    assert can_transition(WorkStatus.REVIEWING, WorkStatus.WAITING_EXTERNAL)
    assert can_transition(WorkStatus.WAITING_EXTERNAL, WorkStatus.WAITING_OWNER)
    assert can_transition(WorkStatus.WAITING_OWNER, WorkStatus.APPROVED)
    assert can_transition(WorkStatus.APPROVED, WorkStatus.COMMITTABLE)
    assert can_transition(WorkStatus.COMMITTABLE, WorkStatus.COMMITTED)
    assert not can_transition(WorkStatus.APPROVED, WorkStatus.COMMITTED)
    assert not can_transition(WorkStatus.COMMITTED, WorkStatus.REVIEWING)

    try:
        require_transition(WorkStatus.APPROVED, WorkStatus.COMMITTED)
    except ValueError:
        pass
    else:
        raise AssertionError("APPROVED must not transition directly to COMMITTED")

    try:
        ArtifactDraft(
            work_item_id="wi-test",
            artifact_type="BAD",
            version=0,
            created_by=analyst,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Artifact version zero must be rejected")

    print("D4.8 work/review contracts verified")


if __name__ == "__main__":
    main()
