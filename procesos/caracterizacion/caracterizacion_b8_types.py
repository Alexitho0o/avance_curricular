from dataclasses import dataclass


@dataclass
class B8HeaderMeta:
    column_index: int
    column_letter: str
    header_original: str
    header_normalized: str
    key: str
    base_code: str
    sub_code: str
    category_block: str
    category_name: str
    question_text: str
    subquestion_text: str
    structure_type: str
    response_mode: str
    analyzable: bool
    exclusion_reason: str


@dataclass
class B8SummaryRecord:
    category_block: str
    category_name: str
    base_code: str
    key: str
    sub_code: str
    structure_type: str
    response_mode: str
    column_letter: str
    question_text: str
    subquestion_text: str
    total_records: int
    answered_count: int
    blank_count: int
    response_rate: float
    distinct_answers: int
    top_answer: str
    top_answer_count: int
    top_answer_pct: float


@dataclass
class B8DetailRecord:
    category_block: str
    category_name: str
    base_code: str
    key: str
    sub_code: str
    structure_type: str
    column_letter: str
    question_text: str
    subquestion_text: str
    answer: str
    count: int
    pct_answered: float
    pct_total: float


@dataclass
class B8CategoryKpiRecord:
    category_block: str
    category_name: str
    total_questions: int
    avg_response_rate: float
    min_response_rate: float
    max_response_rate: float
    full_response_questions: int
    no_response_questions: int
    avg_distinct_answers: float
    total_answered_cells: int
    total_blank_cells: int
    response_volume_rate: float


@dataclass
class B8BinaryExecutiveRecord:
    category_block: str
    category_name: str
    base_code: str
    key: str
    question_text: str
    subquestion_text: str
    yes_count: int
    no_count: int
    no_response_count: int
    na_excluded_count: int
    analytic_base: int
    pct_yes: float
    pct_no: float
    pct_no_response: float
    sort_label: str
