#include <arduino.h>

#define NUM_TEAMS 3
#define PLAYERS_PER_TEAM 4
int teams[NUM_TEAMS][PLAYERS_PER_TEAM] = {
                                           {2, 3, 4, 5},
                                           {6, 7, 8, 9},
                                           {10, 11, 12, 13}
                                         };

void setup() {
  Serial.begin(115200);
  Serial.println("Starting up TriviaBox. Version 0.1");
  
  for (int team=0; team < NUM_TEAMS; team++) {
    for (int player=0; player < PLAYERS_PER_TEAM; player++) {
      int pin = teams[team][player];
      pinMode(pin, INPUT);
      digitalWrite(pin, HIGH);
    }
  }
  
  // Use analog 0 pullup-resistor for faster resets.
  digitalWrite(A0, HIGH);
}

void loop() {
  Serial.println("--------- Ready --------------------");  

  while (analogRead(14) < 100) 
    ;
    
  Serial.println("----------- GO! -------------");

  int winning_team = -1;
  int winning_player = -1;

  while (winning_team == -1) {    
    for (int team=0; team < NUM_TEAMS && winning_team == -1; team++) {
      for (int player=0; player < PLAYERS_PER_TEAM && winning_player == -1; player++) {
        int pin = teams[team][player];
        int state = digitalRead(pin);

        if (state == 0) {
           winning_team = team;
           winning_player = player;
        }
      }
    }
  }
  
  Serial.print("Winning Team: "); 
  Serial.print(winning_team);
  Serial.print(", Winning Player: ");
  Serial.println(winning_player);
  Serial.println("--------- Waiting for Reset ---------------");  
  
  while (analogRead(14) >= 100)
    ;

}
