import json
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, model_validator


class ContactSchema(BaseModel):

    id: UUID
    botId: UUID
    timezone: int | None
    nps: str | None
    duration: int | None
    mainCallDuration: int | None
    robotCallDuration: int | None
    companyId: int | None
    isIncoming: bool | None
    createdAt: datetime
    startedAt: datetime | None
    finishedAt: datetime | None
    status: str | None
    confirmation: str | None
    evaluation: str | None
    currentStatusName: str | None
    autoCallCandidateId: str | None
    dialogResult: str | None
    resultsString: dict | str | None

    @model_validator(mode="before")
    @classmethod
    def validate_result(cls, values):

        results = values.get("resultsString")

        if isinstance(results, str):
            try:
                results_dict = json.loads(results) if results else None
            except json.JSONDecodeError:
                results_dict = None
        else:
            results_dict = results

        if isinstance(results_dict, dict):
            values["status"] = results_dict.get("status")
            values["confirmation"] = results_dict.get("confirmation")
            values["evaluation"] = results_dict.get("evaluation")
            values["resultsString"] = results_dict

        else:
            values["status"] = values["confirmation"] = None
            values["resultsString"] = values["evaluation"] = None
        return values


