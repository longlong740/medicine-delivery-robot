#ifndef __HUIDU_H
#define __HUIDU_H

#include <stdio.h>

#define L2 GPIO_ReadInputDataBit(GPIOA,GPIO_Pin_3)
#define L1 GPIO_ReadInputDataBit(GPIOA,GPIO_Pin_4)
#define M0 GPIO_ReadInputDataBit(GPIOA,GPIO_Pin_5)
#define R1 GPIO_ReadInputDataBit(GPIOA,GPIO_Pin_6)
#define R2 GPIO_ReadInputDataBit(GPIOA,GPIO_Pin_7)



void huidu_Init(void);
uint16_t Sensor_GetState(void);
char* StateToString(u8 state);
#endif
