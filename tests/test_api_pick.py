"""Contract tests for POST /api/pick."""

import json

import pytest


API_PATH = "/api/pick"


def candidate(candidate_id, name):
    return {"id": candidate_id, "name": name}


def assert_json_response(response, expected_status):
    assert response.status_code == expected_status
    assert response.content_type.startswith("application/json")
    assert response.is_json
    return response.get_json()


def assert_error_response(response, expected_status, expected_code):
    payload = assert_json_response(response, expected_status)
    assert set(payload) == {"error"}

    error = payload["error"]
    assert isinstance(error, dict)
    assert error.get("code") == expected_code
    assert isinstance(error.get("message"), str)
    assert error["message"].strip()

    if "details" in error:
        assert isinstance(error["details"], list)
        for detail in error["details"]:
            assert isinstance(detail, dict)
            assert isinstance(detail.get("field"), str)
            assert detail["field"].strip()
            assert isinstance(detail.get("reason"), str)
            assert detail["reason"].strip()


def assert_success_response(response, candidates, expected_count):
    payload = assert_json_response(response, 200)
    assert set(payload) == {"picked", "candidate_count"}
    assert payload["candidate_count"] == len(candidates)
    assert isinstance(payload["picked"], list)
    assert len(payload["picked"]) == expected_count

    candidates_by_id = {item["id"]: item["name"] for item in candidates}
    picked_ids = []
    for picked in payload["picked"]:
        assert set(picked) == {"id", "name"}
        assert picked["id"] in candidates_by_id
        assert picked["name"] == candidates_by_id[picked["id"]]
        picked_ids.append(picked["id"])

    assert len(picked_ids) == len(set(picked_ids))
    return payload


def test_pick_returns_requested_number_of_unique_candidates(client):
    candidates = [
        candidate("student-001", "Ada"),
        candidate("student-002", "Linus"),
        candidate("student-003", "Grace"),
    ]

    response = client.post(API_PATH, json={"candidates": candidates, "count": 2})

    assert_success_response(response, candidates, expected_count=2)


def test_pick_defaults_count_to_one(client):
    candidates = [
        candidate("student-001", "Ada"),
        candidate("student-002", "Linus"),
    ]

    response = client.post(API_PATH, json={"candidates": candidates})

    assert_success_response(response, candidates, expected_count=1)


def test_pick_allows_duplicate_names_when_ids_are_unique(client):
    candidates = [
        candidate("student-001", "Alex"),
        candidate("student-002", "Alex"),
    ]

    response = client.post(API_PATH, json={"candidates": candidates, "count": 2})

    assert_success_response(response, candidates, expected_count=2)


def test_pick_ignores_unknown_fields(client):
    candidates = [candidate("student-001", "Ada")]
    request_body = {
        "candidates": [
            {"id": "student-001", "name": "Ada", "group": "A"},
        ],
        "count": 1,
        "request_id": "example-request",
    }

    response = client.post(API_PATH, json=request_body)

    assert_success_response(response, candidates, expected_count=1)


def test_pick_accepts_id_and_name_at_maximum_length(client):
    candidates = [candidate("i" * 64, "n" * 50)]

    response = client.post(API_PATH, json={"candidates": candidates, "count": 1})

    assert_success_response(response, candidates, expected_count=1)


@pytest.mark.parametrize(
    "request_body",
    [
        {},
        {"candidates": None},
        {"candidates": "not-a-list"},
        {"candidates": []},
        {"candidates": [candidate(f"student-{index:03d}", "Name") for index in range(101)]},
        {"candidates": [None]},
        {"candidates": [{"name": "Ada"}]},
        {"candidates": [{"id": "student-001"}]},
        {"candidates": [candidate(1, "Ada")]},
        {"candidates": [candidate("student-001", 1)]},
        {"candidates": [candidate(" ", "Ada")]},
        {"candidates": [candidate("student-001", " ")]},
        {"candidates": [candidate("x" * 65, "Ada")]},
        {"candidates": [candidate("student-001", "x" * 51)]},
        {
            "candidates": [
                candidate("student-001", "Ada"),
                candidate("student-001", "Grace"),
            ]
        },
        {
            "candidates": [
                candidate("student-001", "Ada"),
                candidate(" student-001 ", "Grace"),
            ]
        },
        {"candidates": [candidate("student-001", "Ada")], "count": None},
        {"candidates": [candidate("student-001", "Ada")], "count": -1},
        {"candidates": [candidate("student-001", "Ada")], "count": 0},
        {"candidates": [candidate("student-001", "Ada")], "count": 2},
        {"candidates": [candidate("student-001", "Ada")], "count": 1.5},
        {"candidates": [candidate("student-001", "Ada")], "count": True},
        {"candidates": [candidate("student-001", "Ada")], "count": "1"},
    ],
    ids=[
        "missing-candidates",
        "null-candidates",
        "candidates-not-array",
        "empty-candidates",
        "too-many-candidates",
        "candidate-not-object",
        "missing-id",
        "missing-name",
        "id-not-string",
        "name-not-string",
        "blank-id",
        "blank-name",
        "id-too-long",
        "name-too-long",
        "duplicate-id",
        "duplicate-id-after-trimming",
        "count-null",
        "count-negative",
        "count-zero",
        "count-greater-than-candidates",
        "count-float",
        "count-boolean",
        "count-string",
    ],
)
def test_pick_rejects_invalid_request_fields(client, request_body):
    response = client.post(API_PATH, json=request_body)

    assert_error_response(response, 422, "VALIDATION_ERROR")


def test_pick_rejects_invalid_json(client):
    response = client.post(
        API_PATH,
        data='{"candidates": [',
        content_type="application/json",
    )

    assert_error_response(response, 400, "INVALID_JSON")


def test_pick_accepts_valid_raw_json(client):
    candidates = [candidate("student-001", "Ada")]
    response = client.post(
        API_PATH,
        data=json.dumps({"candidates": candidates}),
        content_type="application/json",
    )

    assert_success_response(response, candidates, expected_count=1)
