import curses

from curitz.culistbox import listbox, BoxSize, BoxElement


class demoplugin1():
    def __init__(self):
        self.description = "Demoplugin"

    def action(self, screen, case):
        try:
            #     listbox(nlines, ncols, startx, starty)
            box = listbox(9, 100, 4, 9)
            box.add(case.__repr__())
            box.heading = "Nizebox :)"

            box.draw()
            screen.noutrefresh()
            curses.doupdate()

            while True:
                x = screen.getch()
                if x == -1:
                    pass
                elif x == curses.KEY_UP:
                    # Move up one element in list
                    if box.active_element > 0:
                        box.active_element -= 1

                elif x == curses.KEY_DOWN:
                    # Move down one element in list
                    if box.active_element < len(box) - 1:
                        box.active_element += 1

                elif x == curses.KEY_ENTER or x == 13 or x == 10:
                    pass
                elif x == 27 or x == ord('q') or x == ord('Q'):  # ESC and Q
                    raise KeyboardInterrupt("ESC pressed")

                box.draw()
                curses.doupdate()
        except KeyboardInterrupt:
            box.clear()
