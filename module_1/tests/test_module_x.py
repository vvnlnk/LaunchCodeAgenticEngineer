"""Unit tests for the public functions in module_x.py."""

import pytest

from module_x import (
    VALID_CUSTOMER_TIERS,
    calculate_discount,
    classify_priority,
    is_valid_project_code,
    normalize_name,
    summarize_order,
)


class TestNormalizeName:
    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("ada lovelace", "Ada Lovelace"),
            ("  ada lovelace  ", "Ada Lovelace"),
            ("ada    lovelace", "Ada Lovelace"),
            ("ada\tlovelace\nbyron", "Ada Lovelace Byron"),
            ("ADA LOVELACE", "Ada Lovelace"),
            ("aDa LoVeLaCe", "Ada Lovelace"),
            ("ada", "Ada"),
        ],
    )
    def test_collapses_whitespace_and_title_cases(self, raw, expected):
        assert normalize_name(raw) == expected

    def test_hyphenated_and_apostrophe_names_capitalize_each_part(self):
        # str.title() treats non-alpha characters as word boundaries.
        assert normalize_name("mary-jane o'brien") == "Mary-Jane O'Brien"

    @pytest.mark.parametrize("raw", ["", "   ", "\t\n  "])
    def test_empty_or_whitespace_only_raises_value_error(self, raw):
        with pytest.raises(ValueError, match="name cannot be empty"):
            normalize_name(raw)

    @pytest.mark.parametrize("raw", [None, 42, 3.5, ["ada"], {"name": "ada"}, b"ada"])
    def test_non_string_raises_type_error(self, raw):
        with pytest.raises(TypeError, match="name must be a string"):
            normalize_name(raw)


class TestCalculateDiscount:
    @pytest.mark.parametrize(
        "tier, expected",
        [
            ("standard", 100.00),
            ("silver", 95.00),
            ("gold", 90.00),
            ("platinum", 85.00),
        ],
    )
    def test_applies_the_rate_for_each_tier(self, tier, expected):
        assert calculate_discount(100.0, tier) == expected

    @pytest.mark.parametrize("tier", ["GOLD", "Gold", "  gold  ", "\tGoLd\n"])
    def test_tier_is_case_insensitive_and_whitespace_tolerant(self, tier):
        assert calculate_discount(100.0, tier) == 90.00

    def test_every_documented_tier_is_accepted(self):
        for tier in VALID_CUSTOMER_TIERS:
            assert calculate_discount(50.0, tier) >= 0

    def test_zero_price_stays_zero(self):
        assert calculate_discount(0, "platinum") == 0.0

    def test_result_is_rounded_to_two_decimal_places(self):
        # 19.99 * 0.95 == 18.9905
        assert calculate_discount(19.99, "silver") == 18.99

    def test_integer_price_is_accepted(self):
        assert calculate_discount(200, "gold") == 180.00

    def test_negative_price_raises_value_error(self):
        with pytest.raises(ValueError, match="price cannot be negative"):
            calculate_discount(-0.01, "gold")

    @pytest.mark.parametrize("tier", ["bronze", "", "  ", "gold ish", "platinum!"])
    def test_unknown_tier_raises_value_error(self, tier):
        with pytest.raises(ValueError, match="unknown customer tier"):
            calculate_discount(100.0, tier)

    def test_unknown_tier_error_reports_the_original_input(self):
        with pytest.raises(ValueError, match="unknown customer tier: Bronze"):
            calculate_discount(100.0, "Bronze")

    def test_price_is_validated_before_tier(self):
        with pytest.raises(ValueError, match="price cannot be negative"):
            calculate_discount(-1, "bronze")


class TestClassifyPriority:
    @pytest.mark.parametrize(
        "score, expected",
        [
            (0, "low"),
            (39, "low"),
            (40, "medium"),
            (69, "medium"),
            (70, "high"),
            (89, "high"),
            (90, "urgent"),
            (100, "urgent"),
        ],
    )
    def test_boundaries_of_each_band(self, score, expected):
        assert classify_priority(score) == expected

    @pytest.mark.parametrize("score", [-1, -100, 101, 1000])
    def test_out_of_range_raises_value_error(self, score):
        with pytest.raises(ValueError, match="score must be between 0 and 100"):
            classify_priority(score)

    @pytest.mark.parametrize("score", [None, "50", 50.0, 90.5, [50]])
    def test_non_integer_raises_type_error(self, score):
        with pytest.raises(TypeError, match="score must be an integer"):
            classify_priority(score)

    def test_type_is_validated_before_range(self):
        with pytest.raises(TypeError, match="score must be an integer"):
            classify_priority(-5.0)


class TestSummarizeOrder:
    def test_empty_order_returns_zeroed_summary(self):
        assert summarize_order([]) == {"item_count": 0, "subtotal": 0.0}

    def test_single_item(self):
        items = [{"quantity": 3, "unit_price": 2.50}]
        assert summarize_order(items) == {"item_count": 3, "subtotal": 7.50}

    def test_multiple_items_are_accumulated(self):
        items = [
            {"quantity": 2, "unit_price": 10.00},
            {"quantity": 1, "unit_price": 5.25},
            {"quantity": 4, "unit_price": 0.50},
        ]
        assert summarize_order(items) == {"item_count": 7, "subtotal": 27.25}

    def test_missing_keys_default_to_zero(self):
        items = [{"name": "widget"}, {"quantity": 2}, {"unit_price": 9.99}]
        assert summarize_order(items) == {"item_count": 2, "subtotal": 0.0}

    def test_zero_quantity_and_zero_price_are_allowed(self):
        items = [{"quantity": 0, "unit_price": 100.0}, {"quantity": 5, "unit_price": 0}]
        assert summarize_order(items) == {"item_count": 5, "subtotal": 0.0}

    def test_integer_unit_price_is_accepted(self):
        items = [{"quantity": 2, "unit_price": 3}]
        assert summarize_order(items) == {"item_count": 2, "subtotal": 6.0}

    def test_subtotal_is_rounded_to_two_decimal_places(self):
        # 3 * 0.1 == 0.30000000000000004 in binary floating point.
        items = [{"quantity": 3, "unit_price": 0.1}]
        assert summarize_order(items) == {"item_count": 3, "subtotal": 0.3}

    def test_extra_keys_on_an_item_are_ignored(self):
        items = [{"quantity": 1, "unit_price": 2.0, "sku": "A1", "note": "gift"}]
        assert summarize_order(items) == {"item_count": 1, "subtotal": 2.0}

    @pytest.mark.parametrize("quantity", [-1, 1.5, "2", None, [1]])
    def test_invalid_quantity_raises_value_error(self, quantity):
        items = [{"quantity": quantity, "unit_price": 1.0}]
        with pytest.raises(ValueError, match="quantity must be a non-negative integer"):
            summarize_order(items)

    @pytest.mark.parametrize("unit_price", [-0.01, "1.0", None, [1.0]])
    def test_invalid_unit_price_raises_value_error(self, unit_price):
        items = [{"quantity": 1, "unit_price": unit_price}]
        with pytest.raises(ValueError, match="unit_price must be a non-negative number"):
            summarize_order(items)

    def test_a_bad_item_later_in_the_order_still_raises(self):
        items = [{"quantity": 1, "unit_price": 1.0}, {"quantity": -1, "unit_price": 1.0}]
        with pytest.raises(ValueError, match="quantity must be a non-negative integer"):
            summarize_order(items)

    def test_quantity_is_validated_before_unit_price(self):
        items = [{"quantity": -1, "unit_price": -1}]
        with pytest.raises(ValueError, match="quantity must be a non-negative integer"):
            summarize_order(items)

    def test_returns_a_new_dict_each_call(self):
        first = summarize_order([])
        second = summarize_order([])
        assert first == second
        assert first is not second


class TestIsValidProjectCode:
    @pytest.mark.parametrize("code", ["AA-1234", "AB-0000", "ZZ-9999", "QQ-0001"])
    def test_accepts_well_formed_codes(self, code):
        assert is_valid_project_code(code) is True

    @pytest.mark.parametrize(
        "code",
        [
            "aa-1234",  # lowercase prefix
            "Aa-1234",  # mixed-case prefix
            "A-1234",  # prefix too short
            "ABC-1234",  # prefix too long
            "A1-1234",  # non-alphabetic prefix
            "AB-123",  # number too short
            "AB-12345",  # number too long
            "AB-12a4",  # non-numeric body
            "AB-1234-5",  # too many segments
            "AB1234",  # missing separator
            "AB_1234",  # wrong separator
            "AB - 1234",  # padded separator
            " AB-1234",  # leading whitespace
            "AB-1234 ",  # trailing whitespace
            "-1234",  # missing prefix
            "AB-",  # missing number
            "",
            "-",
        ],
    )
    def test_rejects_malformed_codes(self, code):
        assert is_valid_project_code(code) is False

    @pytest.mark.parametrize("code", [None, 1234, 12.34, ["AA-1234"], b"AA-1234"])
    def test_rejects_non_string_input(self, code):
        assert is_valid_project_code(code) is False
