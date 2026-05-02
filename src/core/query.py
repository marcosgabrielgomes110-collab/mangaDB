import re
import math
from typing import Any

_OPERATORS = [">=", "<=", "!=", ">", "<", "="]
_TEXT_OPERATORS = ["LIKE", "STARTS", "ENDS", "IN", "BETWEEN"]


class Condition:
    def __init__(self, field: str, op: str, value: Any):
        self.field = field
        self.op = op.upper()
        self.value = value

    def match(self, record: dict) -> bool:
        val = record.get(self.field)
        if val is None:
            return False

        try:
            if self.op == "=":
                return self._coerce_eq(val, self.value)
            elif self.op == "!=":
                return not self._coerce_eq(val, self.value)
            elif self.op == ">":
                return self._coerce_num(val) > self._coerce_num(self.value)
            elif self.op == "<":
                return self._coerce_num(val) < self._coerce_num(self.value)
            elif self.op == ">=":
                return self._coerce_num(val) >= self._coerce_num(self.value)
            elif self.op == "<=":
                return self._coerce_num(val) <= self._coerce_num(self.value)
            elif self.op == "LIKE":
                return str(self.value).lower() in str(val).lower()
            elif self.op == "STARTS":
                return str(val).lower().startswith(str(self.value).lower())
            elif self.op == "ENDS":
                return str(val).lower().endswith(str(self.value).lower())
            elif self.op == "IN":
                return val in self.value
            elif self.op == "BETWEEN":
                lo, hi = self.value
                n = self._coerce_num(val)
                return self._coerce_num(lo) <= n <= self._coerce_num(hi)
        except (ValueError, TypeError):
            return False

        return False

    @staticmethod
    def _coerce_num(v) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).replace(',', '.').strip()
        return float(s)

    @staticmethod
    def _coerce_eq(a, b) -> bool:
        if type(a) is type(b) is int:
            return a == b
        if isinstance(a, int) and isinstance(b, int):
            return a == b
        try:
            fa, fb = float(a), float(b)
            if math.isfinite(fa) and math.isfinite(fb):
                return fa == fb
        except (ValueError, TypeError):
            pass
        return str(a).lower() == str(b).lower()

    def __repr__(self):
        return f"Condition({self.field} {self.op} {self.value!r})"


def parse_expression(expr: str) -> Condition | None:
    expr = expr.strip()
    if not expr:
        return None

    for text_op in _TEXT_OPERATORS:
        pattern = rf'^(\w+)\s+{text_op}\s+(.+)$'
        m = re.match(pattern, expr, re.IGNORECASE)
        if m:
            field = m.group(1).strip()
            raw_val = m.group(2).strip()

            if text_op == "IN":
                value = [v.strip() for v in raw_val.split(",")]
                converted = []
                for v in value:
                    try:
                        converted.append(float(v) if ('.' in v or 'e' in v.lower()) else int(v))
                    except ValueError:
                        converted.append(v)
                value = converted
            elif text_op == "BETWEEN":
                parts = [v.strip() for v in raw_val.split(",")]
                if len(parts) != 2:
                    return None
                value = (parts[0], parts[1])
            else:
                value = raw_val

            return Condition(field, text_op, value)

    for op in _OPERATORS:
        idx = expr.find(op)
        if idx > 0:
            field = expr[:idx].strip()
            raw_val = expr[idx + len(op):].strip()

            try:
                value = float(raw_val) if ('.' in raw_val or 'e' in raw_val.lower()) else int(raw_val)
            except ValueError:
                value = raw_val

            return Condition(field, op, value)

    return None


def parse_query(query_str: str) -> list[Condition]:
    if not query_str or not query_str.strip():
        return []

    parts = re.split(r'\s+AND\s+|,', query_str, flags=re.IGNORECASE)

    conditions = []
    for part in parts:
        cond = parse_expression(part.strip())
        if cond:
            conditions.append(cond)

    return conditions


def apply_conditions(records: list[dict], conditions: list[Condition]) -> list[dict]:
    if not conditions:
        return records
    return [
        rec for rec in records
        if all(c.match(rec) for c in conditions)
    ]
