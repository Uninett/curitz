"""Guards the listbox cursor invariant behind issue #3.

The row list is replaced by cli.py on every rebuild, which happens on any model
change and unconditionally every ten seconds, so the cursor has to stay valid
across a list that changes under it, and has to stay where the operator put it
when the same rows come back.
"""

from curitz.culistbox import BoxElement, BoxSize, listbox


class TestActiveElement:
    def test_when_the_list_is_empty_it_should_be_zero(self):
        box = make_listbox(rows=0)

        assert box.active_element == 0

    def test_when_set_beyond_the_end_it_should_clamp_to_the_last_row(self):
        box = make_listbox(rows=5)

        box.active_element = 99

        assert box.active_element == 4

    def test_when_set_to_a_negative_index_it_should_clamp_to_the_first_row(self):
        box = make_listbox(rows=5)

        box.active_element = -3

        assert box.active_element == 0

    def test_when_the_list_shrinks_under_it_it_should_clamp_to_the_last_row(self):
        box = make_listbox(rows=100)
        box.active_element = 50

        del box.elements[10:]

        assert box.active_element == 9

    def test_when_set_past_the_end_it_should_not_move_when_rows_arrive(self):
        box = make_listbox(rows=10)

        box.active_element = 99
        box.add(BoxElement(10, "a new case", []))

        assert box.active_element == 9

    def test_when_the_list_is_emptied_under_it_it_should_be_zero(self):
        box = make_listbox(rows=100)
        box.active_element = 50

        box.elements = []

        assert box.active_element == 0


class TestActive:
    def test_when_the_list_is_empty_it_should_be_none(self):
        box = make_listbox(rows=0)

        assert box.active is None

    def test_when_the_list_is_emptied_under_the_cursor_it_should_be_none(self):
        box = make_listbox(rows=10)
        box.active_element = 5

        box.clear()

        assert box.active is None

    def test_when_the_cursor_is_on_a_row_it_should_be_that_row(self):
        box = make_listbox(rows=10)

        box.active_element = 3

        assert box.active.id == 3

    def test_when_the_list_shrinks_under_the_cursor_it_should_be_the_last_row(self):
        box = make_listbox(rows=100)
        box.active_element = 50

        del box.elements[10:]

        assert box.active.id == 9


class TestLastRowIndex:
    def test_when_the_list_is_empty_it_should_be_minus_one(self):
        assert make_listbox(rows=0).last_row_index == -1

    def test_when_the_list_has_rows_it_should_index_the_final_one(self):
        assert make_listbox(rows=7).last_row_index == 6


def make_rows(count):
    """Build `count` rows, each carrying its own index as its case id.

    :param count: number of rows wanted
    :return: a list of BoxElements
    """
    return [BoxElement(i, "row {}".format(i), []) for i in range(count)]


def make_listbox(rows, height=12, length=80):
    """Build a listbox without a curses screen.

    `listbox.__init__` calls `curses.newwin()`, which needs an initialised
    terminal, so the parts of the class that are pure list arithmetic are
    otherwise untestable.  Only the attributes those parts read are set here.

    :param rows: number of elements to fill the list with
    :param height: height of the box, which decides its page size
    :param length: width of the box
    :return: a listbox holding `rows` elements, with the cursor on the first
    """
    box = listbox.__new__(listbox)
    box.size = BoxSize(height=height, length=length)
    box.elements = make_rows(rows)
    box.active_element = 0
    return box


class FakeWindow:
    """The handful of curses window calls draw() makes.

    Stands in for a curses window, which cannot be created without a terminal.

    :ivar rows: the (y, text, attrs) written, in the order they were written
    """

    def __init__(self):
        self.rows = []

    def addstr(self, y, x, text, *attrs):
        self.rows.append((y, text, attrs))

    def erase(self):
        self.rows = []

    def border(self, *args):
        pass

    def noutrefresh(self):
        pass
