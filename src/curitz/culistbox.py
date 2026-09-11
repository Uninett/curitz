import curses
from typing import NamedTuple, List
import logging

log = logging.getLogger("cuRitz")


BoxSize = NamedTuple("BoxSize", [("height", int), ("length", int)])
BoxElement = NamedTuple("BoxElement", [("id", int), ("text", str), ("font_args", List)])


class listbox:
    """
    Create a curses lixtbox.
    Based on code from:
    https://stackoverflow.com/questions/30828804/how-to-make-a-scrolling-menu-in-python-curses
    """

    _active_element = 0

    # Shown in place of the rows when there are none.  Left empty by default:
    # a box with nothing in it yet is not the same as one with nothing to show,
    # and only the owner of the box knows which of the two it is looking at.
    empty_message = ""

    def __init__(
        self,
        nlines,
        ncols,
        begin_y=0,
        begin_x=0,
        current_selected_arrow="",
        lr_border=True,
    ):
        self.box = curses.newwin(nlines, ncols, begin_y, begin_x)
        self.size = BoxSize(*self.box.getmaxyx())
        self.highlightText = curses.color_pair(1)
        self.normalText = curses.A_NORMAL
        self.heading = ""
        self.arrow = current_selected_arrow

        self.elements: list[BoxElement | str] = []
        self.active_element = 0
        self.lr_border = lr_border

    @property
    def pagesize(self):
        return self.size.height - 2

    def draw(self):
        self.box.erase()
        if not self.lr_border:
            pass
            self.box.border(
                " ",
                " ",
                curses.ACS_HLINE,
                curses.ACS_HLINE,
                curses.ACS_HLINE,
                curses.ACS_HLINE,
                curses.ACS_HLINE,
                curses.ACS_HLINE,
            )
        else:
            self.box.border()
        self.box.addstr(0, 1, self.heading)

        if self.pagesize < 1:
            # The box is too short to hold a single row
            self.box.noutrefresh()
            return

        if not self.elements:
            if self.empty_message:
                self.box.addstr(1, 1, self.empty_message, self.highlightText)
            self.box.noutrefresh()
            return

        page_number = self.active_element // self.pagesize
        page_start, page_end = get_pagination_indexes(self.pagesize, page_number)
        # Draw from a copy of the page.  Slicing also bounds the loop for us, so
        # a page that is short because the list ends mid-way just draws fewer
        # rows instead of running off the end of the list.
        for row, element in enumerate(self.elements[page_start:page_end]):
            index = page_start + row

            if isinstance(element, BoxElement):
                curr_element = element
            elif isinstance(element, str):
                curr_element = BoxElement(index, element, [])
            else:
                raise ValueError("LogLine is not a string or BoxElement")

            ar = ""
            c = curr_element.font_args if curr_element.font_args else [self.normalText]
            start_at = 1
            if index == self.active_element:
                # This is the current active element
                if self.arrow:
                    ar = self.arrow
                    start_at = 0
                else:
                    c = [self.highlightText]
            # Print the line

            self.box.addstr(
                row + 1,
                start_at,
                "{}{}".format(
                    ar,
                    (curr_element.text)[0 : self.size.length - 2].ljust(
                        self.size.length - 2
                    ),
                ),
                *c,
            )

        self.box.noutrefresh()

    def __len__(self):
        return len(self.elements)

    @property
    def last_row_index(self):
        """Index of the final row, or -1 while the list is empty."""
        return len(self) - 1

    @property
    def active_element(self):
        """Index of the row the cursor is on.

        Never points past the end of the current list, so a list that shrinks
        under the cursor cannot leave it invalid.  Rebuilds go through
        set_elements(), which is what carries the cursor across them; the clamp
        here is what makes any other mutation of the row list safe.

        :return: the cursor position, or 0 while the list is empty
        """
        if not self.elements:
            return 0
        return min(self._active_element, self.last_row_index)

    @active_element.setter
    def active_element(self, index):
        self._active_element = max(min(index, self.last_row_index), 0)

    @property
    def active(self):
        """The element the cursor is on.

        Elements are BoxElements or, in the boxes built by the popup windows,
        plain strings.

        :return: the active element, or None while the list is empty
        """
        if not self.elements:
            return None
        return self.elements[self.active_element]

    def go_one_row_up(self) -> None:
        """Move the cursor one row towards the top of the list."""
        self.active_element -= 1

    def go_one_row_down(self) -> None:
        """Move the cursor one row towards the bottom of the list."""
        self.active_element += 1

    def go_one_page_up(self) -> None:
        """Move the cursor one screenful towards the top of the list."""
        self.active_element -= self.pagesize

    def go_one_page_down(self) -> None:
        """Move the cursor one screenful towards the bottom of the list."""
        self.active_element += self.pagesize

    def set_elements(self, elements) -> None:
        """Replace every row, keeping the cursor on the row it was on.

        The cursor is clamped as the rows are replaced, so a rebuild that
        returns the same rows leaves it exactly where the operator put it, and
        one that returns fewer moves it no further up than it has to, without
        remembering a row that no longer exists.

        :param elements: the rows to display
        :return: None
        """
        self.elements = list(elements)
        self.active_element = self._active_element

    def add(self, element: BoxElement):
        self.elements.append(element)

    def clear(self) -> None:
        """Remove every row, and with it the cursor position.

        :return: None
        """
        self.elements = []
        self.active_element = 0

    def resize(self, nlines, ncols):
        self.box.resize(nlines, ncols)
        self.size = BoxSize(*self.box.getmaxyx())


def get_pagination_indexes(page_size, page_number):
    """Find the slice bounds of a page.

    :param page_size: number of rows on a page
    :param page_number: zero-based number of the page wanted
    :return: the (start, end) indexes to slice the element list with
    """
    start_index = page_size * page_number
    end_index = start_index + page_size
    return start_index, end_index
