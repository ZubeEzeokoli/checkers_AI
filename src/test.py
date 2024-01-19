import os # create new processes
import time

# to use: cd Tools/ and run 'python3 test.py'

# set parameters
num_games = 10  # modify to simulate a different number of games
board_size = "10 10"
initial_rows = "2"
local = "l"
student_AI = "../src/checkers-python/main.py"
opponent_ai = "Sample_AIs/Poor_AI/main.py" # change to a different path to test different AI difficulty

student_wins = 0
start_time = time.time()

for _ in range(num_games):
    # runs one game
    command = "python3 AI_Runner.py {} {} {} {} {}".format(
        board_size, initial_rows, local, student_AI, opponent_ai
    )

    # runs shell command and reads into output
    process = os.popen(command)
    output = process.read()
    process.close()

    # check if our ai won
    if "player 1 wins" in output or "Tie" in output:
        student_wins += 1

    # print(output) # uncomment if you want to see the output of each game
end_time = time.time()

# total number of wins
win_rate =  int((student_wins / num_games) * 100)

print("Your AI won " + str(win_rate) + "% of the " + str(num_games) + " games.")
print("Runtime: {:.2f} sec".format(end_time - start_time))
