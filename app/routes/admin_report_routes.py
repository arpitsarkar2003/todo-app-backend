from fastapi import APIRouter, Depends

from app.dependencies.auth_dependencies import get_current_admin
from app.schemas.admin_schemas import AdminReportSummary
from app.services import admin_service


router = APIRouter(prefix="/api/v1/admin/reports", tags=["admin-reports"])


@router.get("/summary", response_model=AdminReportSummary)
async def get_admin_summary_report(current_admin=Depends(get_current_admin)):
    report_data = await admin_service.get_summary_report()
    return report_data

