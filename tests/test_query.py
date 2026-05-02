import pytest
from src.core.query import Condition, parse_expression, parse_query, apply_conditions


class TestParseExpression:
    def test_equal(self):
        c = parse_expression("nome=Marcos")
        assert c.field == "nome"
        assert c.op == "="
        assert c.value == "Marcos"

    def test_not_equal(self):
        c = parse_expression("status!=ativo")
        assert c.op == "!="

    def test_greater(self):
        c = parse_expression("idade>18")
        assert c.op == ">"
        assert c.value == 18

    def test_greater_equal(self):
        c = parse_expression("idade>=18")
        assert c.op == ">="

    def test_less(self):
        c = parse_expression("preco<100")
        assert c.op == "<"

    def test_less_equal(self):
        c = parse_expression("preco<=99.9")
        assert c.op == "<="
        assert c.value == 99.9

    def test_scientific_notation(self):
        c = parse_expression("valor>1e5")
        assert c.op == ">"
        assert c.value == 100000.0

    def test_like(self):
        c = parse_expression("nome LIKE Mar")
        assert c.op == "LIKE"
        assert c.value == "Mar"

    def test_starts(self):
        c = parse_expression("nome STARTS Ma")
        assert c.op == "STARTS"

    def test_ends(self):
        c = parse_expression("email ENDS .com")
        assert c.op == "ENDS"

    def test_in(self):
        c = parse_expression("status IN ativo,inativo,pendente")
        assert c.op == "IN"
        assert c.value == ["ativo", "inativo", "pendente"]

    def test_in_with_numbers(self):
        c = parse_expression("idade IN 1,2,3")
        assert c.value == [1, 2, 3]

    def test_between(self):
        c = parse_expression("idade BETWEEN 18,65")
        assert c.op == "BETWEEN"
        assert c.value == ("18", "65")

    def test_empty(self):
        assert parse_expression("") is None

    def test_invalid(self):
        assert parse_expression("campo BETWEEN 1,2,3") is None


class TestParseQuery:
    def test_and(self):
        conds = parse_query("idade>18 AND nome LIKE Mar")
        assert len(conds) == 2

    def test_comma(self):
        conds = parse_query("idade>18, nome LIKE Mar")
        assert len(conds) == 2

    def test_empty(self):
        assert parse_query("") == []


RECORDS = [
    {"nome": "Marcos", "idade": 25, "email": "marcos@x.com"},
    {"nome": "Maria", "idade": 17, "email": "maria@y.org"},
    {"nome": "Joao", "idade": 40, "email": "joao@x.com"},
]


class TestConditionMatch:
    def test_eq(self):
        c = Condition("nome", "=", "Marcos")
        assert c.match(RECORDS[0])
        assert not c.match(RECORDS[1])

    def test_neq(self):
        c = Condition("nome", "!=", "Marcos")
        assert not c.match(RECORDS[0])
        assert c.match(RECORDS[1])

    def test_gt(self):
        c = Condition("idade", ">", 18)
        assert c.match(RECORDS[0])
        assert not c.match(RECORDS[1])

    def test_gte(self):
        c = Condition("idade", ">=", 25)
        assert c.match(RECORDS[0])
        assert not c.match(RECORDS[1])

    def test_lt(self):
        c = Condition("idade", "<", 18)
        assert not c.match(RECORDS[0])
        assert c.match(RECORDS[1])

    def test_lte(self):
        c = Condition("idade", "<=", 25)
        assert c.match(RECORDS[0])
        assert c.match(RECORDS[1])
        assert not c.match(RECORDS[2])

    def test_like(self):
        c = Condition("nome", "LIKE", "Mar")
        assert c.match(RECORDS[0])
        assert c.match(RECORDS[1])
        assert not c.match(RECORDS[2])

    def test_starts(self):
        c = Condition("nome", "STARTS", "Jo")
        assert not c.match(RECORDS[0])
        assert c.match(RECORDS[2])

    def test_ends(self):
        c = Condition("email", "ENDS", ".com")
        assert c.match(RECORDS[0])
        assert not c.match(RECORDS[1])

    def test_in(self):
        c = Condition("nome", "IN", ["Marcos", "Maria"])
        assert c.match(RECORDS[0])
        assert c.match(RECORDS[1])
        assert not c.match(RECORDS[2])

    def test_between(self):
        c = Condition("idade", "BETWEEN", (18, 30))
        assert c.match(RECORDS[0])
        assert not c.match(RECORDS[1])
        assert not c.match(RECORDS[2])

    def test_missing_field(self):
        c = Condition("telefone", "=", "123")
        assert not c.match(RECORDS[0])

    def test_scientific_notation(self):
        c = Condition("valor", ">", 1e5)
        record = {"valor": 200000}
        assert c.match(record)

    def test_large_int_eq(self):
        c = Condition("big", "=", 9007199254740992)
        record = {"big": 9007199254740993}
        assert c.match(record) is False


class TestApplyConditions:
    def test_multiple(self):
        conds = [
            Condition("idade", ">", 18),
            Condition("email", "ENDS", ".com"),
        ]
        result = apply_conditions(RECORDS, conds)
        assert len(result) == 2

    def test_no_conditions(self):
        assert apply_conditions(RECORDS, []) == RECORDS

    def test_empty_records(self):
        assert apply_conditions([], [Condition("a", "=", "1")]) == []

    def test_bool_field(self):
        records = [{"name": "x", "active": True}, {"name": "y", "active": False}]
        c = Condition("active", "=", True)
        result = apply_conditions(records, [c])
        assert len(result) == 1
        assert result[0]["name"] == "x"
