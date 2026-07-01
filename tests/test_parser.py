from parser.tasks import format_price

def test_format_price_normal():
    raw_price = "40\xa0000 ₽"
    result = format_price(raw_price)
    assert result == ("40 000 ₽")

def test_format_price_empty():
    result = format_price(None)
    assert result == "Цена не указана"
