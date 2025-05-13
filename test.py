from typing import Optional

class Game:
    def __init__(self, rows: int, cols: int, field_contents: Optional[list[list[str]]] = None):
        self.rows = rows
        self.cols = cols
        if field_contents == None:
            self.field = [[" " for i in range(cols)] for a in range(rows)]
        else:
            self.field = field_contents
        self.faller = None
            #pass

    def show_field(self) -> list[str]:
        lines = []
        for r in range(self.rows):
            line = "|"
            for c in range(self.cols):
                cell_output = "   "
                cell = self.field[r][c]
                if self.faller and self.faller["state"] != "frozen":
                    faller_col = self.faller["col"]
                    faller_row = self.faller["row"]
                    faller_state = self.faller["state"]
                    color1, color2 = self.faller["colors"]
                    
                    if self.faller["orientation"] == "vertical" and c == faller_col and r in (faller_row-1, faller_row):
                        color = color1 if r == faller_row-1 else color2
                        if faller_state == "falling" or "landed":
                            cell_output = f"|{color}|"
                        else:
                            cell_output = f" {color} "
                    elif self.faller["orientation"] == "horizontal" and r == faller_row and c in (faller_col, faller_col+1):
                        color = color1 if c == faller_col else color2
                        if c == faller_col:  # Left side of faller
                            if faller_state == "falling":
                                cell_output = f"[{color}--"
                            elif faller_state == "landed":
                                cell_output = f"|{color}--"
                            elif faller_state == "frozen":
                                cell_output = f" {color}--"
                        elif c == faller_col + 1:   # Right side of faller
                            if faller_state == "falling":
                                cell_output = f"{color}]"
                            elif faller_state == "landed":
                                cell_output = f"{color}|"
                            elif faller_state == "frozen":
                                cell_output = f"{color} "
                if cell_output == "   ":
                    if cell in ("R", "Y", "B"):
                        left = (c > 0 and self.field[r][c-1] in ("R", "Y", "B"))
                        right = (c + 1 < self.cols and self.field[r][c+1] in ("R", "Y", "B"))
                        if right and not left:
                            cell_output = f" {cell}-"
                        elif left and not right:
                            cell_output = f"-{cell} "
                        else:
                            cell_output = f" {cell} "
                    elif cell in ("r", "y", "b"):
                        cell_output = f" {cell} "
                line += cell_output
            line += "|"
            lines.append(line)
        lines.append(" " + "-" * (self.cols * 3) + " ")
        if self.level_cleared():
            lines.append("LEVEL CLEARED")
        return lines

    def move_left(self) -> None:
        if not self.faller or self.faller["state"] == "frozen":
            return
        r = self.faller["row"]
        c = self.faller["col"]
        orientation = self.faller["orientation"]
        if orientation == "horizontal":
            target_c = c - 1
            if target_c < 0 or self.field[r][target_c] != " ":
                return
            self.faller["col"] = target_c
        else:
            target_c = c - 1
            if target_c < 0 or self.field[r][target_c] != " " or self.field[r-1][target_c] != " ":
                return
            self.faller["col"] = target_c
        if self.faller["state"] == "landed":
            below = r + 1
            if below < self.rows and (self.field[below][self.faller["col"]] == " " and (orientation == "vertical" or self.field[below][self.faller["col"] + 1] == " ")):
                self.faller["state"] = "falling"

    def move_right(self) -> None:
        if not self.faller or self.faller["state"] == "frozen":
            return
        r = self.faller["row"]
        c = self.faller["col"]
        orientation = self.faller["orientation"]
        target_c = c + 1
        if orientation == "horizontal":
            if target_c + 1 >= self.cols or self.field[r][target_c + 1] != " ":
                return
            self.faller["col"] = target_c
        else:
            if target_c >= self.cols or self.field[r][target_c] != " " or self.field[r-1][target_c] != " ":
                return
            self.faller["col"] = target_c
        if self.faller["state"] == "landed":
            below = r + 1
            if below < self.rows and (self.field[below][self.faller["col"]] == " " and (orientation == "vertical" or self.field[below][self.faller["col"] + 1] == " ")):
                    self.faller["state"] = "falling"

    def rotate_clockwise(self) -> None:
        if not self.faller or self.faller["state"] == "frozen":
            return
        row, col = self.faller["row"], self.faller["col"]
        orientation = self.faller["orientation"]
        left, right = self.faller["colors"]
        if orientation == "horizontal":
            if row - 1 < 0 or self.field[row-1][col] != " ":
                return
            self.faller["orientation"] = "vertical"
        else:
            if col + 1 < self.cols and self.field[row][col+1] == " ":
                self.faller["orientation"] = "horizontal"
                self.faller["colors"] = [right, left]
            elif col - 1 >= 0 and self.field[row][col - 1] == " ":
                self.faller["col"] = col - 1
                self.faller["orientation"] = "horizontal"
                self.faller["colors"] = [right, left]
            else:
                return

    def rotate_counter_clockwise(self) -> None:
        if not self.faller or self.faller["state"] == "frozen":
            return
        for i in range(3):
            self.rotate_clockwise()

    def fall(self, color1: str, color2: str) -> None:
        if self.faller and self.faller["state"] == "frozen":
            r, c = self.faller["row"], self.faller["col"]
            col1, col2 = self.faller["colors"]
            self.field[r][c] = col1
            self.field[r][c+1] = col2
            self.faller = None
        middle = (self.cols - 1) // 2
        if ((self.field[0][middle] != " ") or (self.field[1][middle] != " ") or (self.field[1][middle + 1] != " ")):
            return
        self.faller = {"row": 1,
        "col": middle,
        "colors": [color1, color2],
        "orientation": "horizontal",
        "state": "falling"}
    def tick(self) -> None:
        if not self.faller:
            return
        state = self.faller["state"]
        r = self.faller["row"]
        c = self.faller["col"]
        orientation = self.faller["orientation"]
        if state == "falling":
            '''below = r + 1
            both_empty = (below < self.rows and self.field[below][c] == " " and self.field[below][c+1] == " ")
            if both_empty:
                self.faller["row"] = below
                if below == self.rows - 1:
                    self.faller["state"] = "landed"
            else:
                self.faller["state"] = "landed"'''
            if self._will_land():
                self.faller["state"] = "landed"
            else:
                self.faller["row"] += 1
        elif state == "landed":
            self.faller["state"] = "frozen"
        elif state == "frozen":
            color1, color2 = self.faller["colors"]
            if orientation == "horizontal":
                self.field[r][c] = color1
                self.field[r][c+1] = color2
            else:
                self.field[r-1][c] = color1
                self.field[r][c] = color2
            self.faller = None
            for row in range(self.rows - 3, -1, -1):
                if (self.field[row][c]     in ("R","Y","B") and
                    self.field[row + 1][c] in ("R","Y","B") and
                    self.field[row + 2][c] == " "):
                    # pull both down one
                    top = self.field[row][c]
                    bottom = self.field[row+1][c]
                    self.field[row+2][c] = bottom
                    self.field[row+1][c] = top
                    self.field[row][c] = " "
                    return
    def game_over(self) -> bool:
        pass

    def _will_land(self) -> bool:
        r = self.faller["row"]
        c = self.faller["col"]
        orientation = self.faller["orientation"]
        if orientation == "horizontal":
            below = r + 1
            if below >= self.rows:
                return True
            return self.field[below][c] != " " or self.field[below][c+1] != " "
        elif orientation == "vertical":
            below = r + 1
            if below >= self.rows:
                return True
            return self.field[below][c] != " "
    def level_cleared(self) -> bool:
        for row in self.field:
            for cell in row:
                if cell in ("r", "y", "b"):
                    return False
        return True

