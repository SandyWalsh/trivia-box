# Trivia game for Raspberry Pi

Currently this uses I2C to communicate with an Arduino which monitors the
input buttons. But I think the GPIO on the RPi should be plenty fast
enough and there seems to be enough pins ... so I'll likely change all this. 

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
    answer is correct or incorrect. 

* Right / Wrong
    
    After answering, a RIGHT or WRONG screen is displayed. The
    Host presses SPACE to start the next round (the Current
    Score screen).

## Scoring

Correct answers are +10 points and incorrect answers are -10 

Scores are written to `state.json` after every round. When the
game is started the last score is loaded. If you want to start
a fresh game, delete this file.

