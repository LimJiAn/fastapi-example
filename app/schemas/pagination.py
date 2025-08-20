from typing import TypeVar
from fastapi import Query
from fastapi_pagination.cursor import CursorPage, CursorParams
from fastapi_pagination.bases import CursorRawParams
from fastapi_pagination.customization import CustomizedPage, UseParamsFields, UseIncludeTotal

from app.core.config import settings

T = TypeVar("T")

class TotalCursorParams(CursorParams):
    """total 계산을 항상 수행하도록 강제"""
    def to_raw_params(self) -> CursorRawParams:
        raw = super().to_raw_params()
        raw.include_total = True
        return raw

CursorPageCustom = CustomizedPage[
    CursorPage[T],
    UseIncludeTotal(True),  # Cursor pagination은 총 개수를 계산하지 않음
    UseParamsFields(size=Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE
    ),  # 기본 20개, 최대 100개
)]


