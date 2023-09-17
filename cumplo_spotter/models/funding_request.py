# mypy: disable-error-code="call-overload"
# pylint: disable=no-member

from decimal import Decimal
from enum import StrEnum
from functools import cached_property
from typing import Any

from cumplo_common.models.credit import CreditType
from cumplo_common.models.currency import Currency
from cumplo_common.models.funding_request import FundingRequest
from cumplo_common.models.pydantic import ValidatorMode
from pydantic import BaseModel, Field, field_validator

from cumplo_spotter.models.borrower import CumploBorrower
from cumplo_spotter.models.request_duration import FundingRequestDuration


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
    id: int = Field(...)
    score: Decimal = Field(...)
    borrower: CumploBorrower = Field(...)
    irr: Decimal = Field(..., alias="tir")
    currency: Currency = Field(..., alias="moneda")
    amount: int = Field(..., alias="monto_financiar")
    anual_profit_rate: Decimal = Field(..., alias="tasa_anual")
    duration: FundingRequestDuration = Field(..., alias="plazo")
    supporting_documents: list[str] = Field(default_factory=list)
    funded_amount_percentage: Decimal = Field(..., alias="porcentaje_inversion")
    credit_type: str = Field(..., alias="tipo_respaldo")

    @field_validator("funded_amount_percentage", mode=ValidatorMode.BEFORE)
    @classmethod
    def funded_amount_percentage_validator(cls, value: Any) -> Decimal:
        """
        Validates that the funded_amount_percentage is a valid decimal number.
        If it is not, it returns 0 which means that it does not have a credit history yet.
        """
        try:
            return round(Decimal(int(value) / 100), 2)
        except ValueError:
            return Decimal(0)

    @field_validator("anual_profit_rate", mode=ValidatorMode.BEFORE)
    @classmethod
    def anual_profit_rate_validator(cls, value: Any) -> Decimal:
        """Validates that the anual_profit_rate is a valid decimal number"""
        return round(Decimal(int(value) / 100), 2)

    @field_validator("credit_type")
    @classmethod
    def credit_type_validator(cls, value: Any) -> CreditType:
        """Validates that the credit_type has a valid value"""
        return CREDIT_TYPE_TRANSLATIONS[value]

    @cached_property
    def is_completed(self) -> bool:
        """Checks if the funding request is fully funded"""
        return self.funded_amount_percentage == Decimal(1)

    def export(self) -> FundingRequest:
        """Exports the CumploFundingRequest to a FundingRequest"""
        return FundingRequest.model_validate(self.model_dump(exclude_none=True, exclude_unset=True))
