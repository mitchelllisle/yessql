from yessql import NamedParams, NamedParamsList


def test_named_params():
    vals = {'a': 3, 'b': 2, 'c': 1}
    params = NamedParams(vals)
    assert params['a'] == '1'
    assert params['b'] == '2'
    assert params['c'] == '3'


def test_query_generator():
    query = 'select * from test table column = ${foo} and column_two = ${bar}'
    params = NamedParams(foo='hello', bar='world')

    parsed = query.format_map(params)
    assert parsed == 'select * from test table column = $1 and column_two = $2'
    assert '{' not in parsed
    assert '}' not in parsed


def test_params_tuple():
    params = NamedParams(foo='hello', bar='world')
    assert params.as_tuple == ('hello', 'world')


def test_write_generator():
    query = 'insert into test table values (${foo}, ${bar})'
    params = NamedParamsList([dict(foo='hello', bar='world'), dict(foo='foo', bar='bar')])

    parsed = params.format_map(query)
    assert parsed == 'insert into test table values ($2, $1)'
    assert '{' not in parsed
    assert '}' not in parsed
