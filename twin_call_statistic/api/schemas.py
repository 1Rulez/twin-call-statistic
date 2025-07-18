import json
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, model_validator


class ContactSchema(BaseModel):

    id: UUID
    botId: UUID
    timezone: int | None = None
    nps: str | None = None
    duration: int | None = None
    mainCallDuration: int | None = None
    robotCallDuration: int | None = None
    companyId: int | None = None
    isIncoming: bool | None = None
    createdAt: datetime
    startedAt: datetime | None = None
    finishedAt: datetime | None = None
    status: str | None = None
    confirmation: str | None = None
    evaluation: str | None = None
    currentStatusName: str | None = None
    autoCallCandidateId: str | None = None
    dialogResult: str | None = None
    resultsString: dict | str | None = None
    markersString: str | None = None
    variablesString: dict | str | None = None
    redash_variable: dict | str | None = None
    redash_result: dict | str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_result(cls, values):

        results = values.get("resultsString")
        variables = values.get("variablesString")

        if isinstance(variables, str):
            try:
                variables_dict = json.loads(variables) if variables else None
            except json.JSONDecodeError:
                variables_dict = None
        else:
            variables_dict = results

        redash_variables = {}
        redash_results = {}

        if isinstance(variables_dict, dict):
            for variable in variables_dict:
                if "redash_variable" in variable:
                    redash_variables.update({variable: variables_dict[variable]})
                if len(redash_variables) == 5:
                    break

            for result in variables_dict:
                if "redash_result" in result:
                    redash_results.update({result: variables_dict[result]})
                if len(redash_results) == 5:
                    break

        if redash_variables:
            values["redash_variable"] = redash_variables
        if redash_results:
            values["redash_result"] = redash_results

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
