from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from openg2p_bg_task_models.schemas import (
    BeneficiarySearchResponsePayload,
    Disbursement,
)
from openg2p_fastapi_common.schemas import G2PPaginationRequest
from openg2p_pbms_models.models import G2PRegistry
from openg2p_bg_task_models.models import BeneficiaryListDetails
from sqlalchemy import TextClause, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from ..schema import BeneficiaryListSummaryPayload


class RegistryInterface(ABC):
    """
    Base class for Registry Interface
    Defines methods for interacting with the registry classes
    """

    # Maps target_registry values (singular) to actual NSR table names (plural)
    TABLE_NAME_MAP = {
        "individual": "g2p_register_individuals",
        "household": "g2p_register_households",
        "farmer": "g2p_register_farmers",
        "student": "g2p_register_students",
        "group": "g2p_register_groups",
        "families": "g2p_register_families",
        "gramstackhousehold": "g2p_register_gramstack_households",
        "gramstack_household": "g2p_register_gramstack_households",
    }

    def _get_nsr_table_name(self, target_registry: str) -> str:
        """Resolve a target_registry value to the actual NSR table name."""
        return self.TABLE_NAME_MAP.get(
            target_registry, f"g2p_register_{target_registry}"
        )

    # ================
    # Summary methods
    # ================
    @abstractmethod
    async def get_summary(
        self, beneficiary_list_id: str, bg_task_session: AsyncSession, formated: bool = False
    ) -> BeneficiaryListSummaryPayload:
        """
        Abstract method to get async summary statistics for a given beneficiary_list_id.
        """
        raise NotImplementedError("Subclasses must implement get_summary()")

    @abstractmethod
    def get_summary_sync(
        self, beneficiary_list_id: str, bg_task_session: Session
    ) -> BeneficiaryListSummaryPayload:
        """
        Abstract method to get synchronous summary statistics for a given beneficiary_list_id.
        """
        raise NotImplementedError("Subclasses must implement get_summary_sync()")

    @abstractmethod
    def compute_eligibility_statistics(
        self,
        beneficiary_list_details: List[BeneficiaryListDetails],
        base_summary,
        sr_session: Session,
        bg_task_session: Session,
    ):
        """
        Abstract method to compute eligibility summary statistics and update the summary table.
        """
        raise NotImplementedError("Subclasses must implement compute_eligibility_statistics()")

    @abstractmethod
    def compute_entitlement_statistics(
        self, beneficiary_list_id: str, bg_task_session: Session, sr_session: Session
    ):
        """
        Abstract method to compute entitlement statistics and update relevant summary fields.
        """
        raise NotImplementedError(
            "Subclasses must implement compute_entitlement_statistics()"
        )

    # =================
    # Registry methods
    # =================
    @abstractmethod
    def get_registrants_by_ids(
        self, registrant_ids: List, sr_session: Session
    ) -> List[G2PRegistry]:
        """
        Abstract method to fetch registrants for given registrant_ids from the registry database.
        """
        raise NotImplementedError("Subclasses must implement get_registrants_by_ids()")

    @abstractmethod
    def get_is_registant_entitled(
        self, registrant_id: str, sql_query: str, sr_session: Session
    ) -> bool:
        """
        Abstract method to check if a registrant is entitled based on custom SQL and session.
        """
        raise NotImplementedError(
            "Subclasses must implement get_is_registant_entitled()"
        )

    @abstractmethod
    def get_entitlement_multiplier(
        self, multiplier: str, registrant_id: str, sr_session: Session
    ) -> int:
        """
        Abstract method to get the multiplier value for entitlement calculation
        for a single registrant_id by executing a SQL query.
        """
        raise NotImplementedError(
            "Subclasses must implement get_entitlement_multiplier()"
        )

    @abstractmethod
    async def search_beneficiaries(
        self,
        bg_task_session: AsyncSession,
        sr_session: AsyncSession,
        beneficiary_list_id: str,
        target_registry: str,
        search_query,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "internal_record_id asc",
    ) -> Tuple[BeneficiarySearchResponsePayload, int]:
        """
        Abstract method to search beneficiaries for particular eligibility request id.
        Returns a tuple of (response_payload, total_count) where total_count is the
        total number of matching beneficiaries (used for pagination response).
        """
        raise NotImplementedError("Subclasses must implement search_beneficiaries()")

    def get_bridge_disbursement_details(
        self,
        beneficiary_list_id: str,
        registrant_ids: List[str],
        bg_task_session: Session,
    ) -> List[Disbursement]:
        raise NotImplementedError("Subclasses must implement get_bridge_disbursement_details()")

    # ===============================
    # Registry SQL Query Constructors
    # ===============================
    def construct_multiplier_sql_query(
        self, multiplier: str, target_registry: str
    ) -> TextClause:
        if not multiplier or multiplier == "none":
            return None

        table_name = self._get_nsr_table_name(target_registry)
        sql_query = text(
            f"""
            SELECT {multiplier} FROM {table_name}
            WHERE internal_record_id = :registrant_id
            """
        )
        return sql_query

    def _normalize_where_clause(self, where_clause: str) -> str:
        if not where_clause:
            return ""
        # Replace curly quotes in the where clause
        where_clause = where_clause.replace("“", '"').replace("”", '"')
        where_clause = where_clause.replace("‘", "'").replace("’", "'")
        # Ensure gender comparisons are case-insensitive
        if "gender" in where_clause:
            import re
            where_clause = re.sub(
                r'("[^"]*"\."gender")\s*=\s*(\'[^\']*\')',
                r'LOWER(\1) = LOWER(\2)',
                where_clause,
                flags=re.IGNORECASE,
            )
        return where_clause

    def construct_beneficiary_search_sql_query(
        self,
        registrant_ids: List[str],
        target_registry: str,
        where_clause: str,
        order_by: str,
        page_size: int,
        page: int,
    ) -> Tuple[TextClause, Dict[str, Any]]:
        if not registrant_ids:
            return None, {}

        where_clause = self._normalize_where_clause(where_clause)
        table_name = self._get_nsr_table_name(target_registry)
        where_clause_sql = f" AND {where_clause}" if where_clause else ""
        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )

        sql_query = text(
            f"""
            SELECT * FROM {table_name}
            WHERE internal_record_id IN ({registrant_placeholders}) {where_clause_sql}
            ORDER BY {order_by}
            OFFSET :offset
            LIMIT :limit
        """
        )

        params = {
            f"registrant_id_{i}": registrant_ids[i] for i in range(len(registrant_ids))
        }
        params.update({"offset": page_size * (page - 1), "limit": page_size})

        return sql_query, params

    def construct_beneficiary_search_count_sql_query(
        self, registrant_ids: List[str], target_registry: str, where_clause: str
    ) -> Tuple[TextClause, Dict[str, Any]]:
        if not registrant_ids:
            return None, {}

        where_clause = self._normalize_where_clause(where_clause)
        table_name = self._get_nsr_table_name(target_registry)
        where_clause_sql = f" AND {where_clause}" if where_clause else ""
        registrant_placeholders = ", ".join(
            [f":registrant_id_{i}" for i in range(len(registrant_ids))]
        )

        sql_query = text(
            f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE internal_record_id IN ({registrant_placeholders}) {where_clause_sql}
        """
        )

        params = {
            f"registrant_id_{i}": registrant_ids[i] for i in range(len(registrant_ids))
        }

        return sql_query, params

    def construct_get_is_registrant_entitled_sql_query(
        self, registrant_id: str, target_registry: str, sql_query: str
    ) -> TextClause:
        sql_query = sql_query.strip()

        if not registrant_id:
            raise ValueError("registrant_id cannot be None or zero")
        if not sql_query.upper().startswith("SELECT"):
            raise ValueError("Invalid SQL query: Must be a valid SELECT statement")

        import re
        from_match = re.search(r'FROM\s+["\']?([a-zA-Z0-9_]+)["\']?', sql_query, re.IGNORECASE)
        if from_match:
            nsr_table = f'"{from_match.group(1)}"'
        else:
            nsr_table = self._get_nsr_table_name(target_registry)

        if "WHERE" in sql_query.upper():
            sql_query += (
                f" AND {nsr_table}.internal_record_id = :registrant_id"
            )
        else:
            sql_query += (
                f" WHERE {nsr_table}.internal_record_id = :registrant_id"
            )

        params = {"registrant_id": registrant_id}

        return text(sql_query).params(**params)

    async def update_reconciliation_status(
        self,
        sr_session: AsyncSession,
        target_registry: str,
        registrant_ids: List[str],
        scheme_code: str,
        new_status: str,
        tranche_number: Optional[int] = None,
        amount: Optional[float] = None,
        reconciliation_id: Optional[str] = None,
        bank_reference_number: Optional[str] = None,
        program_mnemonic: Optional[str] = None,
        cycle_mnemonic: Optional[str] = None,
    ) -> int:
        """
        OpenG2P Standard Reconciliation Sync:
        1. Updates applicant status in the NSR base registry table.
        2. Appends an immutable record into NSR's g2p_registry_transaction_ledger.
        """
        if not registrant_ids:
            return 0

        table_name = self._get_nsr_table_name(target_registry)
        amount_val = float(amount or 0.0)

        # 1. Update status and aggregate columns in NSR base registry table
        update_stmt = text(f"""
            UPDATE {table_name}
            SET 
                status = :new_status,
                payment_status = 'RECONCILED_SUCCESS',
                reconciled_at = NOW(),
                completed_tranches_count = COALESCE(completed_tranches_count, 0) + 1,
                total_disbursed_amount = COALESCE(total_disbursed_amount, 0) + :amount,
                last_disbursed_date = NOW(),
                write_date = NOW()
            WHERE internal_record_id = ANY(:registrant_ids)
              AND (:scheme_code IS NULL OR scheme_code = :scheme_code)
              AND status = 'APPLIED'
            RETURNING internal_record_id;
        """)

        result = await sr_session.execute(update_stmt, {
            "new_status": new_status,
            "amount": amount_val,
            "registrant_ids": registrant_ids,
            "scheme_code": scheme_code,
        })
        updated_rows = result.fetchall()

        if not updated_rows:
            return 0

        updated_ids = [row[0] for row in updated_rows]

        # 2. Append immutable record to NSR g2p_registry_transaction_ledger
        ledger_stmt = text(f"""
            INSERT INTO g2p_registry_transaction_ledger (
                target_registry,
                internal_record_id,
                beneficiary_name,
                beneficiary_mobile,
                aadhaar_number,
                scheme_code,
                scheme_name,
                program_mnemonic,
                cycle_mnemonic,
                tranche_number,
                source_system,
                amount,
                currency,
                payment_method,
                bank_account_no,
                ifsc,
                reconciliation_id,
                bank_reference_number,
                transaction_status,
                reconciled_at
            )
            SELECT 
                :target_registry,
                h.internal_record_id,
                COALESCE(h.applicant_name, h.member_name, h.household_reference_name, ''),
                COALESCE(h.mobile_number, ''),
                COALESCE(h.aadhaar_number, ''),
                COALESCE(h.scheme_code, :scheme_code, ''),
                COALESCE(h.scheme_name, :scheme_name, ''),
                :program_mnemonic,
                :cycle_mnemonic,
                :tranche_number,
                'PBMS',
                :amount,
                'INR',
                'DBT_BANK',
                COALESCE(h.bank_account_no, ''),
                COALESCE(h.ifsc, ''),
                :reconciliation_id,
                :bank_reference_number,
                'SUCCESS',
                NOW()
            FROM {table_name} h
            WHERE h.internal_record_id = ANY(:updated_ids);
        """)

        await sr_session.execute(ledger_stmt, {
            "target_registry": target_registry,
            "scheme_code": scheme_code or "",
            "scheme_name": "",
            "program_mnemonic": program_mnemonic or "",
            "cycle_mnemonic": cycle_mnemonic or "",
            "tranche_number": tranche_number,
            "amount": amount_val,
            "reconciliation_id": reconciliation_id or "",
            "bank_reference_number": bank_reference_number or "",
            "updated_ids": updated_ids,
        })

        await sr_session.commit()
        return len(updated_ids)

