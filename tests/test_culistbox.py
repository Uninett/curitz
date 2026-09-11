"""Guards the listbox cursor invariant behind issue #3.

The row list is replaced by cli.py on every rebuild, which happens on any model
change and unconditionally every ten seconds, so the cursor has to stay valid
across a list that changes under it, and has to stay where the operator put it
when the same rows come back.

draw() is covered here too, through a fake curses window, because the crash
these tests exist to prevent used to happen in the middle of a redraw with
nobody touching the keyboard.
"""

from curitz.culistbox import BoxElement, BoxSize, get_pagination_indexes, listbox


class TestGetPaginationIndexes:
    def test_when_asked_for_the_first_page_it_should_start_at_zero(self):
        assert get_pagination_indexes(page_size=10, page_number=0) == (0, 10)

    def test_when_asked_for_a_later_page_it_should_span_that_page(self):
        assert get_pagination_indexes(page_size=10, page_number=3) == (30, 40)


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

    def test_when_moved_past_the_end_it_should_not_move_when_rows_arrive(self):
        box = make_listbox(rows=10)
        box.active_element = 9

        box.go_one_row_down()
        box.add(BoxElement(10, "a new case", []))

        assert box.active_element == 9

    def test_when_the_list_is_rebuilt_under_it_it_should_return_to_the_same_row(self):
        box = make_listbox(rows=100)
        box.active_element = 50

        rebuild(box, rows=100)

        assert box.active_element == 50

    def test_when_a_rebuild_leaves_fewer_rows_it_should_clamp_to_the_last_one(self):
        box = make_listbox(rows=100)
        box.active_element = 50

        rebuild(box, rows=10)

        assert box.active_element == 9

    def test_when_the_list_is_cleared_it_should_be_zero(self):
        box = make_listbox(rows=100)
        box.active_element = 50

        box.clear()

        assert box.active_element == 0

    def test_when_a_rebuild_shrinks_the_list_it_should_not_drift_when_rows_return(self):
        box = make_listbox(rows=100)
        box.active_element = 50

        rebuild(box, rows=10)
        rebuild(box, rows=100)

        assert box.active_element == 9


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


class TestGoOneRowUp:
    def test_when_it_is_on_the_first_row_it_should_stay_there(self):
        box = make_listbox(rows=10)

        box.go_one_row_up()

        assert box.active_element == 0

    def test_when_it_is_further_down_it_should_move_up_one_row(self):
        box = make_listbox(rows=10)
        box.active_element = 4

        box.go_one_row_up()

        assert box.active_element == 3

    def test_when_the_list_is_empty_it_should_leave_the_cursor_at_zero(self):
        box = make_listbox(rows=0)

        box.go_one_row_up()

        assert box.active_element == 0


class TestGoOneRowDown:
    def test_when_it_is_on_the_last_row_it_should_stay_there(self):
        box = make_listbox(rows=10)
        box.active_element = 9

        box.go_one_row_down()

        assert box.active_element == 9

    def test_when_it_is_further_up_it_should_move_down_one_row(self):
        box = make_listbox(rows=10)

        box.go_one_row_down()

        assert box.active_element == 1

    def test_when_the_list_is_empty_it_should_leave_the_cursor_at_zero(self):
        box = make_listbox(rows=0)

        box.go_one_row_down()

        assert box.active_element == 0


class TestGoOnePageUp:
    def test_when_a_full_page_is_above_the_cursor_it_should_move_a_page(self):
        box = make_listbox(rows=100, height=12)  # a page is 10 rows
        box.active_element = 50

        box.go_one_page_up()

        assert box.active_element == 40

    def test_when_less_than_a_page_is_above_the_cursor_it_should_stop_at_the_top(self):
        box = make_listbox(rows=100, height=12)
        box.active_element = 3

        box.go_one_page_up()

        assert box.active_element == 0


class TestGoOnePageDown:
    def test_when_a_full_page_is_below_the_cursor_it_should_move_a_page(self):
        box = make_listbox(rows=100, height=12)  # a page is 10 rows

        box.go_one_page_down()

        assert box.active_element == 10

    def test_when_less_than_a_page_is_below_the_cursor_it_should_stop_at_the_end(self):
        box = make_listbox(rows=100, height=12)
        box.active_element = 97

        box.go_one_page_down()

        assert box.active_element == 99


class TestDraw:
    def test_when_the_list_shrank_under_the_cursor_it_should_draw_the_short_list(self):
        box = make_listbox(rows=100, height=12)
        box.active_element = 55

        del box.elements[3:]
        box.draw()

        assert drawn_text(box) == ["row 0", "row 1", "row 2"]

    def test_when_the_list_is_empty_it_should_show_the_empty_message(self):
        box = make_listbox(rows=0)
        box.empty_message = "Nothing to display"

        box.draw()

        assert drawn_text(box) == ["Nothing to display"]

    def test_when_the_list_is_empty_and_unexplained_it_should_draw_nothing(self):
        box = make_listbox(rows=0)

        box.draw()

        assert drawn_text(box) == []

    def test_when_the_cursor_is_on_a_later_page_it_should_draw_that_page(self):
        box = make_listbox(rows=100, height=12)  # a page is 10 rows

        box.active_element = 55
        box.draw()

        assert drawn_text(box)[0] == "row 50"
        assert [y for y, _, _ in box.box.rows if y > 0] == list(range(1, 11))

    def test_when_the_cursor_is_on_a_later_page_it_should_highlight_the_right_row(self):
        box = make_listbox(rows=100, height=12)

        box.active_element = 55
        box.draw()

        assert highlighted_text(box) == ["row 55"]

    def test_when_the_box_is_too_short_for_a_row_it_should_draw_nothing(self):
        box = make_listbox(rows=100, height=2)  # a page is zero rows

        box.draw()

        assert drawn_text(box) == []


class TestLastRowIndex:
    def test_when_the_list_is_empty_it_should_be_minus_one(self):
        assert make_listbox(rows=0).last_row_index == -1

    def test_when_the_list_has_rows_it_should_index_the_final_one(self):
        assert make_listbox(rows=7).last_row_index == 6


def drawn_text(box):
    """The text of every row draw() wrote, stripped of its padding.

    The heading, which is written to row 0 whether there are rows or not, is
    left out.

    :param box: a listbox built by make_listbox()
    :return: a list of strings, in the order they were drawn
    """
    return [text.strip() for y, text, _ in box.box.rows if y > 0]


def highlighted_text(box):
    """As drawn_text(), but only the rows drawn with the highlight attribute.

    :param box: a listbox built by make_listbox()
    :return: a list of strings, in the order they were drawn
    """
    return [
        text.strip() for y, text, attrs in box.box.rows if y > 0 and HIGHLIGHT in attrs
    ]


def rebuild(box, rows):
    """Replace the box' rows, the way create_case_list() does.

    :param box: the listbox to rebuild
    :param rows: number of rows to refill it with
    :return: None
    """
    box.set_elements(make_rows(rows))


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
    box.box = FakeWindow()
    box.heading = ""
    box.arrow = ""
    box.lr_border = True
    box.empty_message = ""
    box.highlightText = HIGHLIGHT
    box.normalText = NORMAL
    box.elements = make_rows(rows)
    box.active_element = 0
    return box


HIGHLIGHT = "highlighted"
NORMAL = "normal"


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
