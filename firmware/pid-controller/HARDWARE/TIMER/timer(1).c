#include "timer.h"
#include "pid.h"

void TIM2_Init(u16 arr,u16 psc)
{
	NVIC_InitTypeDef NVIC_InitStructure;
	TIM_TimeBaseInitTypeDef  TIM_TimeBaseStructure;//GPIO初始化，定时器初始化，初始化外部中断
	
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_TIM2, ENABLE);
	
	//溢出时间tim=(arr+1)*(psc+1)/72000000	50000*72/72000000=500ms
	TIM_TimeBaseStructure.TIM_Period = arr;
	TIM_TimeBaseStructure.TIM_Prescaler = psc;
	TIM_TimeBaseStructure.TIM_ClockDivision = TIM_CKD_DIV1; 
	TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;//向上计数
	TIM_TimeBaseInit(TIM2, &TIM_TimeBaseStructure); 
	
	TIM_ITConfig(TIM2,TIM_IT_Update,ENABLE);//使能中断	
	NVIC_InitStructure.NVIC_IRQChannel = TIM2_IRQn;  
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 1;  //先占优先级2级
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;  //从优先级0级
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE; //IRQ通道被使能
	NVIC_Init(&NVIC_InitStructure); 
	
	TIM_Cmd(TIM2, ENABLE);
}

float v_real=0;
float val=0;

float Kp=0.0;//
float Ki=10.0;//
float Kd= 0;
int target=15;
int err_now=0;
int err_last=0;
int err_last_last=0;
int spd_now=0;
int err_i=0;
int jisuan=0;
int out=0;

void TIM2_IRQHandler(void)
{
	if(TIM_GetITStatus(TIM2, TIM_IT_Update) != RESET)
	{
		int cnt;
		cnt=TIM4->CNT-0x7fff;
		TIM4->CNT=0x7fff;
		v_real=cnt*1.0;

		//位置式
//		spd_now=cnt;
//		err_now=target-spd_now;
//		err_i+=err_now;
//		if(err_i>19000) err_i=19000;
//		out=Kp*err_now+Ki*err_i+Kd*(err_now-err_last);
//		if(out>19000) out=19000;
//		TIM_SetCompare1(TIM3,out);
//		err_last=err_now;
		
		//增量式		
//		spd_now=cnt;
//		err_now=target-spd_now;
//		jisuan=Kp*(err_now-err_last)+Ki*err_now+Kd*(err_now+err_last_last-2*err_last);
//		out+=jisuan;		
//		if(out>19000) out=19000;		
//		TIM_SetCompare1(TIM3,out);		
//		err_last_last=err_last;
//		err_last=err_now;
	}
    TIM_ClearITPendingBit(TIM2, TIM_IT_Update); //清除中断标志位
}