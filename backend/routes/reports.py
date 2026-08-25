from fastapi import APIRouter
from models import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])

fake_reports_db = []

@router.post("/", response_model=ReportResponse)
def create_report(report: ReportCreate):
    fake_reports_db.append(report.dict())
    return {"message": "Report received", "total_reports": len(fake_reports_db)}

@router.get("/{train_id}")
def get_reports(train_id: str):
    matching = [r for r in fake_reports_db if r.get("train_id") == train_id]
    return {"train_id": train_id, "reports": matching}