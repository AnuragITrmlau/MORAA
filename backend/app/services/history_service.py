"""History service for managing analysis history."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.history import HistoryEntry
from app.repositories.base import BaseRepository
from app.schemas.history import (
    HistoryItemResponse,
    HistoryListResponse,
    HistoryStatsResponse,
)
from app.utils.logger import logger


class HistoryService:
    """Analysis history management service."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = BaseRepository(HistoryEntry, db)

    def get_history(
        self,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> HistoryListResponse:
        """
        Get paginated history entries.
        Supports filtering by status and search.
        """
        query = self.db.query(HistoryEntry)

        if user_id:
            query = query.filter(HistoryEntry.user_id == user_id)

        if status and status != "all":
            query = query.filter(HistoryEntry.status == status)

        if search:
            query = query.filter(
                HistoryEntry.product_name.ilike(f"%{search}%")
            )

        # Order by most recent first
        query = query.order_by(HistoryEntry.created_at.desc())

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        items = query.offset(skip).limit(page_size).all()

        return HistoryListResponse(
            items=[self._to_response(item) for item in items],
            total=total,
        )

    def get_history_item(
        self, history_id: str, user_id: Optional[str] = None
    ) -> Optional[HistoryItemResponse]:
        """Get a single history entry."""
        item = self.repo.get(history_id)
        if not item:
            return None
        if user_id and item.user_id != user_id:
            return None
        return self._to_response(item)

    def delete_history_item(
        self, history_id: str, user_id: Optional[str] = None
    ) -> bool:
        """Delete a history entry."""
        item = self.repo.get(history_id)
        if not item:
            return False
        if user_id and item.user_id != user_id:
            return False

        self.repo.delete(history_id)

        logger.bind(category="history").info(
            f"History entry deleted: {history_id}"
        )
        return True

    def get_stats(
        self, user_id: Optional[str] = None
    ) -> HistoryStatsResponse:
        """Get history statistics."""
        query = self.db.query(HistoryEntry)

        if user_id:
            query = query.filter(HistoryEntry.user_id == user_id)

        total = query.count()

        # This month count
        now = datetime.now(timezone.utc)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month = query.filter(
            HistoryEntry.created_at >= first_of_month
        ).count()

        # Average price
        from sqlalchemy import func

        avg_price = query.with_entities(
            func.avg(HistoryEntry.estimated_price)
        ).scalar()

        return HistoryStatsResponse(
            total=total,
            thisMonth=this_month,
            averagePrice=round(avg_price or 0, 2),
        )

    def _to_response(self, entry: HistoryEntry) -> HistoryItemResponse:
        """Convert model to response schema."""
        return HistoryItemResponse(
            id=entry.id,
            productName=entry.product_name or "Unknown Item",
            imageUrl=entry.image_url or "",
            analysisDate=entry.created_at.strftime("%Y-%m-%d") if entry.created_at else "",
            status=entry.status,
            estimatedPrice=entry.estimated_price or 0.0,
        )
