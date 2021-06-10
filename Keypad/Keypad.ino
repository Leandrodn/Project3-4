#include <Keypad.h>

//2 constanten aanmaken voor hoeveelheid knoppen
const byte ROWS = 4; //four rows
const byte COLS = 4; //four columns

//keypad layout declareren in een 2D Array
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

//Digitale inputs verklaren van arduino
byte rowPins[ROWS] = {6, 7, 8, 9}; //connect to the row pinouts of the keypad
byte colPins[COLS] = {10, 11, 12, 13}; //connect to the column pinouts of the keypad

//Create an object of keypad
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
  //Seriële monitor initialiseren
  Serial.begin(9600);
}
  
void loop() {
  //Als er een knop op de keypad wordt ingedrukt, wordt deze opgeslagen in variabele key als character
  char key = keypad.getKey();// Read the key
  
  //Print de key uit op de Seriële monitor als er een waarde in de variable key is gezet
  if (key) {
    Serial.print(key);
  }
}
