#Liam Kennedy
#lpkenned@uci.edu
#81845142
from typing import Optional
class Game:
    '''Includes all of the states and rules of the Dr. Mario game.'''
    def __init__(self, rows: int, cols: int, field_contents: Optional[list[list[str]]] = None) -> None:
        self.rows = rows
        self.cols = cols
        self.game_over_flag = False
        self.marked_matches = set()
        self.connected_caps = set()
        valid_vars = ("R", "Y", "B")
        if field_contents == None:
            self.field = [[" " for i in range(cols)] for a in range(rows)]
        else:
            self.field = field_contents
        self.faller = None       

    def show_field(self) -> list[str]:
        '''This prints out the whole field and determines what the faller looks like.'''
        lines = []
        for r in range(self.rows):
            line = "|"
            for c in range(self.cols):
                cell_output = "   "
                cell = self.field[r][c]
                if isinstance(cell, str) and len(cell) == 3 and cell.startswith("*") and cell.endswith("*"):
                    cell_output = cell
                if self.faller:
                    faller_col, faller_row = self.faller["col"], self.faller["row"]
                    faller_state = self.faller["state"]
                    color1, color2 = self.faller["colors"]
                    
                    if self.faller["orientation"] == "vertical" and c == faller_col and r in (faller_row-1, faller_row):
                        color = color1 if r == faller_row-1 else color2
                        if faller_state == "falling":
                            cell_output = f"[{color}]"
                        elif faller_state == "landed":
                            cell_output = f"|{color}|"
                        else:
                            cell_output = f" {color} "
                    elif self.faller["orientation"] == "horizontal" and r == faller_row and c in (faller_col, faller_col+1):
                        color = color1 if c == faller_col else color2
                        if c == faller_col:  # Left
                            if faller_state == "falling":
                                cell_output = f"[{color}--"
                            elif faller_state == "landed":
                                cell_output = f"|{color}--"
                            elif faller_state == "frozen":
                                cell_output = f" {color}--"
                        elif c == faller_col + 1:   # Right
                            if faller_state == "falling":
                                cell_output = f"{color}]"
                            elif faller_state == "landed":
                                cell_output = f"{color}|"
                            elif faller_state == "frozen":
                                cell_output = f"{color} "
                if cell_output == "   ":
                    capsule_letters =  ("R", "Y", "B")
                    if isinstance(cell, str) and (cell in capsule_letters or (cell.startswith("*") 
                        and cell.endswith("*") and cell[1] in capsule_letters)):
                        value = cell[1] if cell.startswith("*") and cell.endswith("*") else cell
                        left = (c > 0) and self.is_capsule_connected(r, c, r, c-1)
                        right = (c + 1 < self.cols) and self.is_capsule_connected(r, c, r, c+1)
                        if right and not left:
                            cell_output = f" {value}-"
                        elif left and not right:
                            cell_output = f"-{value} "
                        else:
                            cell_output = f" {value} "
                    elif cell in ("r", "y", "b"):
                        cell_output = f" {cell} "
                line += cell_output
            line += "|"
            lines.append(line)
        lines.append(" " + "-" * (self.cols * 3) + " ")
        if not self.game_over_flag and self.level_cleared():
            lines.append("LEVEL CLEARED")
        return lines

    def is_capsule_piece(self, nr, nc) -> bool:
        '''Checks if the current pieces are separate or connected.'''
        capsule_letters =  ("R", "Y", "B")
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return False
        neighbor = self.field[nr][nc]
        return (neighbor in capsule_letters or (isinstance(neighbor, str) 
        and neighbor.startswith("*") and neighbor.endswith("*") 
        and neighbor[1] in capsule_letters))

    def move_left(self) -> None:
        '''Moves the current faller one cell to the left if possible.'''
        if not self.faller or self.faller["state"] == "frozen":
            return
        r = self.faller["row"]
        c = self.faller["col"]
        orientation = self.faller["orientation"]
        if orientation == "horizontal":
            target_c = c - 1
            if target_c < 0 or target_c + 1 >= self.cols:
                return
            if self.field[r][target_c] != " " or self.field[r][target_c + 1] != " ":
                return
            self.faller["col"] = target_c           
        else:
            target_c = c - 1
            if target_c < 0 or self.field[r][target_c] != " " or self.field[r-1][target_c] != " ":
                return
            self.faller["col"] = target_c
        if self.faller["state"] == "landed":
            below = r + 1
            if below < self.rows and (self.field[below][self.faller["col"]] == " " 
                and (orientation == "vertical" or self.field[below][self.faller["col"] + 1] == " ")):
                self.faller["state"] = "falling"
        if self._will_land():
            self.faller["state"] = "landed"

    def move_right(self) -> None:
        '''Moves the current faller one cell to the right if possible.'''
        if not self.faller or self.faller["state"] == "frozen":
            return
        r = self.faller["row"]
        c = self.faller["col"]
        orientation = self.faller["orientation"]
        target_c = c + 1
        if orientation == "horizontal":
            target_c = c + 1
            if target_c + 1 >= self.cols:
                return
            if self.field[r][target_c] != " " or self.field[r][target_c + 1] != " ":
                return
            self.faller["col"] = target_c
        else:
            if (target_c >= self.cols or self.field[r][target_c] != " " 
                or self.field[r-1][target_c] != " "):
                return
            self.faller["col"] = target_c
        if self.faller["state"] == "landed":
            below = r + 1
            if (below < self.rows and (self.field[below][self.faller["col"]] == " " 
                and (orientation == "vertical" 
                or self.field[below][self.faller["col"] + 1] == " "))):
                    self.faller["state"] = "falling"
        if self._will_land():
            self.faller["state"] = "landed"

    def rotate_clockwise(self) -> None:
        '''Rotates the current faller 90 degrees clockwise with implementation of the wall-kick if necessary.'''
        if not self.faller or self.faller["state"] == "frozen":
            return
        row, col = self.faller["row"], self.faller["col"]
        orientation = self.faller["orientation"]
        color1, color2 = self.faller["colors"]
        if orientation == "horizontal":
            if row - 1 < 0 or self.field[row-1][col] != " ":
                return
            self.faller["orientation"] = "vertical"
        else:
            if col + 1 < self.cols and self.field[row][col+1] == " ":
                self.faller["orientation"] = "horizontal"
                self.faller["colors"] = [color2, color1]
            elif col - 1 >= 0 and self.field[row][col - 1] == " ":
                self.faller["col"] = col - 1
                self.faller["orientation"] = "horizontal"
                self.faller["colors"] = [color2, color1]
            else:
                return
        if self.faller["state"] == "falling" and self._will_land():
            self.faller["state"] = "landed"

    def rotate_counter_clockwise(self) -> None:
        '''Rotates the current faller 90 degrees counterclockwise.'''
        if not self.faller or self.faller["state"] == "frozen":
            return
        for i in range(3):
            self.rotate_clockwise()
        if self.faller["state"] == "falling" and self._will_land():
            self.faller["state"] = "landed"
        
    def fall(self, color1: str, color2: str) -> None:
        '''Implements the new horizontal faller with its two segments and if the spawner cell is activated then game over will be called.'''
        if self.faller is not None:
            return
        middle = (self.cols - 1) // 2
        self.faller = {
            "row": 1,
            "col": middle,
            "colors": [color1, color2],
            "orientation": "horizontal",
            "state": "falling", "just_spawned": True}
        if self._will_land():
            self.faller["state"] = "landed"
        if self.game_over():
            self.game_over_flag = True
        if hasattr(self, "gravity_pending"):
            self.gravity_pending = False

    def tick(self) -> None:
        '''Advances the game by one time step which could mean the faller moves, matches are cleared, or gravity is applied.'''
        if self.faller:
            st = self.faller["state"]
            r, c = self.faller["row"], self.faller["col"]
            left, right = self.faller["colors"]
            ori = self.faller["orientation"]
            if st == "falling":
                self.faller["row"] += 1
                if self._will_land():
                    self.faller["state"] = "landed"
                return
            if st == "landed":
                if ori == "horizontal":
                    self.field[r][c]   = left
                    self.field[r][c+1] = right
                    self.connected_caps.add(((r,c),(r,c+1)))
                else:
                    self.field[r-1][c] = left
                    self.field[r][c]   = right
                    self.connected_caps.add(((r-1,c),(r,c)))
                self.faller = None
                matches = self._find_matches()
                if matches:
                    self.marked_matches = matches
                    for (mr, mc) in matches:
                        self.field[mr][mc] = f"*{self.field[mr][mc]}*"
                return
        if self.marked_matches:
            matched = set(self.marked_matches)
            old_cons = self.connected_caps.copy()
            self._remove_matches(matched)
            self.marked_matches.clear()
            just_broken = set()
            for (p1, p2) in old_cons:
                if (p1 in matched) ^ (p2 in matched):
                    orphan = p2 if p1 in matched else p1
                    just_broken.add(orphan)
            rows, cols = self.rows, self.cols
            for rr in range(rows -2, -1, -1):
                for cc in range(cols):
                    cell = self.field[rr][cc]
                    if cell not in ("R", "Y", "B"):
                        continue
                    if  any((rr,cc) in pair for pair in self.connected_caps):
                        continue
                    if (rr, cc) in just_broken:
                        continue
                    if self.field[rr+1][cc] != " ":
                        continue
                    self.field[rr+1][cc] = cell
                    self.field[rr][cc] = " "
            return
        matches = self._find_matches()
        if matches:
            self.marked_matches = matches
            for (mr, mc) in matches:
                self.field[mr][mc] = f"*{self.field[mr][mc]}*"
            return
        self._gravity_step()
            
    def game_over(self) -> bool:
        '''Checks spawner cells and would return True if occupied.'''
        if self.cols % 2 == 0:
            middle1 = (self.cols // 2) - 1
            middle2 = middle1 + 1
        else:
            middle1 = middle2 = self.cols // 2
        return (self.field[1][middle1] != " " or self.field[1][middle2] != " ")

    def _gravity_step(self) -> bool:
        '''Implements the actual gravity once and will return True if there is any movement.'''
        moved = False
        new_connected = set()
        #  Horizontal connected capsules (L-R)
        for r in range(self.rows - 2, -1, -1):
            for c in range(self.cols - 1):
                pair = ((r, c), (r, c + 1))
                pair_rev = ((r, c + 1), (r, c))
                if pair in self.connected_caps or pair_rev in self.connected_caps:
                    if self.field[r][c] == " " or self.field[r][c + 1] == " ":
                        continue
                    if r + 1 >= self.rows:
                        continue
                    if self.field[r + 1][c] != " " or self.field[r + 1][c + 1] != " ":
                    self.field[r + 1][c] = self.field[r][c]
                    self.field[r + 1][c + 1] = self.field[r][c + 1]
                    self.field[r][c] = " "
                    self.field[r][c + 1] = " "
                    new_connected.add(((r + 1, c),  (r + 1, c + 1)))
                    moved = True
        # Vertical connected capsules (top-down)
        for r in range(self.rows - 2, -1, -1):
            for c in range(self.cols):
                current = self.field[r][c]
                below = self.field[r + 1][c]
                if current not in ("R", "Y", "B"):
                    continue
                pair = ((r, c), (r + 1, c))
                pair_rev = ((r + 1, c), (r, c))
                in_connected_pair = pair in self.connected_caps or pair_rev in self.connected_caps
                if in_connected_pair:
                    if r + 2 < self.rows and self.field[r + 2][c] == " ":
                        self.field[r + 2][c] = self.field[r + 1][c]
                        self.field[r + 1][c] = self.field[r][c]
                        self.field[r][c] = " "
                        new_connected.add(((r + 1, c), (r + 2, c)))
                        moved = True
                elif below == " " and not any((r, c) in p for p in self.connected_caps):
                    self.field[r + 1][c] = current
                    self.field[r][c] = " "
                    moved = True
        for (r1, c1), (r2, c2) in self.connected_caps:
            if ((abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)):
                if all(0 <= r < self.rows and 0 <= c < self.cols for r, c in [(r1, c1), (r2, c2)]):
                    cell1 = self.field[r1][c1]
                    cell2 = self.field[r2][c2]
                    if cell1 in ("R", "Y", "B") and cell2 in ("R", "Y", "B"):
                        new_connected.add(((r1, c1), (r2, c2)))
        self.connected_caps = new_connected
        return moved

    def _will_land(self, row = None, col = None, orientation = None) -> bool:
        '''Checks to see if fallers will land on its next movement and will report back if that is True.'''
        if self.faller is not None and row is None:
            row = self.faller["row"]
            col = self.faller["col"]
            orientation = self.faller["orientation"]
        below = row + 1
        if below >= self.rows:
            return True
        if orientation == "horizontal":
            return (self.field[below][col]   != " "
                or self.field[below][col+1] != " ")
        else:
            return self.field[below][col] != " "

    def _find_matches(self) -> set[tuple[int, int]]:
        '''Looks to find matches in the map and marks them as matches  to be returne.'''
        matches = set()
        directions = [(0, 1), (1, 0)]
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.field[r][c]
                if not isinstance(cell, str):
                    continue
                current_clean = cell.strip("*")
                if current_clean not in ("R", "Y", "B", "r", "y", "b"):
                    continue
                color = current_clean.upper()
                for dr, dc in directions:
                    chain = [(r, c)]
                    new_r = r + dr
                    new_c = c + dc
                    while (0 <= new_r < self.rows and 0 <= new_c < self.cols and
                        isinstance(self.field[new_r][new_c], str) and
                        self.field[new_r][new_c].strip("*").upper() == color):
                        chain.append((new_r, new_c))
                        new_r += dr
                        new_c += dc
                    if len(chain) >= 4:
                        matches.update(chain)
        return matches
    
    def _remove_matches(self, matched_pos: set[tuple[int, int]]) -> None:
        '''Removes matches and gets ready to split the caps.'''
        for r, c in matched_pos:
            self.field[r][c] = " "
        self.connected_caps = {pair for pair in self.connected_caps if pair[0] not in matched_pos and pair [1] not in matched_pos}
        self._split_caps_after_match(matched_pos)

    def check_matches_first(self) -> None:
        '''This looks for matches and marks them with asterisks.'''
        matches = self._find_matches()
        if matches:
            self.marked_matches = matches
            for r, c in matches:
                self.field[r][c] = f"*{self.field[r][c]}*"
    
    def is_capsule_connected(self, r1, c1, r2, c2) -> bool:
        '''Returns the connected capsulses.'''
        return ((r1, c1), (r2, c2)) in self.connected_caps or ((r2, c2), (r1, c1)) in self.connected_caps
        
    def _split_caps_after_match(self, matched_pos: set[tuple[int, int]]) -> None:
        '''This splits the capsules after it matches.'''
        updated_caps = set()
        for (r1, c1), (r2, c2) in self.connected_caps:
            in_match = (r1, c1) in matched_pos or (r2, c2) in matched_pos
            if not in_match:
                updated_caps.add(((r1, c1), (r2, c2)))
            else:
                for (r, c) in [(r1, c1), (r2, c2)]:
                    if (r, c) not in matched_pos:
                        if self.field[r][c] in ("R", "Y", "B"):
                            self.field[r][c] = self.field[r][c]
        self.connected_caps = updated_caps
        
    def level_cleared(self) -> bool:
        '''This checks to see if there is any viruses on the board.'''
        for row in self.field:
            for cell in row:
                clean = cell.strip("*")
                if clean in ("r", "y", "b"):
                    return False
        return True
