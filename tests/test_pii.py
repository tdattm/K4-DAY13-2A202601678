from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd() -> None:
    out = scrub_text("My CCCD is 012345678901.")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card() -> None:
    cards = (
        "1234567812345678",
        "1234 5678 1234 5678",
        "1234-5678-1234-5678"
    )
    for card in cards:
        out = scrub_text(f"Card: {card}")
        assert card not in out
        assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport() -> None:
    out = scrub_text("My passport is B1234567.")
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT" in out


def test_scrub_event_dict() -> None:
    from app.logging_config import scrub_event
    event_dict = {
        "event": "Error with 0901234567",
        "payload": {
            "detail": "Email is test@vinuni.edu.vn",
            "nested": ["B1234567"]
        },
        "latency_ms": 120,
        "is_ok": True
    }
    result = scrub_event(None, None, event_dict)
    assert "0901234567" not in result["event"]
    assert "REDACTED_PHONE_VN" in result["event"]
    assert "test@vinuni.edu.vn" not in result["payload"]["detail"]
    assert "REDACTED_EMAIL" in result["payload"]["detail"]
    assert "B1234567" not in result["payload"]["nested"][0]
    assert "REDACTED_PASSPORT" in result["payload"]["nested"][0]
    assert result["latency_ms"] == 120
    assert result["is_ok"] is True

