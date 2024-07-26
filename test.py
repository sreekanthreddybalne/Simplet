from unittest import TestCase

from parameterized import parameterized

from main import reduce_value, transform_primitive_type


class TestPrimitiveTypeTransformer(TestCase):
    @parameterized.expand(
        [
            ("John", "John"),
            (" John", "John"),
            (" John ", "John"),
            ("Hello world ", "Hello world"),
            ("123", "123"),
            ("2014-07-16T20:55:46Z", 1405544146),
        ]
    )
    def test_valid_string(self, raw_value, expected_output):
        self.assertEqual(
            transform_primitive_type(key="S", val=raw_value), expected_output
        )

    @parameterized.expand(
        [
            (123,),
            ({},),
            ([],),
            (["Sree"],),
            ("",),
            ("  ",),
            (None,),
        ]
    )
    def test_invalid_string(self, raw_value):
        with self.assertRaises(ValueError):
            transform_primitive_type(key="S", val=raw_value)

    @parameterized.expand(
        [
            ("123", 123),
            ("0123", 123),
            (" 123", 123),
            ("-123", -123),
            ("-1.50 ", -1.5),
            (" 1.50 ", 1.5),
            (" 01.50 ", 1.5),
            ("999.0 ", 999.0),
        ]
    )
    def test_valid_number(self, raw_value, expected_output):
        self.assertEqual(
            transform_primitive_type(key="N", val=raw_value), expected_output
        )

    @parameterized.expand(
        [
            (
                123,  # All raw values are expected to be in string format. So, this is considered as an invalid raw value.
            ),
            ("123..44",),
            ({},),
            ([],),
            (["Sree"],),
            ("",),
            ("  ",),
            (None,),
        ]
    )
    def test_invalid_number(self, raw_value):
        with self.assertRaises(ValueError):
            transform_primitive_type(key="N", val=raw_value)

    @parameterized.expand(
        [
            ("1", True),
            ("t", True),
            ("T", True),
            ("TRUE", True),
            ("true", True),
            ("True", True),
            ("0", False),
            ("0   ", False),
            ("f", False),
            ("f ", False),
            ("F", False),
            ("FALSE", False),
            ("false", False),
            ("False", False),
            (" False ", False),
        ]
    )
    def test_valid_boolean(self, raw_value, expected_output):
        self.assertEqual(
            transform_primitive_type(key="BOOL", val=raw_value), expected_output
        )

    @parameterized.expand(
        [
            (
                0,  # All raw values are expected to be in string format. So, this is considered as an invalid raw value.
            ),
            (
                1,  # All raw values are expected to be in string format. So, this is considered as an invalid raw value.
            ),
            ("3",),
            ({},),
            ([],),
            (["Sree"],),
            ("",),
            ("  ",),
            ("truthy",),
            (None,),
        ]
    )
    def test_invalid_boolean(self, raw_value):
        with self.assertRaises(ValueError):
            transform_primitive_type(key="BOOL", val=raw_value)

    @parameterized.expand(
        [
            ("1", None),
            ("t", None),
            ("T", None),
            ("TRUE", None),
            ("true", None),
            ("True", None),
        ]
    )
    def test_valid_null(self, raw_value, expected_output):
        self.assertEqual(
            transform_primitive_type(key="NULL", val=raw_value), expected_output
        )

    @parameterized.expand(
        [
            (0,),
            (
                1,  # All raw values are expected to be in string format. So, this is considered as an invalid raw value.
            ),
            ("3",),
            ({},),
            ([],),
            (["Sree"],),
            ("",),
            ("  ",),
            ("truthy",),
            (None,),
            ("f",),
            ("False",),
            (False,),
            (True,),
        ]
    )
    def test_invalid_null(self, raw_value):
        with self.assertRaises(ValueError):
            transform_primitive_type(key="NULL", val=raw_value)


class TestReduceValue(TestCase):
    @parameterized.expand(
        [
            (
                [{"S": "John"}, {"S": "123"}, {"N": "123"}, {"N": "123.50"}],
                ["John", "123", 123, 123.5],
            ),
            (
                [
                    {"S": "John"},
                    {"N ": "123.22"},
                    {"S": "2014-07-16T20:55:46Z"},
                    {"S": "123"},
                    {"BOOL": "truthy"},
                    {"BOOL": "t"},
                    {"NULL": "t"},
                    {"M": "t"},
                    {"M": {}},
                    {"M": {"name": {"S": "John"}}},
                    {"L": []},
                    {"L": [{"S": "John"}]},
                ],
                [
                    "John",
                    123.22,
                    1405544146,
                    "123",
                    True,
                ],
            ),
        ]
    )
    def test_valid_list(self, raw_value, expected_output):
        self.assertEqual(reduce_value({"L": raw_value}), expected_output)

    @parameterized.expand(
        [
            ([],),
            (["none"],),
            (["none", "1", 123],),
            (123,),
            ({},),
            ("",),
            ("Hello",),
            ("123",),
            ({"S": "John"},),
        ]
    )
    def test_invalid_list(self, raw_value):
        with self.assertRaises(ValueError):
            reduce_value({"L": raw_value})

    def test_valid_map(self):
        raw_value = {
            "name": {"S": "John"},
            "age": {"N": "24"},
            "debt": {"N": "-1000.8000"},
            "balance": {"N": " 000019.60"},
            "favorite_number": {"S": "9"},
            "valid_list": {
                "L": [
                    {"N": 1},
                    {"N": "2"},
                    {"N": "3.0"},
                    {"S": "4.000"},
                    {"M": {"name": {"S": "John"}}},
                    {"NULL": "t"},
                    {"BOOL": "t"},
                ]
            },
            "valid_map": {"M": {"name": {"S": "John"}}},
            "invalid_val1": "9",
            "invalid_val2": 333,
            "invalid_val3": {"M": {}},
            "invalid_val4": {"M": {"S": ""}},
            "invalid_val5": {"M": {"S": "124"}},
            "invalid_val6": {"M": {"name": {"S": ""}}},
            "invalid_val7": {"M": {"age": {"N": ""}}},
        }
        expected_output = {
            "age": 24,
            "balance": 19.6,
            "debt": -1000.8,
            "favorite_number": "9",
            "name": "John",
            "valid_list": [2, 3.0, "4.000", True],
            "valid_map": {"name": "John"},
        }
        self.assertEqual(reduce_value({"M": raw_value}), expected_output)

    @parameterized.expand(
        [
            (0,),
            (
                1,  # All raw values are expected to be in string format. So, this is considered as an invalid raw value.
            ),
            ("3",),
            ({},),
            ({"S": ""},),
            ({"S": "John"},),
            ({"name": {"S": ""}},),
            ({"name": {"S": "   "}},),
            ({"name": {"L": ""}},),
            ({"name": {"L": []}},),
            ([],),
            (["Sree"],),
            ("",),
            ("  ",),
            ("truthy",),
            (None,),
            ("f",),
            ("False",),
            (False,),
            (True,),
        ]
    )
    def test_invalid_map(self, raw_value):
        with self.assertRaises(ValueError):
            reduce_value({"M": raw_value})

    def test_map_sorted_lexically(self):
        raw_value = {
            "M": {"last": {"N": "124"}, "first": {"BOOL": "t"}, "game": {"NULL": "t"}}
        }
        result = reduce_value(raw_value)
        self.assertEqual(list(result.keys()), ["first", "game", "last"])
