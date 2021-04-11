import variables, AbaloneGraphics

class Abalone:
    ARRANGEMENT = [5, 6, 7, 8, 9, 8, 7, 6, 5]  # const
    DIRECTIONS = ['right', 'left', 'top right', 'top left', 'bottom right', 'bottom left']

    def __init__(self):
        # Create the board:
        rows = 9
        curr = 5
        # Initialize every cell to its correct value
        self.board = list()
        self.pushed_out = {'black': 0, 'white': 0}
        adder = 0
        index = 0
        row_start = 0
        row_end = row_start + curr - 1
        for i in range(rows):
            for j in range(curr):
                dist = abs(rows // 2 - i)
                if min(j, curr - j - 1) < adder:
                    dist = rows // 2 - min(j, curr - j - 1)
                cell = Cell('blank', index, i, row_start, row_end, dist)
                index += 1
                self.board.append(cell)
            curr += 1 if rows // 2 - i > 0 else -1
            adder += 1 if rows // 2 - i > 0 else -1
            row_start = row_end + 1
            row_end = row_start + curr - 1
        # Initialize board configuration
        if variables.regular_layout == True:
            for i in self.board[:11] + self.board[13:16]:
                i.value = 'white'
            for i in self.board[50:] + self.board[45:48]:
                i.value = 'black'
        else: #Daisy format
            for i in self.board[5:7] + self.board[11:14] + self.board[19:21] + self.board[40:42] + self.board[47:50] + self.board[54:56]:
                i.value = 'black'
            for i in self.board[9:11] + self.board[15:18] + self.board[23:25] + self.board[36:38] + self.board[43:46] + self.board[50:52]:
                i.value = 'white'

        self._all_lines = []
        for i in [0, 5, 11, 18, 26, 35, 43, 50, 56]:
            self._all_lines.append(self.getLine(i, 'right'))
        for i in [26, 35, 43, 50, 56, 57, 58, 59, 60]:
            self._all_lines.append(self.getLine(i, 'top right'))
        for i in [56, 57, 58, 59, 60, 55, 49, 42, 34]:
            self._all_lines.append(self.getLine(i, 'top left'))

    def getLine(self, index, direction):
        """ Return a list of indexes on one line, that a move can be played on """

        # Possible directions: [top / bottom] + left / right

        def diag(op, offset, condition, stop=-1):
            """ Helper function to avoid code duplication, nested for incapsulation's sake """
            # stop - stop when reached a row whos index is "stop" (get rows [index, stop))
            # condition - after the addition how far above should the next row be
            # offset - amount to add to the index each time
            # op - add or substract - either 1 or -1
            res = [index]
            next = index + op * (self.board[index].row_size) + offset
            while 0 <= next <= 60 and self.board[next].row_index + condition == self.board[res[-1]].row_index and \
                            self.board[next].row_index != stop:
                res.append(next)
                next = next + op * (self.board[next].row_size) + offset
            return res

        cell = self.board[index]
        if direction == "right":
            return [i for i in range(index, cell.row_end + 1)]

        if direction == "left":
            return [i for i in range(index, cell.row_start - 1, -1)]

        if direction == "top right":
            if cell.row_index <= 4:
                return diag(-1, 1, 1)
            res = diag(-1, 0, 1, 3)
            index = res[-1]
            res.pop(-1)
            res += diag(-1, 1, 1)
            return res

        if direction == "top left":
            if cell.row_index <= 4:
                return diag(-1, 0, 1)
            res = diag(-1, -1, 1, 3)
            index = res[-1]
            res.pop(-1)
            res += diag(-1, 0, 1)
            return res

        if direction == "bottom right":
            if cell.row_index > 4:
                return diag(1, 0, -1)
            res = diag(1, 1, -1, 5)
            index = res[-1]
            res.pop(-1)
            res += diag(1, 0, -1)
            return res

        if direction == "bottom left":
            if cell.row_index > 4:
                return diag(1, -1, -1)
            res = diag(1, 0, -1, 5)
            index = res[-1]
            res.pop(-1)
            res += diag(1, -1, -1)
            return res

    def makeMove(self, index, direction):
        """ Tries to make a move (single ball), if not possible raises an InvalidMove exception """
        line = self.getLine(index, direction)
        pusher_ball = self.board[line[0]]  # The ball chosen to try and move
        if pusher_ball.value == 'blank':
            raise InvalidMove("An empty cell was chosen")
        if len(line) == 1:
            raise InvalidMove("You cannot eliminate yourself!")

        pusher_balls = 1  # The amount we try to push at once
        for i in range(1, len(line)):  # Count that amount
            if self.board[line[i]].value == pusher_ball.value:
                pusher_balls += 1
                if pusher_balls > 3:
                    raise InvalidMove("Cannot push more than 3 balls")
            else:
                break
        else:
            raise InvalidMove("You cannot eliminate yourself!")

        # Got here if try to push < 4 balls, and we found potential space to push them to
        if self.board[line[i]].value == 'blank':  # i is the next item in the list
            self.board[line[i]].value = self.board[line[0]].value  # Blank spot fills in with the pusher ball
            self.board[line[0]].value = 'blank'  # The pushing ball turns to blank
            return  # Push successful, simple move done

        # Trying to push an enemy ball if got here
        pushed_ball = self.board[line[i]]
        pushed_balls = 0
        for j in range(i, len(line)):  # Count amount of enemy balls trying to push
            if self.board[line[j]].value == pushed_ball.value:
                pushed_balls += 1
                if pushed_balls >= pusher_balls:
                    raise InvalidMove("Cannot push over or equal amount of enemy balls")
            else:
                break
        else:
            self.pushed_out[self.board[line[pusher_balls]].value] += 1
            self.board[line[pusher_balls]].value = self.board[line[0]].value  # pushed_ball = pusher_ball
            self.board[line[0]].value = 'blank'  # The pushing ball turns to blank
            return  # Push successful, pushed enemy ball out of the board!

        # Got here if hit a blank spot and therefor can move, or there is a pusher ball type ball in the way
        if self.board[line[j]].value == pusher_ball.value:
            raise InvalidMove("Cannot push your own balls through enemy ones!")

        self.board[line[j]].value = pushed_ball.value  # Blank spot became occupied by the enemy ball
        self.board[line[pusher_balls]].value = self.board[line[0]].value  # pushed_ball = pusher_ball
        self.board[line[0]].value = 'blank'  # The pushing ball turns to blank
        return  # Push successful, pushed enemy balls

    def move(self, indices, direction):
        """ Make a diagonal move with 2/3 balls selected, if impossible raise InvalidMove """
        if len(indices) < 0:
            raise InvalidMove("No target was selected!")
        if len(indices) > 3:
            raise InvalidMove("Cannot push more than 3 balls")
        if len(indices) == 1:
            self.makeMove(indices[0], direction)

        else:
            for dirct in self.DIRECTIONS:
                line = self.getLine(indices[0], dirct)
                if line[:len(indices)] == indices:
                    break
            else:
                raise InvalidMove("Chosen balls are not in a straight line!")

            ball_type = self.board[indices[0]].value
            for i in indices:
                if self.board[i].value == 'blank' or self.board[i].value != ball_type:
                    raise InvalidMove("You have not chosen the same kind of balls (or none at all)")

            target_indices = []
            for i in indices:
                line = self.getLine(i, direction)
                if not (len(line) > 1 and self.board[line[1]].value == 'blank'):
                    break
                target_indices.append(
                    line[1])  # If everything is legal, we will move the selected balls to these locations
            else:  # Never broke the loop - all indices legal
                for i in range(len(indices)):
                    self.board[target_indices[i]].value = self.board[indices[i]].value
                    self.board[indices[i]].value = 'blank'
                return
            raise InvalidMove("Path blocked")

    def calcDistance(self, value):
        '''Used in the calculation of the value of a given board in self.evaluate_max/min'''
        sum = 0
        for i in self.board:
            if i.value == value:
                sum += 4 - i.distance
        return sum

    def getAdjacent(self, index):
        '''Returns a list of all adjacent friendly balls'''
        value = self.board[index].value
        tot = list()
        for i in self.DIRECTIONS:
            temp = self.getLine(index, i)
            if len(temp) > 1 and self.board[temp[1]].value == value:
                tot.append(self.board[temp[1]])
        return tot

    def calcChunks(self, value):
        '''Returns the total value of all chunks, used in the calculation of the value of a given board in self.evaluate_max/min'''
        res = 0
        for i in range(len(self.board)):
            if self.board[i].value == value:
                temp = self.getAdjacent(i)
                res += len(temp)
        if res == 6:
            return 2
        return res

    def calcSequences(self, value):
        '''Returns the value of sequences of balls, used in the calculation of the value of a given board in self.evaluate_max/min'''
        result = 0
        for line in self._all_lines:
            seq = 0
            for i in line:
                if self.board[i].value == value:
                    seq += 1
                else:
                    result += 0 if seq != 2 and seq != 3 else 1 if seq == 2 else 3
                    seq = 0
            result += 0 if seq != 2 and seq != 3 else 1 if seq == 2 else 3
        return result

    def getAvaliableMoves(self, value):
        '''Returns all possible moves'''
        moves = []  # move format: ([index 1, index 2, index 3], direction)
        for i, line in enumerate(self._all_lines):
            directions = [ \
                ['top right', 'top left', 'bottom right', 'bottom left'], \
                ['right', 'left', 'top left', 'bottom right'], \
                ['right', 'left', 'top right', 'bottom left']][i // 9]
            last = []
            for index in line:
                if self.board[index].value == value:
                    [moves.append(([index], direction)) for direction in directions]
                    for j in range(1, min(len(last), 2) + 1):
                        [moves.append((sorted([index] + last[-1 * j:]), direction)) for direction in directions]
                    last.append(index)
                else:
                    last = []
        return moves

    def minimax(self, value, depth):
        '''Returns the optimal move'''
        diff = AbaloneGraphics.difficulty
        push_out_value = 45 if diff == 1 else 50 if diff == 2 else 75
        return self.evaluate_max(value, min(2, depth), self.pushed_out, float('inf'), push_out_value,
                                 variables.percentage_display)[1]

    def evaluate_max(self, value, depth, curr, smaller, push_out_value, percentage_display = False):
        #curr - state of how many balls are out at the time of the evaluation
        #smaller - cut the tree when your best is greater than "smaller" (all valid results must be smaller than it)
        value2 = 'black' if value == 'white' else 'white'
        backup = [i.value for i in self.board]
        pushed_out = dict(self.pushed_out)
        moves = self.getAvaliableMoves(value)
        best = float('-inf')
        best_move = []

        for i, move in enumerate(moves):
            if percentage_display:
                print(str(round(i/len(moves)*100, 2)) + '% done')
            val = 0
            try:
                if depth == 1:
                    self.move(move[0], move[1])
                    val += push_out_value * (self.pushed_out[value2] - curr[value2] - (self.pushed_out[value] - curr[
                        value]))
                    if val == 0 and variables.boring_moves >= variables.boring_move_cap: #none pushed = boring move!
                        val -= 250 #penalty
                    elif val != 0:
                        val += 250
                    val += self.calcChunks(value) - self.calcChunks(value2)
                    val += self.calcDistance(value) - self.calcDistance(value2)
                    val += self.calcSequences(value) - self.calcSequences(value2)
                else:
                    self.move(move[0], move[1])
                    val = self.evaluate_min(value, depth-1, curr, best, push_out_value)[0]

                if best < val:
                    best = val
                    best_move = move

                for i in move[0]: #restore board
                    for j in self.getLine(i, move[1]):
                        self.board[j].value = backup[j]
                self.pushed_out = dict(pushed_out) #restore pushed out

                if best >= smaller:
                    return best, best_move

            except InvalidMove:
                pass

        return best, best_move

    def evaluate_min(self, value, depth, curr, greater, push_out_value):
        # curr - state of how many balls are out at the time of the evaluation
        # greater - cut the tree when your best is smaller than "greater" (all valid results must be greater than it)
        value2 = 'black' if value == 'white' else 'white'
        backup = [i.value for i in self.board]
        pushed_out = dict(self.pushed_out)
        moves = self.getAvaliableMoves(value2)
        best = float('inf')
        best_move = []

        for move in moves:
            val = 0
            try:
                if depth == 1:
                    self.move(move[0], move[1])
                    val += push_out_value * (self.pushed_out[value2] - curr[value2] - (self.pushed_out[value] - curr[
                        value]))
                    if val == 0 and variables.boring_moves >= variables.boring_move_cap: #none pushed = boring move!
                        val -= 250 #penalty
                    elif val != 0:
                        val += 250
                    val += self.calcChunks(value) - self.calcChunks(value2)
                    val += self.calcDistance(value) - self.calcDistance(value2)
                    val += self.calcSequences(value) - self.calcSequences(value2)
                else:
                    self.move(move[0], move[1])
                    val = self.evaluate_max(value, depth - 1, curr, best, push_out_value)[0]

                if best > val:
                    best = val
                    best_move = move

                for i in move[0]: #restore board
                    for j in self.getLine(i, move[1]):
                        self.board[j].value = backup[j]
                self.pushed_out = dict(pushed_out) #restore pushed out

                if best <= greater:
                    return best, best_move

            except InvalidMove:
                pass

        return best, best_move

class Error(Exception):
    pass

class InvalidMove(Error):
    def __init__(self, message):
        self.message = message

class Cell:
    def __init__(self, value, index, row_index, row_start, row_end, distance):
        self.index = index
        self.row_index = row_index
        self.distance = distance
        self.value = value
        self.row_start = row_start
        self.row_end = row_end
        self.row_size = row_end - row_start + 1
