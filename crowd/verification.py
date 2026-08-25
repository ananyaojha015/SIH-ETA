def get_confidence(report_count):
    if report_count >= 10:
        return "High"
    elif report_count >= 5:
        return "Medium"
    else:
        return "Low"


def verify_reports(reports):
    if not reports:
        return {
            "report_count": 0,
            "confidence": "Low"
        }

    first_report = reports[0]

    consistent_reports = [
        report for report in reports
        if report.train_id == first_report.train_id
        and report.type == first_report.type
        and report.location == first_report.location
    ]

    count = len(consistent_reports)

    return {
        "train_id": first_report.train_id,
        "type": first_report.type,
        "location": first_report.location,
        "report_count": count,
        "confidence": get_confidence(count)
    }