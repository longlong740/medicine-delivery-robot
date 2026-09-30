# 智能送药小车｜电子设计竞赛

本科竞赛团队代码整理稿，包含 K210 视觉端程序和 STM32F10x 控制代码片段。

## 目录

- vision/上位机最终代码.py：视觉端主程序。
- vision/experiments：K210 拍照辅助程序和模型环境中的另一份 Python 程序。
- firmware/pid-controller：PID、电机相关传感器与控制模块，以及下位机入口程序。
- firmware/gray-sensor-serial：灰度传感器串口调试工程。

## 运行与构建

视觉主程序运行在 K210/MaixPy 环境，并需要对应的模型文件；模型权重和采集图片没有放入本仓库。

固件使用 STM32F10x 工程配置。STM32 标准外设库、CMSIS 和部分板级支持代码没有随本仓库发布，需要按对应提供方的条款获取。代码没有在本仓库环境中重新构建，也没有连接实物验证。

## 许可证

团队编写的项目代码按 MIT License 发布。第三方组件继续遵循其自身条款，见 THIRD_PARTY_NOTICES.md。
