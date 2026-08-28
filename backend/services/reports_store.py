fake_reports_db = []


def add_report(report: dict):
    fake_reports_db.append(report)


def get_reports_for_train(train_id: str):
    return [r for r in fake_reports_db if r.get("train_id") == train_id]


def get_all_reports():
    return fake_reports_db