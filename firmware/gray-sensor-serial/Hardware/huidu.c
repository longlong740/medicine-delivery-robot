#include "stm32f10x.h"                  // Device header
#include <stdio.h>
#include <stdarg.h>
#include "huidu.h"
uint8_t sensor_val[5];//灰度返回值


void huidu_Init(void)
{
	    GPIO_InitTypeDef GPIO_InitStructure;

    // 1. 使能GPIOA时钟
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOB, ENABLE);

    // 2. 配置PA3、PA4、PA5、PA6、PA7
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3 | GPIO_Pin_4 | GPIO_Pin_5 | GPIO_Pin_6 | GPIO_Pin_7;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU; // 上拉输入模式
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;    // 
    GPIO_Init(GPIOA, &GPIO_InitStructure);
}



uint16_t Sensor_GetState(void)
{
    int state = 0;
    state |= (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_4) << 4); // PA3 对应位 4
    state |= (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_3) << 3); // PA4 对应位 3
    state |= (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_5) << 2); // PA5 对应位 2
    state |= (GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_6) << 1); // PA6 对应位 1
    state |= GPIO_ReadInputDataBit(GPIOA, GPIO_Pin_7);       // PA7 对应位 0

    return state;
	
}


//将整形转成字符串，方便串口打印输出
char* StateToString(u8 state)
{
    static char state_str[6]; // 静态数组保存结果
    
    for (int i = 0; i < 5; i++) {
        // 从高位到低位处理PA3-PA7的传感器状态
        // 注意：低电平有效需要取反显示
        uint8_t bit = (state >> (4 - i)) & 0x01; // 提取第i位
        state_str[i] = (bit) ? '0' : '1';      // 低电平显示'1'
    }
    state_str[5] = '\0'; // 字符串终止符
    
    return state_str;
}


////功  能：循迹调整函数
////形  参：无
////返回值： 无
////说  明：根据获取到的传感器输出状态，进行左右电机的速度调整
////******/
//void Track_Adjust(void)
//{
//	u8 flag = 1;//是否复位标志
//	u8 state = 0;//状态获取变量定义
//	
//	while(flag)
//	{
//		state = Get_Infrared_State();//获取传感器状态
//		switch(state)
//		{
//			case 0x00000: 
//			case 0x10001: 
//			case 0x00001: 
//			case 0x10000: Motor_Speed_Adjust(0,0); break;//停止

//			case 0x10011: Motor_Speed_Adjust(STARTER_SPEED-100,STARTER_SPEED+100); break;//右偏1级
//			case 0x10111: Motor_Speed_Adjust(STARTER_SPEED-250,STARTER_SPEED+250); break;//右偏2级
//			case 0x00111: Motor_Speed_Adjust(STARTER_SPEED-400,STARTER_SPEED+400); break;//右偏3级
//			case 0x01111: Motor_Opposite(L); break;//右偏4级，

//			case 0x11001: Motor_Speed_Adjust(STARTER_SPEED+100,STARTER_SPEED-100); break;//左偏1级
//			case 0x11101: Motor_Speed_Adjust(STARTER_SPEED+250,STARTER_SPEED-250); break;//左偏2级
//			case 0x11100: Motor_Speed_Adjust(STARTER_SPEED+400,STARTER_SPEED-400); break;//左偏3级
//			case 0x11110: Motor_Opposite(R); break;//左偏4级
//			
//			case 0x11011: Motor_Speed_Adjust(STARTER_SPEED,STARTER_SPEED);flag = 0; break;//正常
//			
//			case 0x11111: Motor_Speed_Adjust(0,0); break;
//			
//			default: Motor_Speed_Adjust(0,0); break;
//		}
//	}
//}
