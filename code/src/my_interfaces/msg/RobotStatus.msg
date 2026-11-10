# 机器人状态：上层看板用
# string status  状态文本：idle / moving / error 等
# float32 battery  电量百分比 0~100
# uint8 mode  模式编号 0=manual 1=auto 2=sport（与 SetMode 服务的合法模式一致）
# builtin_interfaces/Time stamp  时间戳

string status
float32 battery
uint8 mode
builtin_interfaces/Time stamp
