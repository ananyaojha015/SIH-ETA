from fastapi import APIRouter
from models import ReportCreate, ReportResponse
from services.crowd_service import evaluate_reports
from services.reports_store import add_report, get_reports_for_train, get_all_reports

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse)
def create_report(report: ReportCreate):
    add_report(report.dict())
    return {"message": "Report received", "total_reports": len(get_all_reports())}


@router.get("/{train_id}")
def get_reports(train_id: str):
    matching = get_reports_for_train(train_id)
    verification = evaluate_reports(train_id, get_all_reports())
    return {
        "train_id": train_id,
        "reports": matching,
        "verification": verification,
    }