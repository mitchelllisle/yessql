from yessql import NamedParams


def test_named_params():
    params = NamedParams(a=1, b=2, c=3)
    assert params['a'] == '$1'
    assert params['b'] == '$2'
    assert params['c'] == '$3'


def test_query_generator():
    query = 'select * from test table column = {foo} and column_two = {bar}'
    params = NamedParams(foo='hello', bar='world')

    parsed = query.format_map(params)
    assert parsed == 'select * from test table column = $1 and column_two = $2'
    assert '{' not in parsed
    assert '}' not in parsed


def test_params_tuple():
    params = NamedParams(foo='hello', bar='world')
    assert params.as_tuple == ('hello', 'world')
