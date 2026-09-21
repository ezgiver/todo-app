from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

StepText = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=120)]


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: StepText
    done_when: StepText


class StepsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    steps: list[Step] = Field(min_length=1, max_length=3)
