from dls_motorhome import HelloClass, say_hello_lots


def test_hello_class_formats_greeting() -> None:
    inst = HelloClass("person")
    assert inst.format_greeting() == "Hello person"


def test_hello_lots_defaults(capsys) -> None:
    say_hello_lots()
    captured = capsys.readouterr()
    assert captured.out == "Hello me\n" * 5
    assert captured.err == ""
