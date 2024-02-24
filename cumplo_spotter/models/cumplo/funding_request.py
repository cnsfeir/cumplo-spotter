# mypy: disable-error-code="call-overload"
# pylint: disable=no-member

from decimal import Decimal
from enum import StrEnum
from functools import cached_property
from typing import Any

from cumplo_common.models.credit import CreditType
from cumplo_common.models.currency import Currency
from cumplo_common.models.funding_request import FundingRequest
from cumplo_common.utils.text import clean_text
from pydantic import BaseModel, Field, field_validator

from cumplo_spotter.models.cumplo.borrower import Borrower
from cumplo_spotter.models.cumplo.debtor import Debtor
from cumplo_spotter.models.cumplo.request_duration import CumploFundingRequestDuration
from cumplo_spotter.models.cumplo.simulation import CumploFundingRequestSimulation


class CumploCreditType(StrEnum):
    IRRIGATION = "irrigation"
    BALLOON = "balloon"
    INVOICE = "invoice"
    BULLET = "bullet"
    SIMPLE = "simple"


CREDIT_TYPE_TRANSLATIONS = {
    CumploCreditType.IRRIGATION: CreditType.STATE_SUBSIDY,
    CumploCreditType.SIMPLE: CreditType.WORKING_CAPITAL,
    CumploCreditType.BALLOON: CreditType.BULLET_LOAN,
    CumploCreditType.BULLET: CreditType.BULLET_LOAN,
    CumploCreditType.INVOICE: CreditType.FACTORING,
}


class CumploFundingRequest(BaseModel):
    id: int = Field(..., alias="id_operacion")
    score: Decimal = Field(...)
    irr: Decimal = Field(..., alias="tir")
    installments: int = Field(..., alias="cuotas")
    currency: Currency = Field(..., alias="moneda")
    amount: int = Field(..., alias="monto_financiar")
    credit_type: CreditType = Field(..., alias="tipo_credito")
    due_date: str = Field(..., alias="fecha_vencimiento")
    raised_amount: int = Field(..., alias="total_inversion")
    maximum_investment: int = Field(..., alias="max_inversion")
    investors: int = Field(..., alias="cantidad_inversionistas")
    funded_percentage: Decimal = Field(..., alias="porcentaje_inversion")

    supporting_documents: list[str] = Field(default_factory=list, alias="tipo_respaldo")
    duration: CumploFundingRequestDuration = Field(..., alias="plazo")
    simulation: CumploFundingRequestSimulation = Field(...)
    debtors: list[Debtor] = Field(default_factory=list, alias="pagadores")
    borrower: Borrower = Field(..., alias="solicitante")

    @field_validator("supporting_documents", mode="before")
    @classmethod
    def _format_supporting_documents(cls, value: Any) -> list[str]:
        """Formats the supporting documents names"""
        return [clean_text(document) for document in value]

    @field_validator("funded_percentage", mode="before")
    @classmethod
    def funded_percentage_validator(cls, value: Any) -> Decimal:
        """Validates that the funded percentage is a valid decimal number"""
        return round(Decimal(int(value) / 100), 2)

    @field_validator("credit_type", mode="before")
    @classmethod
    def credit_type_validator(cls, value: Any) -> CreditType:
        """Validates that the credit_type has a valid value"""
        return CREDIT_TYPE_TRANSLATIONS[value]

    @cached_property
    def is_completed(self) -> bool:
        """Checks if the funding request is fully funded"""
        return self.funded_percentage == Decimal(1)

    def export(self) -> FundingRequest:
        """Exports the CumploFundingRequest to a FundingRequest"""
        return FundingRequest.model_validate(self.model_dump(exclude_none=True, exclude_unset=True))
