#include "stm32f10x.h"                  // Device header
#include "Delay.h"
#include "OLED.h"
#include "Serial.h"
#include "huidu.h"



char* state_str1;
uint8_t sensor_state;
int main(void)
{
	huidu_Init();
	Serial_Init();
	while (1)
	{

		sensor_state= Sensor_GetState(); // 
		state_str1 = StateToString(sensor_state);
		Serial_Printf("GPIO State: %s\n", state_str1); // œ‘ æ "01001"
Delay_ms(50);
	}
}
