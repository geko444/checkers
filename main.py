import numpy as np
import ast
import random


class Board:
    def __init__(self):
        self.grid = np.zeros(shape=(8,8), dtype=np.int16)
        for i in range(8):
            for j in range(8):
                if (i+j) % 2 == 0:
                    self.grid[i,j] = 9
        self.setup_pieces()
        self.turn = 1
        self.repeat = 0
        self.history = []
        self.p_dict = {-1: 'B', 1: 'W'}

    def export_board(self):
        return [self.piece_at_num(n) for n in range(1, 33)]

    def import_board(self, board):
        assert len(board) == 32
        for n in range(32):
            self.insert_at_num(n+1, board[n])

    def print_grid(self):
        key = {0:'  ', 9:'██', 1:'⛂ ', 2:'⛃ ', -1:'⛀ ', -2:'⛁ '}
        for j in range(8):
            print(''.join([key[i] for i in self.grid.tolist()[j]]))


    @staticmethod
    def pos_to_num(i,j):
        assert (i+j)%2 == 1
        if i%2==0:
            return int((4*i+1)+(j-1)/2)
        else:
            return int((4*i+1)+j/2)


    @staticmethod
    def num_to_pos(n):
        i = int((n-1)//4)
        if i%2 == 0:
            j = int((n-1)%4*2 + 1)
        else:
            j = int((n-1)%4*2)
        return i,j

    def insert_at_num(self, n, val):
        i,j = self.num_to_pos(n)
        self.grid[i,j] = val

    def setup_pieces(self):
        for n in range(1,13):
            self.insert_at_num(n, 1)
        for n in range(21,33):
            self.insert_at_num(n, -1)

    def state(self):
        board = self.export_board()
        for i in [-1, 1]:
            if board.count(i) + board.count(i*2) == 0:
                return self.p_dict[i*-1]
        if self.repeat == 0:
            if len(self.possible_moves(self.turn)) == 0:
                return self.p_dict[self.turn*-1]
        return 'P'


    def piece_at_num(self, n):
        i,j = self.num_to_pos(n)
        return self.grid[i,j]

    def piece_at_coords(self, n):
        return self.grid[i,j]

    def king_piece(self, n):
        if n in range(29, 33):
            if self.piece_at_num(n) == 1:
                self.insert_at_num(n, 2)
                return 1
        elif n in range(1, 5):
            if self.piece_at_num(n) == -1:
                self.insert_at_num(n, -2)
                return 1
        return 0

    def king_pieces(self):
        k = 0
        for n in [1, 2, 3, 4, 29, 30, 31, 32]:
            k += self.king_piece(n)
        return k

    def step_piece(self, a, b):
        assert self.piece_at_num(b) == 0
        p = self.piece_at_num(a)
        self.insert_at_num(a, 0)
        self.insert_at_num(b, p)

    def jump_piece(self, a, c):
        A = self.num_to_pos(a)
        C = self.num_to_pos(c)
        i,j = ((A[0]+C[0])/2,(A[1]+C[1])/2)
        b = self.pos_to_num(i,j)
        p = self.piece_at_num(a)
        assert self.piece_at_num(a) * self.piece_at_num(b) < 0
        assert self.piece_at_num(c) == 0
        self.insert_at_num(a, 0)
        self.insert_at_num(b, 0)
        self.insert_at_num(c, p)

    def move_piece(self, v, w):
        V = self.num_to_pos(v)
        W = self.num_to_pos(w)
        if (V[0]-W[0])**2 == 1:
            self.step_piece(v, w)
            return 'S'
        else:
            self.jump_piece(v, w)
            return 'J'


    def steps_possible_at_num(self, n, multi=0):
        steps = []
        i,j = self.num_to_pos(n)
        p = self.piece_at_num(n)
        assert p != 0
        if (p*p > 1) or multi==1:
            rows = [i+1, i-1]
        else:
            rows = [i+p]
        for a in rows:
            for b in [j+1, j-1]:
                if a in range(8) and b in range(8):
                    m = self.pos_to_num(a,b)
                    if self.piece_at_num(m) == 0:
                        steps.append((n,m))
        return steps


    def jumps_possible_at_num(self, n, multi=0):
        jumps = []
        i,j = self.num_to_pos(n)
        p = self.piece_at_num(n)
        assert p != 0
        if (p*p > 1) or multi==1:
            rows = [i+2, i-2]
        else:
            rows = [i+2*p]
        for a in rows:
            for b in [j+2, j-2]:
                if a in range(8) and b in range(8):
                    c,d = ((i+a)/2,(j+b)/2)
                    s = self.pos_to_num(a,b)
                    t = self.pos_to_num(c,d)
                    if self.piece_at_num(s) == 0:
                        if self.piece_at_num(t)*p < 0:
                            jumps.append((n,s))
        return jumps

    def possible_moves(self, player, multi=0):
        steps = []
        jumps = []
        for i in range(1,33):
            piece = self.piece_at_num(i)
            if piece in [player, player*2]:
                steps += self.steps_possible_at_num(i)
                jumps += self.jumps_possible_at_num(i, multi=multi)
        if len(jumps) > 0 or multi==1:
            return jumps
        else:
            return steps

    def move(self, move, multi=0):
        possible = self.possible_moves(self.turn, multi)
        assert move in possible
        move_type = self.move_piece(move[0], move[1])
        crowned = self.king_pieces()
        if multi == 0:
            self.history.append(move)
        else:
                self.history[-1] += (move[1],)
        if move_type == 'J' and crowned == 0 and len(self.jumps_possible_at_num(move[1], 1)) > 0:
            self.repeat = 1
        else:
            self.turn *= -1
            self.repeat = 0

    def human_player_turn(self, multi=0):
        multi = self.repeat
        self.print_grid()
        while True:
            try:
                inp = ast.literal_eval(input('{} --> '.format(self.p_dict[self.turn])))
                self.move(inp, multi)
                break
            except SyntaxError:
                print('The fuck?')
            except AssertionError:
                print('Not that one, ya cunt!')
            except ValueError:
                print('Stop typing with your elbows!')
        print(' ')
#        if mt == 'J' and len(self.possible_moves(self.turn, multi=1)) > 0 and cr == 0:
#            human_player_turn(self, multi=1)
#        else:
#            self.turn *= -1

    def random_player_turn(self, multi=0):
        multi = self.repeat
        self.print_grid()
        print("{}'s turn.".format(self.p_dict[self.turn]))
        print(' ')
        possible = self.possible_moves(self.turn, multi)
        turn = random.choice(possible)
        self.move(turn, multi)
#        if mt == 'J' and len(self.possible_moves(self.turn, multi=1)) > 0 and cr == 0:
#            random_player_turn(self, multi=1)
#        else:
#            self.turn *= -1

    def play(self):
        while self.state() == 'P':
            if self.turn == 1:
                self.random_player_turn()
            else:
                self.random_player_turn()
        self.print_grid()
        print(self.state(), 'wins!')

b = Board()

l = [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, -1] + 14*[0]
#b.import_board(l)
#b.turn = -1

b.play()
print(b.history)
