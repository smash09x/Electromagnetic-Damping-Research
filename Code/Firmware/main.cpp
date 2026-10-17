#include <Arduino.h>

#define ADC_PIN 26
#define BUTTON_PIN 18
#define SWITCH_PIN 27

const int Sample_Interval = 10; //take 100k samples every second //might need to reduce this dowm to a stable 50k samples (Sample_Interval = 20) if the output is missing ticks
const int Output_Interval = 1000; //output only 1k of those samples every second
const int Max_Samples = 60000; // 60 seconds max limit since array needs to have a max size //you CAN push this to 90 seconds if you want
const int Oversample_Factor = Output_Interval/Sample_Interval;

// first store in RAM using arrays, then send through serial monitor
uint16_t adcStorage[Max_Samples];
//unsigned long timeStorage[Max_Samples]; 

unsigned long tempStorage; //to store raw ADC values of all the samples we wont be using but we will average out
int Oversample_Count;

void setup() {
  Serial.begin(115200);
  pinMode(ADC_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(SWITCH_PIN, INPUT);
  analogReadResolution(12); //telling the ADC to give outputs in 12 bits because otherwise it only gives it in 10 bits
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(50); //debounce
    
    Serial.println("STARTING CAPTURE..."); 
    
    int sampleCount = 0;
    unsigned long previousMicros = micros();
    tempStorage = 0;
    Oversample_Count = 0;

    
    while (digitalRead(BUTTON_PIN) == LOW && sampleCount < Max_Samples) { //oversample
      unsigned long currentMicros = micros(); //this is gonna be tracking the time in real time since its in a loop
      
      if ((unsigned long)(currentMicros - previousMicros) >= Sample_Interval) { //forcing the calculation to give an unsigned long as a result so that the calculation can never be negative, explained at the bottom
        previousMicros += Sample_Interval;
        
        tempStorage += analogRead(ADC_PIN); //take a bunch of samples
        Oversample_Count++;

        if (Oversample_Count >= Oversample_Factor){ 
          
         // timeStorage[sampleCount] = currentMicros - startTime; //so time starts from 0
          
          adcStorage[sampleCount] = (uint16_t) (tempStorage/Oversample_Factor); //averages all those samples that we took to remove the noise

          sampleCount++;
          tempStorage = 0;
          Oversample_Count = 0;
        }
      }
    }

    //sending data through serial once button was released
    Serial.flush();
    Serial.println("BUTTON RELEASED, DUMPING DATA...");
    delay(10); // gemini told me to add this // apparently it needs a little time so it can remove this string from the queue so it can start outputting the data

    //converting from steps to volts, change these accordingly
    const float  gain = 35.0; //change this accordingly depending on how large your emf produced is, ensuring that the (EMF produced * gain) + 1.65  does not exceed 0-3.3v
    const float refVoltage = 1.65; //op amp voltage when magnet is not near the coil
    const float sourceVoltage = 3.3; //pi pico voltage, its actually most of the times not exactly 3.3v
    
    //send ONLY the number of samples collected during the hold duration so sending sample count instead of Max_Samples
    for (int i = 0; i < sampleCount; i++) {
      unsigned long timeMicroSecond = (unsigned long) i * Output_Interval;
      
      float avgADC = (float) adcStorage[i];
      float pinVoltage = (avgADC / 4095.0) * sourceVoltage; //4095 cuz 2^12 = 4096 possible steps
      float voltageMicroVolts = ((pinVoltage - refVoltage) / gain) * 1000000.0; //removing the bias, removing the gain, converting to micro volts
      
      //if (digitalRead(SWITCH_PIN) == HIGH){
      Serial.print(timeMicroSecond);
      Serial.print(",");
      Serial.println(voltageMicroVolts);
     // }
     // else if (digitalRead(SWITCH_PIN) == LOW){
      //  Serial.println(voltageMicroVolts);
     // }
    }

    Serial.println("DONE.");
    
    //this is in the case that the max time limit has been reached and the button is still being pressed, so the whole thing would just start again and wipe all of the previous data
    while(digitalRead(BUTTON_PIN) == LOW); 
  }
}


/* why use the (unsigned long) before the operation? its called "Type Casting"
 an unsigned long box can hold numbers up to 4,294,967,295
 since micros() counts microseconds constantly, after about 71.5 minutes, the Picos background clock hits that maximum limit
 runs out of bit-space, and overflows back to absolute 0
 Imagine the experiment happens right at the 71.5-minute mark:
 previousMicros took a snapshot right before the roll-over: 4,294,966,500 
 currentMicros ticks forward a bit, overflows, and resets to: 200
 If you do standard math: 200 - 4,294,966,500 = -4,294,966,300$. That negative number completely ruins your timer logic!
 so we decide not do standard math and do unsigned binary math and then 200 - 4,294,966,500$ automatically wraps through binary space to equal exactly 996 microseconds
 even though ill never actually keep repeating the experiment for this long its a good bit of logic to know for future
 */

//might want to add a glitch filter to ensure the pushbutton is not released due to bouncing
