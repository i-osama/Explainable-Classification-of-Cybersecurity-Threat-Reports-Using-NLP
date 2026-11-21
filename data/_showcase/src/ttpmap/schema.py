"""Typed data models (pydantic v2). Every shipped table is validated row by row against one of these."""
from __future__ import annotations

from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Split = Literal["train", "dev", "test"]
ClaimStatus = Literal["VERIFIED", "RECOMPUTED", "NOTES-ONLY", "NOT-FOUND", "TODO-COLAB"]
TECH_RE = r"^T\d{4}(\.\d{3})?$"


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Sentence(_Base):
    """One CTI sentence. The text itself is NOT shipped (licence unknown): only its SHA-256 and length."""
    id: str = Field(pattern=r"^(train|dev|test)-\d{4}$")
    split: Split
    text_sha256: str = Field(min_length=64, max_length=64)
    n_words: int = Field(ge=1)
    labels: List[str] = Field(min_length=1)

    @field_validator("labels")
    @classmethod
    def _ids(cls, v):
        import re
        assert all(re.match(TECH_RE, x) for x in v), f"bad technique id in {v}"
        assert len(set(v)) == len(v), "duplicate label"
        return v


class Technique(_Base):
    """One ATT&CK technique or sub-technique in the 733-label matching space."""
    id: str = Field(pattern=TECH_RE)
    name: str
    tactics: List[str]
    parent_id: Optional[str] = Field(default=None, pattern=r"^T\d{4}$")
    is_sub: bool
    train_support: int = Field(ge=0)
    dev_support: int = Field(ge=0)
    test_support: int = Field(ge=0)

    @model_validator(mode="after")
    def _parent(self):
        assert self.is_sub == ("." in self.id), "is_sub must match the id"
        assert (self.parent_id == self.id.split(".")[0]) if self.is_sub else (self.parent_id is None), "parent_id inconsistent"
        return self


class ScoreMatrix(_Base):
    """Pointer to one saved score matrix (the matrix stays in its original file)."""
    system: str
    seed: Union[int, Literal["avg", "-"]]
    split: Literal["dev", "test"]
    n_sentences: int = Field(gt=0)
    n_labels: int = Field(gt=0)
    score_kind: Literal["probability", "cosine", "decision_function", "z_sum"]
    source_file: str
    sha256: Optional[str] = None


class Prediction(_Base):
    """Top-3 labels of one system for one test sentence."""
    sentence_id: str = Field(pattern=r"^test-\d{4}$")
    system: str
    top1: str = Field(pattern=TECH_RE)
    top2: str = Field(pattern=TECH_RE)
    top3: str = Field(pattern=TECH_RE)
    hit_at_1: bool
    rr_at_3: float = Field(ge=0, le=1)


class RunManifest(_Base):
    """One training or analysis run."""
    run_id: str
    system: str
    seed: Union[int, Literal["avg", "-"]]
    config_hash: str
    env: Dict[str, str]
    input_sha256: Dict[str, str]
    output_sha256: Dict[str, str]
    metrics: Dict[str, float]
    status: Literal["DONE", "SMOKE", "TODO-COLAB", "FAILED"]


class Claim(_Base):
    """One number (or fact) the thesis may state. The single source of truth is thesis_numbers.json."""
    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_.-]*$")
    label: str
    value: Union[float, int, str, None]
    display: str
    ci: Optional[List[float]] = None
    definition: str
    source_file: str
    script: str
    status: ClaimStatus
    thesis_section: str
    note: str = ""

    @model_validator(mode="after")
    def _ci(self):
        assert self.ci is None or (len(self.ci) == 2 and self.ci[0] <= self.ci[1]), "ci must be [lo, hi]"
        assert (self.value is None) == (self.status in ("NOT-FOUND", "TODO-COLAB")), "value must be null exactly for NOT-FOUND / TODO-COLAB"
        return self


TABLE_MODELS = {"sentences": Sentence, "techniques": Technique, "score_matrices": ScoreMatrix, "predictions": Prediction}


def validate_rows(rows: List[dict], model: type[BaseModel]) -> int:
    """Validate every row; raises on the first invalid row. Returns the number of rows."""
    for r in rows:
        model.model_validate(r)
    return len(rows)
