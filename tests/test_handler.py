from __future__ import annotations

import unittest

from pokemon_service.handler import compute_summary, parse_names, transform_record


class ParseNamesTests(unittest.TestCase):
    def test_parse_names_preserves_duplicates(self) -> None:
        self.assertEqual(
            parse_names("pikachu, charizard,pikachu"),
            ["pikachu", "charizard", "pikachu"],
        )

    def test_parse_names_rejects_missing_value(self) -> None:
        with self.assertRaisesRegex(ValueError, "required"):
            parse_names(None)

    def test_parse_names_rejects_empty_value(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            parse_names(" ,, ")


class TransformRecordTests(unittest.TestCase):
    def test_transform_record_extracts_requested_fields(self) -> None:
        record = {
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "types": [
                {"type": {"name": "electric"}},
            ],
            "stats": [
                {"stat": {"name": "hp"}, "base_stat": 35},
                {"stat": {"name": "attack"}, "base_stat": 55},
                {"stat": {"name": "defense"}, "base_stat": 40},
            ],
            "sprites": {
                "front_default": "https://example.com/front.png",
                "other": {
                    "official-artwork": {
                        "front_default": "https://example.com/art.png",
                    }
                },
            },
        }

        transformed = transform_record(record)

        self.assertEqual(transformed["name"], "pikachu")
        self.assertEqual(transformed["height"], 4)
        self.assertEqual(transformed["weight"], 60)
        self.assertEqual(transformed["types"], ["electric"])
        self.assertEqual(
            transformed["stats"],
            {"hp": 35, "attack": 55, "defense": 40},
        )
        self.assertEqual(transformed["image"], "https://example.com/art.png")


class ComputeSummaryTests(unittest.TestCase):
    def test_compute_summary_aggregates_team_metrics(self) -> None:
        team = [
            {
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "types": ["electric"],
                "stats": {"hp": 35, "attack": 55, "defense": 40},
                "image": "x",
            },
            {
                "name": "charizard",
                "height": 17,
                "weight": 905,
                "types": ["fire", "flying"],
                "stats": {"hp": 78, "attack": 84, "defense": 78},
                "image": "y",
            },
        ]

        summary = compute_summary(team)

        self.assertEqual(summary["total_weight"], 965)
        self.assertEqual(summary["average_height"], 10.5)
        self.assertEqual(summary["total_hp"], 113)
        self.assertEqual(
            summary["type_counts"],
            {"electric": 1, "fire": 1, "flying": 1},
        )


if __name__ == "__main__":
    unittest.main()
