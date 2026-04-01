from __future__ import annotations

from urllib import error
from unittest.mock import patch

import pytest

from pokemon_service.handler import (
    POKEAPI_USER_AGENT,
    RuntimeDependencies,
    build_team_response,
    compute_summary,
    fetch_pokemon,
    handler,
    parse_names,
    transform_record,
)


def test_parse_names_preserves_duplicates() -> None:
    assert parse_names("pikachu, charizard,pikachu") == [
        "pikachu",
        "charizard",
        "pikachu",
    ]


def test_parse_names_rejects_missing_value() -> None:
    with pytest.raises(ValueError, match="required"):
        parse_names(None)


def test_parse_names_rejects_empty_value() -> None:
    with pytest.raises(ValueError, match="at least one"):
        parse_names(" ,, ")


def test_transform_record_extracts_requested_fields() -> None:
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

    assert transformed["name"] == "pikachu"
    assert transformed["height"] == 4
    assert transformed["weight"] == 60
    assert transformed["types"] == ["electric"]
    assert transformed["stats"] == {"hp": 35, "attack": 55, "defense": 40}
    assert transformed["image"] == "https://example.com/art.png"


def test_fetch_pokemon_sets_explicit_user_agent() -> None:
    with patch("pokemon_service.handler.request.urlopen") as mock_urlopen:
        with patch("pokemon_service.handler.json.load", return_value={"name": "pikachu"}):
            mock_urlopen.return_value.__enter__.return_value = object()

            fetch_pokemon("pikachu", RuntimeDependencies())

    req = mock_urlopen.call_args.args[0]
    assert req.full_url == "https://pokeapi.co/api/v2/pokemon/pikachu"
    assert req.get_header("User-agent") == POKEAPI_USER_AGENT


def test_compute_summary_aggregates_team_metrics() -> None:
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

    assert summary["total_weight"] == 965
    assert summary["average_height"] == 10.5
    assert summary["total_hp"] == 113
    assert summary["type_counts"] == {"electric": 1, "fire": 1, "flying": 1}


def test_compute_summary_rounds_average_height_to_two_decimals() -> None:
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
            "name": "bulbasaur",
            "height": 7,
            "weight": 69,
            "types": ["grass", "poison"],
            "stats": {"hp": 45, "attack": 49, "defense": 49},
            "image": "y",
        },
        {
            "name": "charizard",
            "height": 17,
            "weight": 905,
            "types": ["fire", "flying"],
            "stats": {"hp": 78, "attack": 84, "defense": 78},
            "image": "z",
        },
    ]

    summary = compute_summary(team)

    assert summary["average_height"] == 9.33


def test_root_path_serves_frontend() -> None:
    response = handler(
        {
            "rawPath": "/",
            "queryStringParameters": None,
            "requestContext": {"http": {"method": "GET"}},
        },
        None,
    )

    assert response["statusCode"] == 200
    assert response["headers"]["content-type"] == "text/html; charset=utf-8"
    assert "Pokemon Team Service" in response["body"]


def test_build_team_response_keeps_duplicates() -> None:
    with patch(
        "pokemon_service.handler.fetch_pokemon",
        side_effect=[
            {
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "types": [{"type": {"name": "electric"}}],
                "stats": [
                    {"stat": {"name": "hp"}, "base_stat": 35},
                    {"stat": {"name": "attack"}, "base_stat": 55},
                    {"stat": {"name": "defense"}, "base_stat": 40},
                ],
                "sprites": {"front_default": "https://example.com/pikachu.png"},
            },
            {
                "name": "pikachu",
                "height": 4,
                "weight": 60,
                "types": [{"type": {"name": "electric"}}],
                "stats": [
                    {"stat": {"name": "hp"}, "base_stat": 35},
                    {"stat": {"name": "attack"}, "base_stat": 55},
                    {"stat": {"name": "defense"}, "base_stat": 40},
                ],
                "sprites": {"front_default": "https://example.com/pikachu.png"},
            },
        ],
    ):
        payload = build_team_response(["pikachu", "pikachu"], RuntimeDependencies())

    assert [member["name"] for member in payload["team"]] == ["pikachu", "pikachu"]


def test_handler_returns_502_when_pokeapi_is_unreachable() -> None:
    with patch(
        "pokemon_service.handler.fetch_pokemon",
        side_effect=error.URLError("network down"),
    ):
        response = handler(
            {
                "rawPath": "/pokemon/team",
                "queryStringParameters": {"names": "pikachu"},
                "requestContext": {"http": {"method": "GET"}},
            },
            None,
        )

    assert response["statusCode"] == 502
