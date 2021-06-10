#include<Stepper.h>
#include "Adafruit_Thermal.h"
#include "logoV4.4.h"

#include "SoftwareSerial.h"
#define TX_PIN 13 // Arduino transmit  YELLOW WIRE  labeled RX on printer
#define RX_PIN 12 // Arduino receive   GREEN WIRE   labeled TX on printer

const int stepsPerRotation = 2048;
const int stepperSpeed = 14;

//Seen from the front (IN1, IN3, IN2, IN4)
Stepper stepperMotorLeft = Stepper(stepsPerRotation, 14, 16, 15, 17); //pins from Mega
Stepper stepperMotorCenter = Stepper(stepsPerRotation, 7, 5, 6, 4); //pins from Mega
Stepper stepperMotorRight = Stepper(stepsPerRotation, 11, 9, 10, 8); //pins from Mega

SoftwareSerial mySerial(RX_PIN, TX_PIN); // Declare SoftwareSerial obj first
Adafruit_Thermal printer(&mySerial);     // Pass addr to printer constructor


void leftMotorOneBill();
void centerMotorOneBill();
void rightMotorOneBill();


String x;
int notes50 = -1;
int notes20 = -1;
int notes10 = -1;
void moneyDispenser();

String date = "";
String currentTime = "";
int transactionNo = -1;
String accountNo = "";
int cardNo = -1;
int amount = -1;

//setups the motors and the receipt printer
void setup() {
  Serial.begin(9600);
  Serial.setTimeout(100);
  mySerial.begin(9600);
  stepperMotorLeft.setSpeed(stepperSpeed); //10 euro
  stepperMotorCenter.setSpeed(stepperSpeed); //20 euro
  stepperMotorRight.setSpeed(stepperSpeed); //50 euro
  printer.begin();
  checkReceiptOrDispenser();
}

void loop() {
}

//checks if the computer wants to send the dipsenser info or the receipt info
//if it sends m it wants to dispense, and r for receipt
void checkReceiptOrDispenser(){
  while(true){
    int i = -2;
    x = Serial.readString();
    x = String(x);
    Serial.println(i);
    boolean hadMoney = false;
    if(x != ""){
      if(x.indexOf("m") > -1){//m is money dispenser
        Serial.println(-1);
        delay(100);
        moneyDispenser();
        hadMoney = true;
      } else if (x.indexOf("r")){//r is receipt print
        Serial.println(-1);
        receipt();
        hadMoney = false;
      }
    }
  }
}

//Will try to receive the receipt info, in the form (char), info as stated, will wait till all info is set
void receipt(){
  int i = 0;
  while(!(date != "" && currentTime != "" && transactionNo != -1 && accountNo != "" && cardNo != -1 && amount != -1)){
    while (!Serial.available());
    x = Serial.readString();
    x = String(x);
    if(x != ""){
      Serial.println(6);
      if(x.indexOf("d") > -1){ //d is date
        String temp = x.substring(2);
        if(date == ""){
          date = temp;
        }
      } else if (x.indexOf("t") > -1){ //t is time
        String temp = x.substring(2);
        if(currentTime == ""){
          currentTime = temp;
        }
      } else if (x.indexOf("o") > -1){ // o is transaction nO
        int temp = x.substring(2).toInt();
        if(transactionNo == -1){
          transactionNo = temp;
        }
      } else if (x.indexOf("a") > -1){ //a is accountNo
        String temp = x.substring(2);
        if(accountNo == ""){
          accountNo = temp;
        }
      } else if (x.indexOf("c") > -1){ //c is cardNo
        int temp = x.substring(2).toInt();
        if(cardNo == -1){
          cardNo = temp;          
        }
      } else if (x.indexOf("h") > -1){ //h is amount
        int temp = x.substring(2).toInt();
        if(amount == -1){
          amount = temp;
        }
      }
    }
  }
  printReceipt();
}

//prints the receipt with the set info
void printReceipt(){
  //Prints header (Logo and name)
  printer.printBitmap(320, 97, logoV4);
  printer.justify('C');
  printer.boldOn();
  printer.setSize('L');
  printer.println(F("ABN - MANBRO"));
  printer.boldOff();
  printer.setSize('S');
  printer.underlineOn();
  printer.println(F("                                "));
  printer.underlineOff();
  
  //Date and time information
  printer.justify('L');
  printer.print("Datum: ");
  printer.print(date);
  printer.print("   Tijd: ");
  printer.println(currentTime);
  printer.justify('C');
  printer.underlineOn();
  printer.println(F("                                "));
  printer.underlineOff();
  
  //Machine, transaction number information
  printer.justify('L');
  printer.println("Automaat #:    88");
  printer.print("Transactie #:  ");
  printer.println(transactionNo);
  //Account information
  printer.print("Rekening #:    XXXX-XX");
  printer.println(accountNo);
  
  //Card number
  printer.print("Pas #:         ");
  printer.println(cardNo);
  printer.print("Bedrag:        ");
  printer.print(amount);
  printer.println(",-");
  printer.justify('C');
  printer.underlineOn();
  printer.println(F("                                "));
  printer.underlineOff();
  printer.justify('L');
  //Ending with a greet
  printer.println("Bedankt voor het gebruiken van  de services van ABN-MANBRO");
  printer.println("GRAAG TOT ZIENS");
  //Rolls out 
  printer.feed(5);
  

  printer.sleep();      // Tell printer to sleep
  delay(3000L);         // Sleep for 3 seconds
  printer.wake();       // MUST wake() before printing again, even if reset
  printer.setDefault(); // Restore printer to defaults
}

//Will try to receive the info needed for the money dispenser, in the form q,(notes50),(notes20),(notes10) and turn the motor
//respectively 
void moneyDispenser(){
  while(!(notes50 != -1 && notes20 != -1 && notes10 != -1)){
    while (!Serial.available());
    x = Serial.readString();
    x = String(x);
    if(x != ""){
      if(x.indexOf("q") > -1){ //q = data
        String temp = x.substring(2);
        notes50 = temp.substring(0, 1).toInt();
        notes20 = temp.substring(2, 3).toInt();
        notes10 = temp.substring(4, 5).toInt();
        for(int j = 0; j < notes50; j++){
          rightMotorOneBill();
        }
        for(int j = 0; j < notes20; j++){
          centerMotorOneBill();
        }
        for(int j = 0; j < notes10; j++){
          leftMotorOneBill();
        }
      }
    }
  }
}

//Turns the left motor ones
void leftMotorOneBill() {
  stepperMotorLeft.step(-stepsPerRotation);
}

//Turns the center motor ones
void centerMotorOneBill() {
  stepperMotorCenter.step(-stepsPerRotation);  
}

//Turns the right motor ones
void rightMotorOneBill() {
  stepperMotorRight.step(stepsPerRotation);
}
