# Trivia game for Raspberry Pi

Reads inputs from PiFace DIO card. 
Inputs 0-3 = Team 1
Inputs 4-7 = Team 2

The game itself assumes two teams for four players. These are defined in
`config.json`, which looks like this

```json
{
    "teams": [
        ["Honey Monsters", ["Karen", "Sandy", "Jim", "Colleen"]],
        ["The Fridge Ninjas", ["Penny", "Arthur", "Chris", "Leslie"]]
    ]
}
```

This corresponds to Team 1 then Team 2. Players are input 0, 1, 2, 3 
for their respective teams. In other words:

* Pin 7 = Team 2, Player 3
* Pin 6 = Team 2, Player 2
* Pin 5 = Team 2, Player 1
* Pin 4 = Team 2, Player 0
* Pin 3 = Team 1, Player 3
* Pin 2 = Team 1, Player 2
* Pin 1 = Team 1, Player 1
* Pin 0 = Team 1, Player 0

## Flow

The game flow is as follows:
* Current Score

    The current score for both teams is shown.

* Listen

    The game displays the Listen screen and the host starts
    to read the question aloud. Any player may buzz in before
    the question has been fully read. 

    If the host fully reads the question, he presses SPACE to
    start the countdown timer.

* Timer

    The TIMER screen is shown after the question has been fully
    read aloud and no one has buzzed in yet. Players have 5 sec
    to buzz in and that person has to answer the question. 

    If no one buzzes in, the OUT OF TIME screen is displayed, 
    the question is forfeited and we go back to the Current 
    Score screen.

* Start Answer

    When a player has buzzed in, they have 5 seconds to start
    answering the question. First answer is accepted. When they
    start answering the question, the Host presses SPACE to 
    stop the timer and wait for the complete answer. 

    If the player does not start to answer within 5 sec, they
    lose the round (-10pts). 

* Answer
    
    Once the player has started answering the question, this
    screen is displayed. The host then presses Y or N if the
    answer is correct or incorrect. Or the host can press S
    to start the Steal phase.

* Steal

    For questions that are not True/False, the opposing team
    has a chance to steal after an incorrect answer is given.
    They get another 5 second timer to buzz in. If they
    buzz in, that player can answer for +5pts. Incorrect
    attempts to steal are -5pts. The original team still loses
    10pts for the first wrong answer. If the opposing
    team does no buzz in, only the original team loses points.

    The original team cannot buzz in during the steal phase.

    Optional rules: the opposing team can confer before buzzing
    in. 

* Right / Wrong
    
    After answering, a RIGHT or WRONG screen is displayed. The
    Host presses SPACE to start the next round (the Current
    Score screen).

## Scoring

Correct answers are +10 points and incorrect answers are -10 

Scores are written to `state.json` after every round. When the
game is started the last score is loaded. If you want to start
a fresh game, delete this file.

