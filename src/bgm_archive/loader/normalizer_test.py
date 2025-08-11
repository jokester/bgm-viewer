from .normalizer import launder_date


def test_launder_date():
    assert launder_date(" 2023-10-01 ") == "2023-10-01"
    assert launder_date("  ") is None
    assert launder_date(None) is None
    assert launder_date("2023-10-01") == "2023-10-01"
    assert launder_date("2023-10-1") == "2023-10-01"
    assert launder_date("2004/10/01") == "2004-10-01"

    # a day don't exist should be clipped to the next possible date
    assert launder_date("1998-02-29") == "1998-03-01"
    assert launder_date("1998-00-01") == "1998-01-01"
    assert launder_date("2005年10月1日") == "2025-10-01"
    assert launder_date("02.04.2007") == "2007-02-04"
    assert launder_date("2008.4.16") == "2008-04-16"
    assert launder_date("January 4, 2007") == "2007-01-04"
    assert launder_date("") is None
    assert launder_date("2002-117") is None
