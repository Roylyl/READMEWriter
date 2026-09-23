# TemperatureKit

现有测试记录仅覆盖 Python 3.11 下的零摄氏度转换。

## 安装与调用

从仓库根目录执行 `python -m pip install .`。

```python
from temperaturekit import celsius_to_fahrenheit
print(celsius_to_fahrenheit(0))
```

函数实现见 [模块](temperaturekit/__init__.py)，运行时声明见 [项目配置](pyproject.toml)。其他输入和运行时尚无测试记录。
