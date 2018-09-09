from ..card import encode, decode, is_set


def test_encode_decode():
    assert decode(0) == [0] * 4
    assert decode(80) == [2] * 4
    assert decode(encode([2, 1, 0, 1])) == [2, 1, 0, 1]


def test_is_set():
    assert is_set([0, 1, 2])
    assert not is_set([0, 0, 0])
    assert not is_set([0, 0, 1])
    assert not is_set([0, 1, 3])
    assert not is_set([-1, -2, -3])
