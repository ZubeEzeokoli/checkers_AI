from random import randint
from BoardClasses import Board
import copy
import math
import time

# To test student AI against another AI - navigate to Tools/ directory
# run this command: python3 AI_Runner.py 8 8 2 l ../src/checkers-python/main.py Sample_AIs/Poor_AI/main.py
# instead of Poor_AI you can specify which one you want to play against

exploration_constant = 1.5 # as suggested by professor
opponent = {1:2,2:1} # used to switch player conveniently
class State():
    """
    State object which represents a node in the MC tree - modularity
    """
    def __init__(self, board, parent, player, move=None):
        self.board_state = board # stores the board state for this node
        self.parent = parent     # reference to the parent of this node
        self.children = []       # list of this node's children
        self.player = player     # stores the player for this node
        self.W = 0               # this node's number of wins
        self.S = 0               # this node's total number of simulations
        self.move = move         # move that led to the creation of this state

    def select(self):
        """
        given a State this function selects the child with the highest UCT of that State
        @return State: A State object
        """
        best_child = None        # no child found yet
        best_uct = float("-inf") 
        
        # returns itself if it is a leaf node
        if not self.children:
            return self

        # iterate over all children
        for child in self.children:

            # immediately return child if it has played no simulation
            if child.S == 0:
                return child
            
            # calculate uct of the child
            else:
                exploitation = child.W / child.S
                exploration = exploration_constant * math.sqrt(math.log(child.parent.S) / child.S)
                uct = exploitation + exploration
            
            # update best_child if current child has better uct
            if uct > best_uct:
                best_child = child
                best_uct = uct

        return best_child # return best child

    def expand(self):
        """
        given a State this function expands the state by adding all possible moves as children States
        """
        # add new State objects for each possible move
        board = self.board_state
        moves = board.get_all_possible_moves(self.player)

        for i in moves:  # add each move as a child of the root
            for move in i:
                temp_board = copy.deepcopy(board) # copy board
                temp_board.make_move(move, self.player) # apply move to new board
                new_state = State(temp_board, self, opponent[self.player], move) # creates a new state with the new board, current State as the parent, opposite player, and the move that led to this new state
                self.children.append(new_state) # add new state as a child of the current State

    def simulate(self):
        """
        this function simulates a rollout from the State's current board.
        simulation is cutoff if no capture is made after 25 moves
        """
        board = copy.deepcopy(self.board_state) # copy board
        player = self.player # track current player
        result = -1    # winner of rollout
        move_count = 0 # number of moves since last capture
        prev_black = board.black_count # number of black peices in previous board state
        prev_white = board.white_count # number of white peices in previous board state

        while True:
            if move_count > 25: #if 25 moves happened without a capture return hueristic as winner
                return self.get_heuristic(board)

            # check board for winner
            result = board.is_win(player)
            if result != 0:
                break
            moves = board.get_all_possible_moves(player)
            if not moves: # if the current player has no moves left (no peices), then the other player won
                return opponent[player]
            
            # otherwise make random momve
            index = randint(0,len(moves)-1)
            inner_index =  randint(0,len(moves[index])-1)
            move = moves[index][inner_index]
            board.make_move(move, player)
            player = opponent[player] # switch player

            # check if a capture happened to increase move out
            if board.black_count == prev_black and board.white_count == prev_white:
                move_count += 1
            else:
                move_count = 0

        # return winner of the simulated game
        return result # 1, 2, or -1

    def backpropagate(self, winner):
        """
        takes the winner of the simulation and updates State's up to the root
        @param winner: winner of the rollout
        """
        current = self # current is the starting State simulate was ran on

        # iterate back up the tree
        while current:
            # increments num and denom if State's color matches the winner
            if current.player == winner:
                current.W += 1
            current.S += 1
            # move to next State up the tree
            current = current.parent
        return
    
    def get_heuristic(self, board):

        """
        Calculates which player is more likely to win based off the number of remaining peices
        @param board: Board object
        @return: player with more peices
        """
        num_w, num_w_kings = 0, 0  # count number of white pieces and kings
        num_b, num_b_kings = 0, 0  # count number or black pieces and kings
        board = board.board
        # board can be variable size
        for r in range(len(board)):
            for c in range(len(board[0])):
                piece = board[r][c] # access checker object
                
                king = piece.is_king              # check if the piece is a king
                color = piece.get_color().lower() # get the piece color

                # update piece counts
                if color == 'w' and king:
                    num_w_kings += 1
                elif color == 'w':
                    num_w += 1
                elif color == 'b' and king:
                    num_b_kings += 1
                elif color == 'b':
                    num_b += 1

        black_points = (num_b - num_w) + 3 * (num_b_kings - num_w_kings)
        white_points = (num_w - num_b) + 3 * (num_w_kings - num_b_kings)

        if black_points > white_points:
            return 1
        else:
            return 2
    
    def get_best_state(self):
        """
        given a State this function selects the child with the highest winrate W/S.
        This is called by the root to get the best State after MCTS
        @return State: A State object
        """
        best_child = None        # no child found yet
        best_val = float("-inf")

        # iterate over all children
        for child in self.children:
            if child.S == 0:
                return child
            val = child.W / child.S
            # update best_child if current child has better uct
            if val > best_val:
                best_child = child
                best_val = val

        return best_child # return best child

class StudentAI():

    total_time = 0 # tracks total time used up for all moves

    def __init__(self,col,row,p):
        
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.opponent = {1:2,2:1}
        self.color = 2
        self.root = None # root of the tree
        self.max_iterations = 1000  # Initial maximum iterations

    def get_move(self, move):
        """
        get_move function for StudentAI
        @param move: A Move object describing the move.
        @return res_move: A Move object describing the move StudentAI wants to make.
        """
        start_time = time.time() # starts timer for current move
        iterations = 0           # number of times MCTS has run within the time limit
        time_limit = 8.0         # maximum time the current move can take

        # update board with opponent's last move
        if move:
            self.board.make_move(move,self.opponent[self.color])
        # otherwise AI makes the first move
        else:
            self.color = 1
        
        # makes a random move if total time has reached 4.5 minutes (5 min time limit)
        if StudentAI.total_time > 270:
            moves = self.board.get_all_possible_moves(self.color)
            index = randint(0,len(moves)-1)
            inner_index =  randint(0,len(moves[index])-1)
            move = moves[index][inner_index]
            self.board.make_move(move,self.color)
            elapsed_time = time.time() - start_time
            StudentAI.total_time += elapsed_time
            return move

        # setup initial tree before any iterations (this is the first time get_move() is called for this game) - consists of the root, with children being all states that can be reached from the initial board
        if self.root == None:
            self.root = State(self.board, None, self.color)       # sets root to a new state with the current board, no parent, and AI's color
            moves = self.board.get_all_possible_moves(self.color) # gets all possible moves

            for i in moves:  # add each move as a child of the root
                for move in i:
                    temp_board = copy.deepcopy(self.board) # copy board
                    temp_board.make_move(move, self.color) # apply move to new board
                    new_state = State(temp_board, self.root, self.opponent[self.root.player], move) # creates a new state with the new board, root as the parent, opposite player, and move that led to new state
                    self.root.children.append(new_state) # add new state as a child of the root

        # otherwise we already have a game tree: update root to point to opponents last action
        else:
            # move root to state that the opponent made
            temp = self.root
            for child in temp.children: # iterate over roots children
                child_move = child.move
                if str(move) == str(child_move): # compare passed in move with child's move
                    self.root = child            # moves match - update root

        # perform MCTS until time_limit or max_iterations is reached (selection, expansion, simulation, backpropagation)
        while time.time() - start_time < time_limit and iterations < self.max_iterations:
            
            iterations += 1     # update iterations for this MCTS
            current = self.root # pointer to root of the game tree

            # SELECTION
            # loops until leaf node is reached and selects new node based off current's children
            while current.children:
                current = current.select()
            # we now should have a selected leaf node
            
            # EXPANSION
            simulate = True

            # if S = 0, then we go straight to simulation on current State
            # if the selected state is a terminal state then do not expand or simulate ONLY do backpropagation
            terminal_state = current.board_state.is_win(current.player)
            if terminal_state != 0: # -1 game tied
                simulate = False
                # winner is the return value if nonzero, otherwise its a tie and our AI wins
                winner = terminal_state if terminal_state > 0 else self.color # winner is 1 or 2
            
            # current State has done some simulations previously - expand it
            elif current.S > 0:
                current.expand()              # adds all children (possible moves)
                if current.children:
                    current = current.children[0] # set current to first child of current

            # SIMULATE - on current State
            if simulate:
                winner = current.simulate() # 1, 2, or -1
                if winner == -1: # if -1 game tied and our AI should win (self.root)
                    winner = self.color

            # BACKPROPAGATION - current points to leaf State and winner has the result of simulate on that State
            current.backpropagate(winner)

        # select root's child with highest UCT and return the move that got there
        best_state = self.root.get_best_state()

        # figure out what move got us to that state
        if best_state:
            move = best_state.move # sometimes crashes if best_state is None - fix later
        
        # update root to the state where it chose its move
        self.root = best_state 

        elapsed_time = time.time() - start_time # calculate time taken for this move
        StudentAI.total_time += elapsed_time    # update total time
        self.max_iterations = max(int(self.max_iterations * 0.9), iterations + 100) # adjust max_iterations for next time - reduce max_iterations by 10% or increase # based off previous iterations

        self.board.make_move(move, self.color) # make the move
        return move
