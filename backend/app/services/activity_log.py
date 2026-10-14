from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import ActivityEvent


class ActivityLogService:
    @staticmethod
    def record_event(
        db: Session,
        examination_id: str,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> ActivityEvent:
        """
        Appends an evidentiary event to the examination's local audit trail.
        Note: This is a standard relational database audit log for preliminary prototype screening.
        It does not claim blockchain or external immutable certification.
        """
        event = ActivityEvent(
            examination_id=examination_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            details=details or {},
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
