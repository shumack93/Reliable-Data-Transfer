# Reliable-Data-Transfer

Created a "reliable" data transfer layer that allows the transfer of string data over an unreliable 
channel when various unreliable flags are enabled (i.e. timeouts, dropped packets, etc.) using Python.

Code for unreliable.py and rdt_main.py were provided. Code was written by me in rdt_layer.py in order
to implement the reliable data transfer layer.


How to run the program:

- rdt_main.py – 2 options (a or b):

   - a. You can download the 3 attached Python files (rdt_main.py, rdt_layer.py, and
unreliable.py) and add them to a new project in a Python IDE and run rdt_main.py. I
used PyCharm to develop and test this program, so it will work there.

   - b. You can also run the program locally through the command prompt on Windows. To do this,
navigate to the command prompt. Then, run the following command:
(python.exe path) *space* (traceroute.py path)

     - For option B, my command looks like the following:

       C:\Users\criss>PycharmProjects\Project2\venv\Scripts\python.exe PycharmProjects/Project2/rdt_main.py
