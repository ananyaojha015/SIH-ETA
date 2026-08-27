from crowd.verification import verify_reports
from crowd.summary import generate_summary


def process_reports(reports):
    result = verify_reports(reports)

    if result["report_count"] == 0:
        return result

    result["summary"] = generate_summary(result)

    return result