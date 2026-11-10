# 附：Python 基础语法



Python 是一门**解释型、动态类型、缩进敏感**的语言，语法简洁易读。下面从最基础的规则开始，分模块讲解，附带示例。

>  运行方式：交互式环境（`python3`）、`.py` 脚本文件

## 一、基础格式规则

### 1. 缩进（最重要！）

Python **不用大括号 `{}` 划分代码块**，依靠**缩进**（一般4个空格，不要混用Tab和空格）。 同一代码块缩进必须一致。

```python
if 1 > 0:
    print("条件成立")   # 缩进，属于if内部
print("这句话不属于if") # 顶格
```

> ❌ 缩进不一致会直接报 `IndentationError`

### 2. 注释

```python
# 单行注释：# 后面的内容不会执行

"""
多行字符串注释（本质是字符串，常用来做多行注释/文档字符串）
第二行
第三行
"""

'''单引号也可以多行注释'''
```

### 3. 语句换行

- 一行一条语句，不需要分号 `;`

- 一行写多条：用分号隔开（不推荐）

  ```python
  a = 1; b = 2
  ```

- 语句太长换行：

  ```python
  \
  ```

   或者括号自动换行

  ```python
  total = 1 + 2 + 3 + \
          4 + 5 + 6
  # 括号内可以直接换行，不用 \
  total = (1 + 2 + 3 +
           4 + 5 + 6)
  ```

### 4. 标识符（变量名）命名规则

- 只能由 **字母、数字、下划线 `_`** 组成
- **不能以数字开头**
- 区分大小写：`Name` 和 `name` 是两个变量
- 不能是关键字（保留字）
- 约定：
  - 变量/函数：`snake_case` 下划线命名 `user_name`
  - 类名：大驼峰 `UserName`
  - 常量：全大写 `MAX_NUM`

Python 关键字（不能用作变量名）：

```python
False, None, True, and, as, assert, async, await, break, class, continue,
def, del, elif, else, except, finally, for, from, global, if, import, in,
is, lambda, nonlocal, not, or, pass, raise, return, try, while, with, yield
```

------

## 二、变量与数据类型

Python 是**动态类型**：不需要提前声明类型，赋值时自动确定类型。

```python
a = 10        # 直接赋值，不用写 int a;
a = "hello"   # 同一个变量可以存不同类型
```

### 常用内置数据类型

1. **整数 int**：`10, -99, 0`，支持二进制`0b101`、八进制`0o12`、十六进制`0xff`

2. **浮点数 float**：`3.14, -0.5, 1e3`（科学计数法）

3. 布尔 bool：只有两个值 （首字母大写）

   - 假值：`0, 0.0, "", [], {}, None` 都会被当作False

4. 字符串 str：单引号、双引号、三引号

   ```python
   s1 = 'hi'
   s2 = "hello"
   s3 = """多行
   文本"""
   ```

5. 列表 list：有序可变，[]
   ```python
   lst = [1, 2, "abc", True]
   ```

6. 元组 tuple：有序不可变，()
   ```python
   t = (1, 2, 3)
   ```

7. 字典 dict：键值对，{key:value}，key不可变、唯一
   ```python
   d = {"name":"小明", "age":18}
   ```

8. 集合 set：无序、元素不重复，{} / set()
   ```python
   s = {1,2,3}
   ```

9. **NoneType**：`None`，代表空，不是0也不是空字符串

​			查看类型：`type()`

   ```python
print(type(10))  # <class 'int'>
   ```

​			类型转换：

   ```python
int("123")
str(123)
float("3.14")
list((1,2))
   ```

------

## 三、运算符

### 1. 算术运算符

| 符号 | 说明               | 示例    |
| ---- | ------------------ | ------- |
| `+`  | 加                 | 3+2=5   |
| `-`  | 减                 | 3-2=1   |
| `*`  | 乘                 | 3*2=6   |
| `/`  | 除（结果float）    | 5/2=2.5 |
| `//` | 地板除（向下取整） | 5//2=2  |
| `%`  | 取余               | 5%2=1   |
| `**` | 幂运算             | 2**3=8  |

### 2. 赋值运算符

```python
= += -= *= /= //= %= **=
a = 1
a += 2  # a = a + 2
```

### 3. 比较运算符，返回布尔值

```python
> < >= <= == !=
```

> `==` 判断相等；`=` 是赋值！

```python
print(3 == 3)   # True
print(3 != 2)   # True
```

### 4. 逻辑运算符

`and`、`or`、`not`（不是 && || !）

```python
a = 10
print(a > 5 and a < 20)
print(a < 5 or a > 0)
print(not a < 0)
```

> 短路特性：and前面为假直接返回前面；or前面为真直接返回前面

### 5. 成员运算符

`in` / `not in`：判断元素是否在序列、集合、字典键中

```python
print("a" in "abc")
print(1 not in [2,3])
```

### 6. 身份运算符

`is` / `is not`：判断是不是同一个对象（内存地址是否相同）

> ⚠️ `is` 和 `==` 不一样：`==` 比较值，`is` 比较id

```python
a = [1,2]
b = [1,2]
print(a == b) # True 值相等
print(a is b) # False 不是同一个对象
```

------

## 四、输入输出

### print() 输出

```python
print("hello")
print(1, 2, 3)          # 多个值默认空格分隔
print(1,2,3, sep="-")   # 指定分隔符
print("加载中...", end="") # 不换行
```

格式化输出（3种常用）

```python
name = "小明"
age = 18
# f-string（推荐，Python3.6+）
print(f"名字：{name}，年龄：{age}")
# format
print("名字：{}，年龄：{}".format(name, age))
# %格式化（老写法）
print("名字：%s，年龄：%d" % (name, age))
```

### input() 输入

**input接收的永远是字符串！**

```python
content = input("请输入：")
num = int(input("输入数字：")) # 转成数字
```

------

## 五、流程控制：分支 if

语法：`if` → `elif` → `else`，`elif` 可以多个，else可选

```python
score = 80
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

- 条件后面必须加冒号 `:`
- 支持嵌套if

**三元表达式（简化if-else）**

```python
a = 10
b = 20
res = a if a > b else b
print(res)
```

------

## 六、流程控制：循环 for / while

### 1. while 循环

适合不知道循环次数的场景

```python
i = 1
while i <= 5:
    print(i)
    i += 1
```

`while + else`：循环正常结束（不是break打断）会执行else

```python
i = 1
while i <=3:
    print(i)
    i +=1
else:
    print("循环正常结束")
```

### 2. for 循环

遍历可迭代对象（字符串、列表、元组、range等）

```python
# range(起始,终止,步长)，左闭右开
for i in range(1, 6):
    print(i)

for char in "python":
    print(char)

for item in [10,20,30]:
    print(item)
```

for 同样支持 `else`

### 循环控制关键字

- `break`：立刻终止整个循环
- `continue`：跳过本次循环剩余代码，进入下一轮
- `pass`：空语句，占位，什么都不做（语法需要但暂时不写代码时用）

```python
for i in range(10):
    if i == 3:
        break
    print(i)
```

------

## 七、函数基础 def

用 `def` 定义函数，冒号+缩进

```python
# 定义
def add(a, b):
    c = a + b
    return c  # return 返回结果，没有return默认返回None

# 调用
res = add(2,3)
print(res)
```

参数类型：

1. 位置参数
2. 关键字参数 `add(a=1,b=2)`
3. 默认参数 `def func(x, y=10):`
4. 可变参数 `*args`（打包成元组）、`**kwargs`（打包成字典）

```python
def demo(*args, **kwargs):
    print(args)
    print(kwargs)
demo(1,2,3, name="小明")
```

作用域：

- **局部变量**：函数内部定义，外面访问不到
- **全局变量**：函数外面；函数内修改全局需要 `global`

```python
a = 100
def test():
    global a
    a = 200
test()
print(a)
```

------

## 八、字符串、列表、字典常用基础操作

### 字符串 str

字符串不可变，不能直接修改某个字符

```python
s = "python"
print(s[0])      # 索引取值 p
print(s[1:4])    # 切片 yth [起始:结束:步长]
print(len(s))    # 长度
print(s.upper()) # 大写
print(s.split()) # 分割
print("hi"+" there") # 拼接
```

### 列表 list（可变）

```python
lst = [1,2,3]
lst.append(4)    # 尾部追加
lst.insert(0,99) # 指定位置插入
lst.pop()        # 删除并返回末尾元素
lst.remove(2)    # 删除第一个匹配值
lst[0] = 100     # 修改
```

### 字典 dict

```python
d = {"name":"小红"}
print(d["name"])
d["age"] = 18    # 新增/修改键值
print(d.get("age", 0)) # 获取，不存在返回默认值
print(d.keys())
print(d.values())
print(d.items())
```

------

## 九、导入模块 import

```python
# 方式1
import math
print(math.sqrt(4))

# 方式2：from ... import
from math import pi
print(pi)

# 别名
import math as m
```

------

## 十、异常捕获 try-except

防止程序遇到错误直接崩溃

```python
try:
    num = int(input("输入数字："))
    print(num)
except ValueError:
    print("你输入的不是数字！")
finally:
    print("无论是否报错都会执行")
```



# 配套基础练习题（含答案）

> 说明：题目顺序和上面讲解顺序对应，难度由浅到深，全部可以直接复制到Python运行。 做题建议：先自己写代码，再看答案。

## 一、基础格式、注释、变量

### 第1题

请写出3种注释方式的示例代码。

答案：

```python
# 单行注释：打印hello
print("hello")

"""
多行注释1
第二行
"""

'''
多行注释2
'''
```

### 第2题

下面哪些变量名合法？ `1name`、`name_1`、`user-name`、`_age`、`if`

答案：

合法：`name_1`、`_age` 

不合法：

- `1name`：数字开头
- `user-name`：包含减号
- `if`：关键字

### 第3题

定义变量 name = "张三"，age = 20，用f-string格式化输出：`我的名字是张三，今年20岁`

答案：

```python
name = "张三"
age = 20
print(f"我的名字是{name}，今年{age}岁")
```

------

## 二、数据类型 & 类型转换

### 第4题

写出下面代码输出结果：

```python
a = 10
b = 3.14
c = True
print(type(a), type(b), type(c))
```

答案：

```python
<class 'int'> <class 'float'> <class 'bool'>
```

### 第5题

输入一个字符串数字 `s = "66"`，把它转为整数，再加10，打印结果。

答案：

```python
s = "66"
num = int(s)
res = num + 10
print(res)  # 76
```

### 第6题

判断：空字符串 `""`、0、`None`、`[]` 在if条件中是 True 还是 False？

答案： 全部为 False

------

## 三、运算符

### 第7题

计算并写出结果：

```python
print(7 / 2)
print(7 // 2)
print(7 % 2)
print(2 ** 4)
```

答案：

```
3.5
3
1
16
```

### 第8题

```python
a = 10
a += 5
print(a)
```

输出？

答案： 15

### 第9题

```python
print(3 > 1 and 5 < 2)
print(3 > 1 or 5 < 2)
print(not 3 > 1)
```

输出？

答案：

```python
False
True
False
```

### 第10题

`==` 和 `is` 的区别？下面代码输出？

```python
list1 = [1,2]
list2 = [1,2]
print(list1 == list2)
print(list1 is list2)
```

答案： `==` 比较值；`is` 比较内存地址（是否同一个对象） ``` True False ```

------

## 四、输入输出 input / print

### 第11题

接收用户输入两个数字，求和并打印。

> 提示：input拿到的是字符串，要转int

答案：

```python
n1 = int(input("请输入第一个数字："))
n2 = int(input("请输入第二个数字："))
print(n1 + n2)
```

------

## 五、分支 if

### 第12题

输入分数，判断：≥90优秀，≥60及格，否则不及格

答案：

```python
score = float(input("输入分数："))
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

### 第13题

用三元表达式：比较a=18，b=25，输出较大的值

答案：

```python
a = 18
b = 25
max_num = a if a > b else b
print(max_num)
```

------

## 六、循环 for / while + break / continue

### 第14题

while循环：打印1~5

答案：

```python
i = 1
while i <= 5:
    print(i)
    i += 1
```

### 第15题

for + range：打印1~10之间所有偶数

答案：

```python
for i in range(1, 11):
    if i % 2 == 0:
        print(i)
```

另一种写法（步长）：

```python
for i in range(2, 11, 2):
    print(i)
```

### 第16题

循环 0~9，遇到 i == 5 的时候用 break 结束循环

答案：

```python
for i in range(10):
    if i == 5:
        break
    print(i)
# 输出：0 1 2 3 4
```

### 第17题

循环0~9，遇到 i==5 时 continue，跳过本次

答案：

```python
for i in range(10):
    if i == 5:
        continue
    print(i)
# 输出0,1,2,3,4,6,7,8,9 没有5
```

### 第18题

求 1 到 100 的累加和（for循环）

答案：

```python
s = 0
for i in range(1,101):
    s += i
print(s) # 5050
```

------

## 七、函数 def

### 第19题

定义函数 mul(a,b)，返回两个数乘积，调用 mul(3,4)

答案：

```python
def mul(a, b):
    return a * b

res = mul(3,4)
print(res)
```

### 第20题

写一个函数，参数带默认值：`def greet(name, msg="你好")`，测试两种调用方式

答案：

```python
def greet(name, msg="你好"):
    print(f"{msg}，{name}")

greet("小明")
greet("小红", "早上好")
```

### 第21题

全局变量练习：

```python
num = 10
def change():
    global num
    num = 100
change()
print(num)
```

输出？

答案： 100

------

## 八、字符串、列表、字典

### 第22题

```python
s = "python"
print(s[0])
print(s[2:5])
print(len(s))
```

输出？

答案： ``` p tho 6 ```

### 第23题

列表操作：创建列表 `lst = [1,2,3]`，追加4，删除2，打印最终列表

答案：

```python
lst = [1,2,3]
lst.append(4)
lst.remove(2)
print(lst) # [1, 3, 4]
```

### 第24题

字典操作：`stu = {"name":"小李","age":19}`

1. 获取name的值
2. 修改age为20
3. 添加键 `gender`，值为 `"男"`

答案：

```python
stu = {"name":"小李","age":19}
print(stu["name"])
stu["age"] = 20
stu["gender"] = "男"
print(stu)
```

------

## 九、模块导入 & 异常捕获

### 第25题

导入math模块，计算 9 的平方根

答案：

```python
import math
print(math.sqrt(9)) # 3.0
```

### 第26题

捕获异常：尝试把用户输入转为int，如果输入不是数字，提示“输入不是整数”

答案：

```python
try:
    n = int(input("请输入整数："))
    print("输入成功，数字是", n)
except ValueError:
    print("输入不是整数")
```

------

## 综合大题（实战）

### 第27题【猜数字简化版】

程序内置数字 secret = 28，让用户输入数字：

- 大了提示：太大
- 小了提示：太小
- 等于提示：猜对了，结束

答案：

```python
secret = 28
guess = int(input("猜一个数字："))
if guess > secret:
    print("太大")
elif guess < secret:
    print("太小")
else:
    print("猜对了！")
```

进阶版（循环可以一直猜直到猜对）：

```python
secret = 28
while True:
    guess = int(input("猜数字："))
    if guess > secret:
        print("太大")
    elif guess < secret:
        print("太小")
    else:
        print("猜对了！")
        break
```

# 进阶综合自测练习题

> 适合做完前面基础题之后自测，综合性更强，会融合多个知识点；建议先独立写代码，再看答案。 难度：中等，覆盖：判断、循环、字符串、列表、字典、函数、异常。

## 1. 字符串处理题

题目：输入一句话，统计里面英文字母、数字、其他字符的数量，分别打印出来。 示例输入：`abc123!!你好` 示例输出： 字母：3 数字：3 其他：4

答案：

```python
s = input("请输入一段文本：")
letter = 0
digit = 0
other = 0
for ch in s:
    if ch.isalpha() and ch.isascii():
        letter += 1
    elif ch.isdigit():
        digit += 1
    else:
        other += 1
print(f"字母：{letter}")
print(f"数字：{digit}")
print(f"其他：{other}")
```

------

## 2. 列表去重+排序

题目：给定列表 `nums = [5,2,8,2,5,9,8,1]`，去除重复元素，从小到大排序，输出结果。

答案：

```python
nums = [5,2,8,2,5,9,8,1]
# 转集合去重，再转回列表排序
new_nums = list(set(nums))
new_nums.sort()
print(new_nums)
# 输出 [1, 2, 5, 8, 9]
```

> 拓展：如果**要求保留原有顺序**，不能直接用set，需要另一种写法：

```python
nums = [5,2,8,2,5,9,8,1]
res = []
for i in nums:
    if i not in res:
        res.append(i)
print(res)
```

------

## 3. 函数：判断素数

题目：写一个函数 `is_prime(n)`，判断一个数字是不是素数（质数），是返回True，不是返回False。

> 素数：大于1，只能被1和自己整除的整数。然后调用这个函数，打印 1~50 之间所有素数。

答案：

```python
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

# 输出1~50所有素数
for num in range(1, 51):
    if is_prime(num):
        print(num, end=" ")
```

------

## 4. 字典综合：学生成绩管理

题目：有学生字典

```python
stu_dict = {"小明":88, "小红":92, "小刚":76, "小李":92}
```

要求：

1. 找出最高分
2. 打印所有最高分的学生名字

答案：

```python
stu_dict = {"小明":88, "小红":92, "小刚":76, "小李":92}
scores = stu_dict.values()
max_score = max(scores)
print("最高分：", max_score)
print("最高分同学：")
for name, score in stu_dict.items():
    if score == max_score:
        print(name)
```

------

## 5. 循环+分支：九九乘法表

题目：用for循环打印九九乘法表，格式整齐。

答案：

```python
for i in range(1, 10):
    for j in range(1, i+1):
        print(f"{j}*{i}={i*j}", end="\t")
    print()
```

------

## 6. 异常处理综合

题目：循环接收用户输入数字，不断求和； 用户输入 `q` 代表退出程序，打印总和； 如果输入不是数字也不是q，捕获异常，提示输入错误，继续循环。

答案：

```python
total = 0
while True:
    content = input("请输入数字，输入q结束：")
    if content == "q":
        break
    try:
        num = float(content)
        total += num
    except ValueError:
        print("输入有误！请输入数字或者q")
print("总和 = ", total)
```

------

## 7. 列表推导式（进阶语法）

题目：使用列表推导式，生成1~20中所有3的倍数组成的列表。

答案：

```python
lst = [x for x in range(1,21) if x % 3 == 0]
print(lst)
# [3, 6, 9, 12, 15, 18]
```

------

## 8. 综合小项目：密码校验

题目：写程序，输入密码，满足下面全部条件才算合法：

1. 长度不少于6位
2. 必须包含至少1个数字
3. 必须包含至少1个英文字母。合法输出`密码合法`，不合法输出对应的原因。

答案：

```python
pwd = input("请输入密码：")
has_num = False
has_alpha = False

for ch in pwd:
    if ch.isdigit():
        has_num = True
    if ch.isalpha():
        has_alpha = True

if len(pwd) < 6:
    print("密码长度不足6位")
elif not has_num:
    print("密码必须包含数字")
elif not has_alpha:
    print("密码必须包含字母")
else:
    print("密码合法")
```

------

## 9. 翻转字符串（两种方法）

题目：输入字符串，输出翻转后的字符串。 例如输入 `hello`，输出 `olleh`。要求：①切片写法 ②循环写法

答案：

```python
s = input("输入字符串：")
# 方法1 切片（最简单）
res1 = s[::-1]
print("切片翻转：", res1)

# 方法2 for循环
res2 = ""
for i in s:
    res2 = i + res2
print("循环翻转：", res2)
```

------

## 10. 终极综合题：猜数字升级版

题目：

- 程序随机生成1~100之间的整数

- 用户循环猜数字，提示大了、小了

- 猜对提示恭喜，并统计一共猜了多少次

  > 提示：需要 random 模块

答案：

```python
import random
secret = random.randint(1,100)
count = 0
while True:
    try:
        guess = int(input("猜1-100数字："))
        count += 1
        if guess > secret:
            print("太大了")
        elif guess < secret:
            print("太小了")
        else:
            print(f"恭喜猜对！一共猜了{count}次")
            break
    except ValueError:
        print("请输入有效整数！")
```

# 自测打分参考

- 能独立写出 7题以上：基础掌握很不错，可以继续学文件、面向对象
- 4~6题：基础熟悉，但循环、函数、字典需要多加练习
- 少于4题：建议回头重做前面基础练习题