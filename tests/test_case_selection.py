"""Guards the rules for which cases a keypress acts on.

The cursor can outlive the case it sits on: poll() drops cases in the same pass
of the key loop that dispatches the keypress, and the case list is not rebuilt
until after the key has been handled.
"""

from curitz.cli import active_case_id, cases_to_act_on
from curitz.culistbox import BoxElement, BoxSize, listbox


class TestCasesToActOn:
    def test_when_cases_are_selected_it_should_be_the_selection(self):
        box = make_listbox(case_ids=[1, 2, 3])

        assert cases_to_act_on(box, cases_by_id(1, 2, 3), [2, 3]) == [2, 3]

    def test_when_nothing_is_selected_it_should_be_the_case_under_the_cursor(self):
        box = make_listbox(case_ids=[1, 2, 3])
        box.active_element = 1

        assert cases_to_act_on(box, cases_by_id(1, 2, 3), []) == [2]

    def test_when_nothing_is_selected_and_the_list_is_empty_it_should_be_empty(self):
        box = make_listbox(case_ids=[])

        assert cases_to_act_on(box, cases_by_id(), []) == []

    def test_when_the_case_under_the_cursor_is_gone_it_should_be_empty(self):
        box = make_listbox(case_ids=[1, 2, 3])
        box.active_element = 1

        assert cases_to_act_on(box, cases_by_id(1, 3), []) == []

    def test_when_a_selected_case_is_gone_it_should_be_dropped(self):
        box = make_listbox(case_ids=[1, 2, 3])

        assert cases_to_act_on(box, cases_by_id(1, 3), [1, 2, 3]) == [1, 3]

    def test_when_case_zero_is_under_the_cursor_it_should_be_acted_on(self):
        box = make_listbox(case_ids=[0, 1])

        assert cases_to_act_on(box, cases_by_id(0, 1), []) == [0]


class TestActiveCaseId:
    def test_when_the_cursor_is_on_a_case_it_should_be_that_case(self):
        box = make_listbox(case_ids=[7, 8, 9])
        box.active_element = 2

        assert active_case_id(box, cases_by_id(7, 8, 9)) == 9

    def test_when_the_list_is_empty_it_should_be_none(self):
        box = make_listbox(case_ids=[])

        assert active_case_id(box, cases_by_id()) is None

    def test_when_the_case_has_been_dropped_since_the_rebuild_it_should_be_none(self):
        box = make_listbox(case_ids=[7, 8, 9])
        box.active_element = 2

        assert active_case_id(box, cases_by_id(7, 8)) is None

    def test_when_case_zero_is_under_the_cursor_it_should_be_zero(self):
        box = make_listbox(case_ids=[0, 1])

        assert active_case_id(box, cases_by_id(0, 1)) == 0


def cases_by_id(*case_ids):
    """Stand in for the module's case dictionary.

    Only the keys matter here; nothing under test looks at the values.

    :param case_ids: the ids the caller wants to exist
    :return: a dict of case id to a placeholder case
    """
    return {caseid: "case {}".format(caseid) for caseid in case_ids}


def make_listbox(case_ids):
    """Build a listbox of case rows without a curses screen.

    `listbox.__init__` needs an initialised terminal; see tests/test_culistbox.py.

    :param case_ids: the case id each row should carry, in display order
    :return: a listbox with the cursor on the first row
    """
    box = listbox.__new__(listbox)
    box.size = BoxSize(height=12, length=80)
    box.elements = [BoxElement(caseid, "row", []) for caseid in case_ids]
    box.active_element = 0
    return box
