from hypothesis import given
import hypothesis.strategies as st

@given(st.lists(st.integers(), unique=True, min_size=1))
def test_take(some_list):
    from helpers import tail
    new_list = tail(some_list)
    assert some_list[0] not in new_list
    assert all([x in new_list for x in some_list[1:]])

@given(st.functions(like=lambda x, y: True, returns=st.booleans()), st.booleans())
def test_partition(predicate, boolean):
    pass    

if __name__ == '__main__':
    test_take()