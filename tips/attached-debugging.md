# Debugging Nuke Scripts in PyCharm
Debugging python scripts inside of nuke can be quite annoying. Unfortunately Nuke doesn't
Provide a debugger inside of nuke. Therefore, you need to use an external tool like 
PyCharm.
Jordan Olson has a nice article on how to setup debugging for Eclipse. If this is 
your tool of choice, take a look at his post on nukepedia:
http://www.nukepedia.com/written-tutorials/debugging-python-code-in-nuke-with-eclipse-step-through-like-a-pro

In my case I want to use PyCharm. I only tested this on windows right now. But I 
hope this will work on other platforms as well. If not, please let me know :)

### Pre-requirements (sort of):
- Windows 10
- Nuke 13.2
- Pycharm 2021.3.1 (Community Edition does work)
### Setup PyCharm
- Open the preferences and search for **'attach'**
- Click on **Python Debugger**
- Remove the **'python'** entry of the textbox with the label: 
  - *For Attach To Pocess show processes with names containing:*
## Steps to connect PyCharm and Nuke:
- Open Nuke (obviously)
- Run the following command:
  ```python
  import os
  print(os.getpid())
  ```
- Copy the output PID (process id) 
- In PyCharm:
  - Go to the menu: Run>Attach to Process... 
  - Paste the copied PID and hit enter
  - PyCharm should now connect with Nuke
## Test the debugger
Simply run the following code:
```python
print('Hello Debugger')
```
You should see the output on the debugger console in PyCharm. 
If you run scripts that are opened inside PyCharm, you can define breakpoints 
and use all debugging features from PyCharm.
## Current Limitations
- The debugger can't be reactivated if it was stopped in the same Nuke session 
- Raising errors will crash Nuke when the script is resumed in PyCharm