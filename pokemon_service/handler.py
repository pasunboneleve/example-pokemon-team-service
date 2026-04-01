from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"
DEFAULT_IMAGE_URL = ""


class BadRequestError(ValueError):
    """Raised when the names query parameter is missing or invalid."""


class UnknownPokemonError(Exception):
    """Raised when one or more requested Pokemon are not found."""

    def __init__(self, unknown_names: list[str]) -> None:
        super().__init__("Unknown pokemon requested.")
        self.unknown_names = unknown_names


@dataclass(frozen=True)
class RuntimeDependencies:
    base_url: str = POKEAPI_BASE_URL


def parse_names(raw_names: str | None) -> list[str]:
    if raw_names is None:
        raise BadRequestError("The names query parameter is required.")

    names = [name.strip().lower() for name in raw_names.split(",") if name.strip()]
    if not names:
        raise BadRequestError("The names query parameter must contain at least one name.")
    return names


def fetch_pokemon(name: str, deps: RuntimeDependencies) -> dict[str, Any]:
    url = f"{deps.base_url}/{parse.quote(name)}"
    try:
        with request.urlopen(url, timeout=10) as response:
            return json.load(response)
    except error.HTTPError as exc:
        if exc.code == 404:
            raise UnknownPokemonError([name]) from exc
        raise


def transform_record(record: dict[str, Any]) -> dict[str, Any]:
    stats_by_name = {
        stat["stat"]["name"]: stat["base_stat"]
        for stat in record.get("stats", [])
    }
    image = (
        record.get("sprites", {})
        .get("other", {})
        .get("official-artwork", {})
        .get("front_default")
        or record.get("sprites", {}).get("front_default")
        or DEFAULT_IMAGE_URL
    )

    return {
        "name": record["name"],
        "height": record["height"],
        "weight": record["weight"],
        "types": [entry["type"]["name"] for entry in record.get("types", [])],
        "stats": {
            "hp": stats_by_name.get("hp", 0),
            "attack": stats_by_name.get("attack", 0),
            "defense": stats_by_name.get("defense", 0),
        },
        "image": image,
    }


def compute_summary(team: list[dict[str, Any]]) -> dict[str, Any]:
    total_weight = sum(member["weight"] for member in team)
    total_height = sum(member["height"] for member in team)
    total_hp = sum(member["stats"]["hp"] for member in team)
    type_counts = Counter(
        pokemon_type
        for member in team
        for pokemon_type in member["types"]
    )

    average_height = total_height / len(team)

    return {
        "total_weight": total_weight,
        "average_height": average_height,
        "total_hp": total_hp,
        "type_counts": dict(sorted(type_counts.items())),
    }


def build_http_response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "access-control-allow-origin": "*",
        },
        "body": json.dumps(payload),
    }


def build_team_response(names: list[str], deps: RuntimeDependencies) -> dict[str, Any]:
    team: list[dict[str, Any]] = []
    unknown_names: list[str] = []

    for name in names:
        try:
            record = fetch_pokemon(name, deps)
        except UnknownPokemonError as exc:
            unknown_names.extend(exc.unknown_names)
            continue

        team.append(transform_record(record))

    if unknown_names:
        raise UnknownPokemonError(unknown_names)

    return {
        "team": team,
        "summary": compute_summary(team),
    }


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    path = event.get("rawPath", "/")
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

    if path != "/pokemon/team" or method != "GET":
        return build_http_response(404, {"error": "Not found"})

    raw_names = (event.get("queryStringParameters") or {}).get("names")
    deps = RuntimeDependencies()

    try:
        names = parse_names(raw_names)
        payload = build_team_response(names, deps)
    except BadRequestError as exc:
        return build_http_response(400, {"error": str(exc)})
    except UnknownPokemonError as exc:
        return build_http_response(
            404,
            {
                "error": "One or more pokemon were not found.",
                "unknown_names": exc.unknown_names,
            },
        )
    except error.URLError:
        return build_http_response(502, {"error": "Failed to reach PokeAPI."})

    return build_http_response(200, payload)
