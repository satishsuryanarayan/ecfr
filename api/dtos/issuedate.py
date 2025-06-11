from datetime import datetime

from marshmallow import Schema, fields, post_load


class IssueDate:
    def __init__(self, issue_date: datetime) -> None:
        self.issue_date = issue_date

    def __repr__(self):
        return f"{self.__class__.__name__}(issue_date={self.issue_date})"


class IssueDateSchema(Schema):
    issue_date = fields.Date(format="%Y-%m-%d", required=True)

    @post_load
    def make_issue_date(self, data: dict, **kwargs: dict) -> IssueDate:
        return IssueDate(**data)
