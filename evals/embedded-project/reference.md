# BoardBlink

记录显示 ESP-IDF v5.3 下 ESP32-S3 目标构建通过。

## 构建与硬件状态

目标见 [sdkconfig.defaults](sdkconfig.defaults)，LED 引脚定义为 GPIO 4，见 [pins.h](main/pins.h)。未提供具体板型、供电和完整构建工程；烧录与实机行为尚未验证，不能直接给出适用于任意板卡的接线与烧录步骤。
