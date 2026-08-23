from __future__ import annotations

import hashlib
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import text

from app.ai_workspace_access import require_ai_chat_access
from app.dashboard_auth import _engine

router = APIRouter(prefix="/dashboard/api/ai-workspace", tags=["ai-workspace-attachments"])

MAX_ATTACHMENT_BYTES = 8 * 1024 * 1024
MAX_PENDING_ATTACHMENTS = 4
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"


def _owned_conversation(connection: Any, conversation_id: str, principal: dict[str, str]) -> None:
    found = connection.execute(
        text(
            """
            SELECT 1
            FROM ai_workspace_conversations
            WHERE conversation_id=CAST(:conversation_id AS uuid)
              AND owner_user_id=CAST(:owner_user_id AS uuid)
              AND state='ACTIVE'
            """
        ),
        {"conversation_id": conversation_id, "owner_user_id": principal["user_id"]},
    ).scalar_one_or_none()
    if found is None:
        raise HTTPException(status_code=404, detail="Conversation not found")


def _metadata(row: Any) -> dict[str, Any]:
    return {
        "attachment_id": row["attachment_id"],
        "conversation_id": row["conversation_id"],
        "message_id": row["message_id"],
        "kind": row["kind"],
        "filename": row["original_filename"],
        "content_type": row["content_type"],
        "byte_size": row["byte_size"],
        "sha256": row["sha256"],
        "state": row["state"],
        "created_at": row["created_at"],
        "processing_status": "NOT_PROCESSED",
    }


@router.post("/conversations/{conversation_id}/attachments", status_code=status.HTTP_201_CREATED, summary="Upload one bounded AI Workspace attachment")
async def upload_attachment(
    conversation_id: str,
    response: Response,
    file: UploadFile = File(...),
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> dict[str, Any]:
    _no_store(response)
    content_type = (file.content_type or "").lower().strip()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported attachment type")
    filename = (file.filename or "attachment").strip()[:255] or "attachment"
    data = await file.read(MAX_ATTACHMENT_BYTES + 1)
    if len(data) > MAX_ATTACHMENT_BYTES:
        raise HTTPException(status_code=413, detail="Attachment exceeds 8 MB limit")
    if not data:
        raise HTTPException(status_code=422, detail="Attachment is empty")
    kind = "IMAGE" if content_type.startswith("image/") else "FILE"
    attachment_id = str(uuid.uuid4())
    digest = hashlib.sha256(data).hexdigest()

    engine = _engine()
    try:
        with engine.begin() as connection:
            _owned_conversation(connection, conversation_id, principal)
            pending_count = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM ai_workspace_attachments
                    WHERE conversation_id=CAST(:conversation_id AS uuid)
                      AND owner_user_id=CAST(:owner_user_id AS uuid)
                      AND state='PENDING'
                    """
                ),
                {"conversation_id": conversation_id, "owner_user_id": principal["user_id"]},
            ).scalar_one()
            if int(pending_count) >= MAX_PENDING_ATTACHMENTS:
                raise HTTPException(status_code=409, detail=f"Only {MAX_PENDING_ATTACHMENTS} pending attachments are allowed per conversation")
            row = connection.execute(
                text(
                    """
                    INSERT INTO ai_workspace_attachments (
                        attachment_id, conversation_id, owner_user_id, kind,
                        original_filename, content_type, byte_size, sha256, content_bytes
                    ) VALUES (
                        CAST(:attachment_id AS uuid), CAST(:conversation_id AS uuid), CAST(:owner_user_id AS uuid), :kind,
                        :filename, :content_type, :byte_size, :sha256, :content_bytes
                    )
                    RETURNING attachment_id::text AS attachment_id,
                              conversation_id::text AS conversation_id,
                              message_id::text AS message_id,
                              kind, original_filename, content_type, byte_size,
                              sha256, state, created_at
                    """
                ),
                {
                    "attachment_id": attachment_id,
                    "conversation_id": conversation_id,
                    "owner_user_id": principal["user_id"],
                    "kind": kind,
                    "filename": filename,
                    "content_type": content_type,
                    "byte_size": len(data),
                    "sha256": digest,
                    "content_bytes": data,
                },
            ).mappings().one()
            return _metadata(row)
    finally:
        engine.dispose()


@router.get("/conversations/{conversation_id}/attachments", summary="List metadata for owned AI Workspace attachments")
def list_attachments(
    conversation_id: str,
    response: Response,
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> dict[str, Any]:
    _no_store(response)
    engine = _engine()
    try:
        with engine.connect() as connection:
            _owned_conversation(connection, conversation_id, principal)
            rows = connection.execute(
                text(
                    """
                    SELECT attachment_id::text AS attachment_id,
                           conversation_id::text AS conversation_id,
                           message_id::text AS message_id,
                           kind, original_filename, content_type, byte_size,
                           sha256, state, created_at
                    FROM ai_workspace_attachments
                    WHERE conversation_id=CAST(:conversation_id AS uuid)
                      AND owner_user_id=CAST(:owner_user_id AS uuid)
                    ORDER BY created_at, attachment_id
                    """
                ),
                {"conversation_id": conversation_id, "owner_user_id": principal["user_id"]},
            ).mappings().all()
            return {"items": [_metadata(row) for row in rows], "count": len(rows)}
    finally:
        engine.dispose()


@router.delete("/conversations/{conversation_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove one pending owned AI Workspace attachment")
def delete_pending_attachment(
    conversation_id: str,
    attachment_id: str,
    principal: dict[str, str] = Depends(require_ai_chat_access),
) -> Response:
    engine = _engine()
    try:
        with engine.begin() as connection:
            _owned_conversation(connection, conversation_id, principal)
            row = connection.execute(
                text(
                    """
                    SELECT state, message_id
                    FROM ai_workspace_attachments
                    WHERE attachment_id=CAST(:attachment_id AS uuid)
                      AND conversation_id=CAST(:conversation_id AS uuid)
                      AND owner_user_id=CAST(:owner_user_id AS uuid)
                    """
                ),
                {
                    "attachment_id": attachment_id,
                    "conversation_id": conversation_id,
                    "owner_user_id": principal["user_id"],
                },
            ).mappings().first()
            if row is None:
                raise HTTPException(status_code=404, detail="Attachment not found")
            if row["state"] != "PENDING" or row["message_id"] is not None:
                raise HTTPException(status_code=409, detail="Only pending attachments can be removed independently")
            connection.execute(
                text("DELETE FROM ai_workspace_attachments WHERE attachment_id=CAST(:attachment_id AS uuid)"),
                {"attachment_id": attachment_id},
            )
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers={"Cache-Control": "no-store", "Pragma": "no-cache"})
    finally:
        engine.dispose()
