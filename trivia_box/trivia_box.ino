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
}

void loop() {
  for (int team=0; team < NUM_TEAMS; team++) {
    for (int player=0; player < PLAYERS_PER_TEAM; player++) {
      int pin = teams[team][player];
      int state = digitalRead(pin);
      Serial.print(pin);
      Serial.print(" ");
      Serial.println(state);
    }
  }
  delay(500);
  Serial.println("-----------------------------");
}
