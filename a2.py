#Liam Kennedy
#lpkenned@uci.edu
#81845142
from game_logic import Game
import shlex
def main():
    #some starting stuff
    row = int(input())
    col = int(input())
    board = []
    config = input().strip()
    if config == "EMPTY":
        board = [[" " for i in range(col)] for i in range(row)]
    elif config == "CONTENTS":
        for i in range(row):
            line = input()
            if len(line) != col:
                raise ValueError
            board.append(list(line))
    else:
        raise ValueError("config error")
    game = Game(row, col, board)
    game.check_matches_first()   
    while True:
        for line in game.show_field():
            print(line)
        command = input()
        if command == "":
            game.tick()
        else:
            command = command.strip().upper()
            if command == "Q":
                break
            args = shlex.split(command)
            if args[0] == "F" and len(args) == 3:
                game.fall(args[1], args[2])
            elif args[0] == "V" and len(args) == 4:
                r, c, col = int(args[1]), int(args[2]), args[3].lower()
                game.field[r][c] = col
                matches_v = game._find_matches()
                if matches_v:
                    game.marked_matches = matches_v
                    for (marked_row, marked_col) in matches_v:
                        game.field[marked_row][marked_col] = f"*{game.field[marked_row][marked_col]}*"
            elif command == "<":
                game.move_left()
            elif command == ">":
                game.move_right()
            elif command == "A":
                game.rotate_clockwise()
            elif command == "B":
                game.rotate_counter_clockwise()
            else:
                pass
        if game.game_over_flag:
            for line in game.show_field():
                print(line)
            print("GAME OVER")
            break
if __name__ == "__main__":
    main()