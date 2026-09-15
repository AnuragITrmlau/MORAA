"""
Celery task: sync_payment_to_erpnext — isolated accounting sync job.

Zero-disruption guarantees:
- This module is NEVER imported by ``app.celery_app`` (which auto-registers
  only ``analysis_tasks`` and ``prompt_tasks``), so the production worker's
  task registry and startup behaviour are completely unchanged. The task is
  registered only when this module is explicitly imported (tests, future
  integration points, or a dedicated worker).
- Every failure path is caught and logged via ``app.utils.logger``; the task
  never raises an unhandled exception that could crash the worker or an
  eager-mode caller.
- Retries are bounded (max 2, 60s delay) and attempted via ``self.retry``;
  once retries are exhausted the task returns a structured failure payload.

Note on imports: the Celery application instance lives at
``app/celery_app.py`` (mirroring ``app.tasks.analysis_tasks``), NOT at
``app/tasks/celery_app.py`` — importing the latter would raise
``ModuleNotFoundError`` and break the worker at import time.
"""

import asyncio
import concurrent.futures
from typing import Any, Dict, Optional

from celery.exceptions import MaxRetriesExceededError, Retry
from celery.result import EagerResult  # noqa: F401 — re-exported for typing convenience

from app.celery_app import celery_app
from app.services.erpnext_service import get_erpnext_service
from app.utils.logger import logger

_LOG_CATEGORY = "accounting"


def _run_async(coro: Any) -> Any:
    """Run an async coroutine from sync Celery context, eager-mode safe.

    Mirrors the event-loop handling used by ``app.tasks.analysis_tasks``:
    if a loop is already running (CELERY_TASK_ALWAYS_EAGER=true inside a
    FastAPI process), the coroutine is executed on a dedicated thread pool
    with a fresh event loop; otherwise ``asyncio.run`` is used directly.
    """
    try:
        asyncio.get_running_loop()
        # Eager mode: already inside a running event loop.
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    except RuntimeError:
        # Worker process: no running event loop.
        return asyncio.run(coro)


@celery_app.task(
    name="sync_payment_to_erpnext",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
)
def sync_payment_to_erpnext(
    self,
    customer_name: str,
    phone: str,
    item_code: str,
    amount: float,
    transaction_id: str,
    email: Optional[str] = None,
) -> Dict[str, Any]:
    """Sync a successful payment into ERPNext (customer + sales invoice).

    Args:
        customer_name: Customer display name to look up / create in ERPNext.
        phone: Customer phone number.
        item_code: ERPNext Item code to bill.
        amount: Amount to invoice (single line item).
        transaction_id: External payment reference (e.g. Razorpay payment id).
        email: Optional customer email address.

    Returns:
        A plain dict describing the outcome. Possible shapes:
            {"status": "skipped", "reason": "noop_mode"|"invalid_input", ...}
            {"status": "synced", "customer_id": ..., "invoice": {...}}
            {"status": "failed", "reason": ..., ...}   (retries exhausted)

    Raises:
        Nothing escapes this task. Bounded retries raise only the
        Celery-internal ``Retry`` exception, which the worker handles
        natively; in eager mode even that is swallowed and returned as a
        failure payload so callers can never be broken.
    """
    logger.bind(category=_LOG_CATEGORY).info(
        f"sync_payment_to_erpnext started: transaction={transaction_id} "
        f"customer='{customer_name}' amount={amount} item={item_code} "
        f"(attempt {self.request.retries + 1}/{self.max_retries + 1})"
    )

    # ------------------------------------------------------------------
    # 1) Execute the async connector, capturing ANY exception.
    # ------------------------------------------------------------------
    sync_error: Optional[BaseException] = None
    customer_id: str = ""
    invoice_result: Dict[str, Any] = {}

    try:
        service = get_erpnext_service()

        # Step 1 — customer upsert (returns "" on no-op or failure).
        customer_id = _run_async(
            service.get_or_create_customer(
                name=customer_name, phone=phone, email=email
            )
        )
        if not customer_id:
            # Either no-op mode (credentials missing) or invalid input /
            # unrecoverable API failure. Retrying will not change the
            # outcome — report and stop.
            reason = (
                "noop_mode" if not service.is_configured else "customer_sync_failed"
            )
            logger.bind(category=_LOG_CATEGORY).warning(
                f"sync_payment_to_erpnext skipped: transaction={transaction_id} "
                f"reason={reason}"
            )
            return {
                "status": "skipped",
                "reason": reason,
                "transaction_id": transaction_id,
            }

        # Step 2 — sales invoice.
        invoice_result = _run_async(
            service.create_sales_invoice(
                customer_id=customer_id,
                item_code=item_code,
                amount=amount,
                transaction_id=transaction_id,
            )
        )
        if not invoice_result.get("success"):
            # Structured failure from the connector (validation / API error).
            # Retrying will not change a validation outcome, so treat it as
            # terminal and report — no exception raised.
            logger.bind(category=_LOG_CATEGORY).warning(
                f"sync_payment_to_erpnext invoice not created: "
                f"transaction={transaction_id} "
                f"reason={invoice_result.get('reason', 'unknown')}"
            )
            return {
                "status": "skipped",
                "reason": f"invoice_{invoice_result.get('reason', 'unknown')}",
                "transaction_id": transaction_id,
                "customer_id": customer_id,
            }

    except Exception as exc:  # noqa: BLE001 — boundary of the safety net.
        sync_error = exc
        logger.bind(category=_LOG_CATEGORY).error(
            f"sync_payment_to_erpnext error: transaction={transaction_id}: {exc}"
        )

    # ------------------------------------------------------------------
    # 2) Success path.
    # ------------------------------------------------------------------
    if sync_error is None and invoice_result.get("success"):
        logger.bind(category=_LOG_CATEGORY).info(
            f"sync_payment_to_erpnext completed: transaction={transaction_id} "
            f"customer={customer_id} "
            f"invoice={invoice_result.get('invoice_name', '')}"
        )
        return {
            "status": "synced",
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "invoice": invoice_result,
        }

    # ------------------------------------------------------------------
    # 3) Failure path — bounded retry, then a logged, non-raising exit.
    # ------------------------------------------------------------------
    if sync_error is not None:
        try:
            # Bounded retry: honours max_retries=2 / default_retry_delay=60.
            # Raises ``Retry`` when the task is re-queued (the worker handles
            # it natively), or ``MaxRetriesExceededError`` when exhausted.
            raise self.retry(exc=sync_error)
        except Retry:
            # Control-flow signal for the worker — must propagate so the
            # retry is actually scheduled.
            raise
        except MaxRetriesExceededError:
            logger.bind(category=_LOG_CATEGORY).error(
                f"sync_payment_to_erpnext permanently failed after "
                f"{self.max_retries} retries: transaction={transaction_id}"
            )
            return {
                "status": "failed",
                "reason": "max_retries_exceeded",
                "transaction_id": transaction_id,
                "detail": str(sync_error),
            }
        except Exception as eager_exc:  # noqa: BLE001
            # Eager mode (CELERY_TASK_ALWAYS_EAGER=true) re-raises the
            # original exception instead of ``Retry``. Swallow it so an
            # in-process caller (e.g. a request handler) is never broken.
            logger.bind(category=_LOG_CATEGORY).error(
                f"sync_payment_to_erpnext swallowed error (eager mode / "
                f"retry unavailable): transaction={transaction_id}: {eager_exc}"
            )
            return {
                "status": "failed",
                "reason": "retry_unavailable",
                "transaction_id": transaction_id,
                "detail": str(eager_exc),
            }

    # Defensive fallback — should be unreachable.
    logger.bind(category=_LOG_CATEGORY).error(
        f"sync_payment_to_erpnext reached an unexpected state: "
        f"transaction={transaction_id}"
    )
    return {
        "status": "failed",
        "reason": "unexpected_state",
        "transaction_id": transaction_id,
    }
