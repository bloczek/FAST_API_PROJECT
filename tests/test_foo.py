from fast_api.foo import foo


def test_foo():
    assert foo("foo") == "foo"
