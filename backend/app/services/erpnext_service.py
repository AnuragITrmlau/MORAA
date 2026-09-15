"""
ERPNext Accounting Connector — isolated, zero-disruption service module.

This module is 100% standalone: it reads its configuration exclusively from
environment variables (with safe defaults), never raises on network/API
errors, and degrades to a logged no-op ("mock") mode when credentials are
absent. It does NOT touch the Razorpay flow, image pipeline, database
models, or any other production path.

Configuration (all optional — missing values activate no-op mode):
    ERPNEXT_BASE_URL     e.g. "https://erp.example.com"
    ERPNEXT_API_KEY      ERPNext API key (token auth)
    ERPNEXT_API_SECRET   ERPNext API secret (token auth)
    ERPNEXT_COMPANY      Company name invoices are booked against
"""

import os
from typing import Any, Dict, Optional

import httpx

from app.utils.logger import logger

_LOG_CATEGORY = "accounting"

#: Environment variables required to leave no-op mode.
_REQUIRED_ENV_VARS = (
    "ERPNEXT_BASE_URL",
    "ERPNEXT_API_KEY",
    "ERPNEXT_API_SECRET",
    "ERPNEXT_COMPANY",
)

#: Strict timeout for every ERPNext HTTP call (seconds), applied to
#: connect / read / write / pool uniformly.
_DEFAULT_TIMEOUT_SECONDS = 8.0

# Process-level flag so the "credentials missing" warning is logged once
# instead of spamming the logs on every sync attempt.
_warned_missing_config = False


class ERPNextService:
    """Async ERPNext REST client that fails silent, never fatal.

    Every public method returns a plain value (``str`` / ``dict``) and
    swallows all network/API errors after logging them, so a broken or
    unconfigured ERPNext instance can never crash an upstream caller
    (e.g. the Celery worker or a request handler).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        company: Optional[str] = None,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """Initialise the connector.

        Args:
            base_url: Overrides ``ERPNEXT_BASE_URL`` (dependency-injection
                hook for tests). Defaults to the environment variable.
            api_key: Overrides ``ERPNEXT_API_KEY``.
            api_secret: Overrides ``ERPNEXT_API_SECRET``.
            company: Overrides ``ERPNEXT_COMPANY``.
            timeout_seconds: Strict HTTP timeout applied to all phases.

        Raises:
            Nothing — invalid configuration simply activates no-op mode.
        """
        self.base_url: str = str(
            base_url if base_url is not None else os.getenv("ERPNEXT_BASE_URL", "")
        ).rstrip("/")
        self.api_key: str = (
            api_key if api_key is not None else os.getenv("ERPNEXT_API_KEY", "")
        )
        self.api_secret: str = (
            api_secret
            if api_secret is not None
            else os.getenv("ERPNEXT_API_SECRET", "")
        )
        self.company: str = (
            company if company is not None else os.getenv("ERPNEXT_COMPANY", "")
        )
        # Strict 8-second timeout: uniform cap on connect, read, write, pool.
        self.timeout: httpx.Timeout = httpx.Timeout(timeout_seconds)

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    @property
    def is_configured(self) -> bool:
        """True when all four ERPNext settings are present and non-empty."""
        return bool(self.base_url and self.api_key and self.api_secret and self.company)

    def _log_missing_config_once(self) -> None:
        """Warn exactly once per process when ERPNext is unconfigured."""
        global _warned_missing_config
        if not _warned_missing_config:
            _warned_missing_config = True
            missing = [
                var
                for var, value in zip(
                    _REQUIRED_ENV_VARS,
                    (self.base_url, self.api_key, self.api_secret, self.company),
                )
                if not value
            ]
            logger.bind(category=_LOG_CATEGORY).warning(
                "ERPNext connector is NOT configured "
                f"(missing: {', '.join(missing)}). "
                "Running in no-op mode — accounting sync calls will be skipped.",
            )

    def _auth_headers(self) -> Dict[str, str]:
        """Build ERPNext token-auth headers."""
        return {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_or_create_customer(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None,
    ) -> str:
        """Find an ERPNext Customer by ``customer_name`` or create it.

        Args:
            name: Customer display name (used as the lookup key).
            phone: Contact phone number stored on the customer record.
            email: Optional contact email address.

        Returns:
            The ERPNext customer document ``name`` (ID string), or an empty
            string when the connector is in no-op mode or the request fails.
        """
        # Input validation — fail silent with a warning, never raise.
        if not isinstance(name, str) or not name.strip():
            logger.bind(category=_LOG_CATEGORY).warning(
                "get_or_create_customer called with an empty customer name — skipping."
            )
            return ""
        if not isinstance(phone, str) or not phone.strip():
            logger.bind(category=_LOG_CATEGORY).warning(
                f"get_or_create_customer called without a phone for '{name}' — skipping."
            )
            return ""

        if not self.is_configured:
            self._log_missing_config_once()
            return ""

        try:
            # 1) Lookup by customer_name (filters are JSON-encoded query params).
            params: Dict[str, str] = {
                "filters": json_dumps_filters([["customer_name", "=", name.strip()]]),
                "fields": json_dumps_filters(["name", "customer_name"]),
                "limit_page_length": "1",
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/resource/Customer",
                    headers=self._auth_headers(),
                    params=params,
                )
                response.raise_for_status()
                records: Any = (response.json() or {}).get("data") or []
                if records:
                    customer_id: str = str(records[0].get("name", ""))
                    logger.bind(category=_LOG_CATEGORY).info(
                        f"ERPNext customer found: '{name}' -> {customer_id}"
                    )
                    return customer_id

                # 2) Not found — create it.
                customer_doc: Dict[str, Any] = {
                    "doctype": "Customer",
                    "customer_name": name.strip(),
                    "customer_type": "Individual",
                    "mobile_no": phone.strip(),
                }
                if email and email.strip():
                    customer_doc["email_id"] = email.strip()
                create_response = await client.post(
                    f"{self.base_url}/api/resource/Customer",
                    headers=self._auth_headers(),
                    json=customer_doc,
                )
                create_response.raise_for_status()
                created: str = str(
                    ((create_response.json() or {}).get("data") or {}).get("name", "")
                )
                logger.bind(category=_LOG_CATEGORY).info(
                    f"ERPNext customer created: '{name}' -> {created}"
                )
                return created
        except httpx.HTTPError as exc:
            # Covers timeouts, connection errors, and HTTP status errors.
            # A "duplicate customer" race is resolved by one final lookup.
            logger.bind(category=_LOG_CATEGORY).warning(
                f"ERPNext customer upsert issue for '{name}': {exc} — retrying lookup."
            )
            return await self._lookup_customer(name)
        except Exception as exc:  # noqa: BLE001 — never propagate to callers.
            logger.bind(category=_LOG_CATEGORY).error(
                f"Unexpected ERPNext error in get_or_create_customer('{name}'): {exc}"
            )
            return ""

    async def create_sales_invoice(
        self,
        customer_id: str,
        item_code: str,
        amount: float,
        transaction_id: str,
    ) -> Dict[str, Any]:
        """Create a single-line Sales Invoice in ERPNext.

        Args:
            customer_id: ERPNext customer document ``name`` (as returned by
                :meth:`get_or_create_customer`).
            item_code: ERPNext Item code billed on the invoice.
            amount: Invoice line rate (must be a finite, positive number).
            transaction_id: External payment reference recorded in remarks
                for reconciliation.

        Returns:
            ``{"success": True, "invoice_name": ..., ...}`` on success, or
            ``{"success": False, ...}`` on no-op/validation/error — never raises.
        """
        # Input validation — fail silent with a warning, never raise.
        if not isinstance(customer_id, str) or not customer_id.strip():
            logger.bind(category=_LOG_CATEGORY).warning(
                "create_sales_invoice called with an empty customer id — skipping."
            )
            return self._failure_result("empty_customer_id", transaction_id)
        if not isinstance(item_code, str) or not item_code.strip():
            logger.bind(category=_LOG_CATEGORY).warning(
                "create_sales_invoice called with an empty item code — skipping."
            )
            return self._failure_result("empty_item_code", transaction_id)
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or not amount > 0:
            logger.bind(category=_LOG_CATEGORY).warning(
                f"create_sales_invoice called with invalid amount {amount!r} — skipping."
            )
            return self._failure_result("invalid_amount", transaction_id)
        if not isinstance(transaction_id, str) or not transaction_id.strip():
            logger.bind(category=_LOG_CATEGORY).warning(
                "create_sales_invoice called with an empty transaction id — skipping."
            )
            return self._failure_result("empty_transaction_id", transaction_id)

        if not self.is_configured:
            self._log_missing_config_once()
            return self._failure_result("noop_mode", transaction_id)

        invoice_doc: Dict[str, Any] = {
            "doctype": "Sales Invoice",
            "company": self.company,
            "customer": customer_id.strip(),
            "items": [
                {
                    "item_code": item_code.strip(),
                    "qty": 1,
                    "rate": float(amount),
                    "amount": float(amount),
                }
            ],
            "remarks": f"Transaction {transaction_id.strip()}",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/resource/Sales Invoice",
                    headers=self._auth_headers(),
                    json=invoice_doc,
                )
                response.raise_for_status()
                data: Any = (response.json() or {}).get("data") or {}
                invoice_name: str = str(data.get("name", ""))
                logger.bind(category=_LOG_CATEGORY).info(
                    f"ERPNext sales invoice created: {invoice_name} "
                    f"(customer={customer_id}, amount={amount}, "
                    f"transaction={transaction_id})"
                )
                return {
                    "success": True,
                    "invoice_name": invoice_name,
                    "customer": customer_id.strip(),
                    "amount": float(amount),
                    "transaction_id": transaction_id.strip(),
                    "company": self.company,
                }
        except httpx.HTTPError as exc:
            logger.bind(category=_LOG_CATEGORY).error(
                f"ERPNext sales invoice failed "
                f"(customer={customer_id}, transaction={transaction_id}): {exc}"
            )
            return self._failure_result("http_error", transaction_id, detail=str(exc))
        except Exception as exc:  # noqa: BLE001 — never propagate to callers.
            logger.bind(category=_LOG_CATEGORY).error(
                f"Unexpected ERPNext error in create_sales_invoice "
                f"(transaction={transaction_id}): {exc}"
            )
            return self._failure_result("unexpected_error", transaction_id, detail=str(exc))

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _lookup_customer(self, name: str) -> str:
        """Single best-effort customer lookup used for duplicate-race recovery."""
        try:
            params: Dict[str, str] = {
                "filters": json_dumps_filters([["customer_name", "=", name.strip()]]),
                "fields": json_dumps_filters(["name"]),
                "limit_page_length": "1",
            }
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/resource/Customer",
                    headers=self._auth_headers(),
                    params=params,
                )
                response.raise_for_status()
                records: Any = (response.json() or {}).get("data") or []
                if records:
                    found: str = str(records[0].get("name", ""))
                    logger.bind(category=_LOG_CATEGORY).info(
                        f"ERPNext customer recovered after race: '{name}' -> {found}"
                    )
                    return found
        except Exception as exc:  # noqa: BLE001 — best effort only.
            logger.bind(category=_LOG_CATEGORY).error(
                f"ERPNext customer recovery lookup failed for '{name}': {exc}"
            )
        return ""

    @staticmethod
    def _failure_result(
        reason: str, transaction_id: str, detail: str = ""
    ) -> Dict[str, Any]:
        """Build a consistent, safe failure payload (never raises)."""
        result: Dict[str, Any] = {
            "success": False,
            "reason": reason,
            "transaction_id": transaction_id,
        }
        if detail:
            result["detail"] = detail
        return result


def json_dumps_filters(value: Any) -> str:
    """Serialise an ERPNext filters/fields value into a JSON query string."""
    import json

    return json.dumps(value, separators=(",", ":"))


def get_erpnext_service() -> ERPNextService:
    """Factory returning a connector instance bound to current env vars.

    Kept as a module-level helper so callers (and tests) can monkeypatch a
    single symbol without touching any other module.
    """
    return ERPNextService()
