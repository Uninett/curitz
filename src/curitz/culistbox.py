import curses
from typing import NamedTuple, List
import logging

log = logging.getLogger("cuRitz")


BoxSize = NamedTuple("BoxSize", [("height", int), ("length", int)])
BoxElement = NamedTuple("BoxElement", [("id", int), ("text", str), ("font_args", List)])


def get_pagination_indexes(page_size, page_number):
    start_index = page_size * page_number
    end_index = start_index + page_size
    return start_index, end_index


class listbox:
    """
    Create a curses lixtbox.
    Based on code from:
    https://stackoverflow.com/questions/30828804/how-to-make-a-scrolling-menu-in-python-curses
    """

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

        self.active_element = 0
        self.lr_border = lr_border

        self.elements = []  # Type: List[BoxElement]

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

        if not self.elements:
            self.box.noutrefresh()
            return

        # Get current page
        page_number = self.active_element // self.pagesize
        # Protect against mutation by working on a copy
        page_start, page_end = get_pagination_indexes(self.pagesize, page_number)

        # Run until screen is full of elements or we are at the bottom of list
        for i, raw_element in enumerate(self.elements[page_start:page_end]):
            position = page_number * self.pagesize + i

            if isinstance(raw_element, BoxElement):
                curr_element = raw_element
            elif isinstance(raw_element, str):
                curr_element = BoxElement(position, raw_element, [])
            else:
                raise ValueError("LogLine is not a string or BoxElement")

            ar = ""
            c = (
                curr_element.font_args
                if curr_element.font_args
                else [self.normalText]
            )
            start_at = 1
            if position + page_start == self.active_element + page_start:
                # This is the current active element
                if self.arrow:
                    ar = self.arrow
                    start_at = 0
                else:
                    c = [self.highlightText]
            # Print the line

            self.box.addstr(
                position + 1 - page_start,
                start_at,
                "{}{}".format(
                    ar,
                    (curr_element.text)[0 : self.size.length - 2].ljust(
                        self.size.length - 2
                    ),
                ),
                *c
            )

            if (
                position == len(self) - 1
            ):  # Len(self) returns the current length of the list
                break

        self.box.noutrefresh()

    def __len__(self):
        return len(self.elements)

    @property
    def active(self):
        return self.elements[self.active_element]

    def add(self, element: BoxElement):
        self.elements.append(element)

    def clear(self):
        self.elements = []

    def select_next(self):
        pass

    def select_prev(self):
        pass

    def resize(self, nlines, ncols):
        self.box.resize(nlines, ncols)
        self.size = BoxSize(*self.box.getmaxyx())
