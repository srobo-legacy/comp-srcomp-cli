
import mock
import sys

from sr.comp.cli.deploy import query, query_bool

input_name = 'sr.comp.cli.deploy.get_input'

@mock.patch(input_name, lambda x: 'nope')
def test_query_with_default_nope():
    res = query('Question?', ('a'), default='a')
    assert res == 'a'

@mock.patch(input_name, lambda x: 'a')
def test_query_with_default_a():
    res = query('Question?', ('a', 'b'), default='b')
    assert res == 'a'

@mock.patch(input_name)
def test_query_nope_then_a(mock_get_input):
    values = ['nope', 'a']
    mock_get_input.side_effect = lambda x: values.pop(0)

    res = query('Question?', ('a', 'b'))
    assert res == 'a'

    assert mock_get_input.call_count == 2


@mock.patch(input_name, lambda x: 'y')
def test_query_bool_True_y():
    res = query_bool('Question?', True)
    assert res == True

@mock.patch(input_name, lambda x: 'n')
def test_query_bool_True_n():
    res = query_bool('Question?', True)
    assert res == False

@mock.patch(input_name, lambda x: 'other')
def test_query_bool_True_other():
    res = query_bool('Question?', True)
    assert res == True


@mock.patch(input_name, lambda x: 'y')
def test_query_bool_False_y():
    res = query_bool('Question?', False)
    assert res == True

@mock.patch(input_name, lambda x: 'n')
def test_query_bool_False_n():
    res = query_bool('Question?', False)
    assert res == False

@mock.patch(input_name, lambda x: 'other')
def test_query_bool_False_other():
    res = query_bool('Question?', False)
    assert res == False


@mock.patch(input_name, lambda x: 'y')
def test_query_bool_no_default_y():
    res = query_bool('Question?')
    assert res == True

@mock.patch(input_name, lambda x: 'n')
def test_query_bool_no_default_n():
    res = query_bool('Question?')
    assert res == False

@mock.patch(input_name)
def test_query_bool_no_default_other_then_y(mock_get_input):
    values = ['other', 'y']
    mock_get_input.side_effect = lambda x: values.pop(0)

    res = query_bool('Question?')
    assert res == True

    assert mock_get_input.call_count == 2
