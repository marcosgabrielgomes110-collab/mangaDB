# Motor de queries do MangaDB
# Suporta: =, !=, >, <, >=, <=, LIKE, STARTS, ENDS, IN, BETWEEN
import re
from typing import Any, Callable


# Operadores suportados (ordem importa: >= antes de >, <= antes de <)
_OPERATORS = [">=", "<=", "!=", ">", "<", "="]
_TEXT_OPERATORS = ["LIKE", "STARTS", "ENDS", "IN", "BETWEEN"]


class Condition:
    """Uma condição de filtro: campo + operador + valor."""

    def __init__(self, field: str, op: str, value: Any):
        self.field = field
        self.op = op.upper()
        self.value = value

    def match(self, record: dict) -> bool:
        """Testa se o registro satisfaz esta condição."""
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
                # value deve ser uma lista
                return val in self.value
            elif self.op == "BETWEEN":
                # value deve ser (min, max)
                lo, hi = self.value
                n = self._coerce_num(val)
                return self._coerce_num(lo) <= n <= self._coerce_num(hi)
        except (ValueError, TypeError):
            return False

        return False

    @staticmethod
    def _coerce_num(v) -> float:
        """Converte para float para comparações numéricas."""
        if isinstance(v, (int, float)):
            return float(v)
        return float(str(v))

    @staticmethod
    def _coerce_eq(a, b) -> bool:
        """Comparação flexível: tenta numérica, depois string case-insensitive."""
        # Tenta numérica
        try:
            return float(a) == float(b)
        except (ValueError, TypeError):
            pass
        # String case-insensitive
        return str(a).lower() == str(b).lower()

    def __repr__(self):
        return f"Condition({self.field} {self.op} {self.value!r})"


def parse_expression(expr: str) -> Condition | None:
    """
    Analisa uma expressão de filtro em uma Condition.

    Formatos aceitos:
      campo=valor        campo!=valor
      campo>valor        campo>=valor
      campo<valor        campo<=valor
      campo LIKE valor
      campo STARTS valor
      campo ENDS valor
      campo IN val1,val2,val3
      campo BETWEEN min,max
    """
    expr = expr.strip()
    if not expr:
        return None

    # Tenta operadores textuais primeiro (LIKE, STARTS, ENDS, IN, BETWEEN)
    for text_op in _TEXT_OPERATORS:
        # Regex: campo <espaço(s)> OPERADOR <espaço(s)> valor
        pattern = rf'^(\w+)\s+{text_op}\s+(.+)$'
        m = re.match(pattern, expr, re.IGNORECASE)
        if m:
            field = m.group(1).strip()
            raw_val = m.group(2).strip()

            if text_op == "IN":
                value = [v.strip() for v in raw_val.split(",")]
                # Tenta converter para números
                converted = []
                for v in value:
                    try:
                        converted.append(float(v) if "." in v else int(v))
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

    # Tenta operadores simbólicos (>=, <=, !=, >, <, =)
    for op in _OPERATORS:
        idx = expr.find(op)
        if idx > 0:
            field = expr[:idx].strip()
            raw_val = expr[idx + len(op):].strip()

            # Tenta converter valor para número
            try:
                value = float(raw_val) if "." in raw_val else int(raw_val)
            except ValueError:
                value = raw_val

            return Condition(field, op, value)

    return None


def parse_query(query_str: str) -> list[Condition]:
    """
    Analisa múltiplas condições separadas por AND (ou vírgula).

    Exemplo: "idade>18 AND nome LIKE Mar"
    Exemplo: "idade>18, nome LIKE Mar"
    """
    if not query_str or not query_str.strip():
        return []

    # Normaliza separadores
    # Substitui " AND " (case-insensitive) e "," por um delimitador interno
    parts = re.split(r'\s+AND\s+|,', query_str, flags=re.IGNORECASE)

    conditions = []
    for part in parts:
        cond = parse_expression(part.strip())
        if cond:
            conditions.append(cond)

    return conditions


def apply_conditions(records: list[dict], conditions: list[Condition]) -> list[dict]:
    """Filtra uma lista de registros aplicando todas as condições (AND lógico)."""
    if not conditions:
        return records
    return [
        rec for rec in records
        if all(c.match(rec) for c in conditions)
    ]
