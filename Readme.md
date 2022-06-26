<div align = "center"> <h1>Collaborative Real-Time Text Editor</h1></div>
<hr>
<br><br>

## Collaborators:
---
<br>
<div align = "center"> <h3>Team 28<h3></div><br>
<div align = "center"> Adel Asaad Sarofeim &nbsp&nbsp&nbsp&nbsp 18P2949</div><br>
<div align = "center"> Marwan Atef Hamed   &nbsp&nbsp&nbsp&nbsp 18P8678</div><br>
<div align = "center"> Moataz Alaa Hamed   &nbsp&nbsp&nbsp&nbsp 19P6238</div><br>
<div align = "center"> Mohamed Adel Lotfy  &nbsp&nbsp&nbsp&nbsp 18P1724</div><br>

---
<br>

## Description :
---
<br>
Real-time text editors have a great market value for their great importance in reducing communication delays greatly. Therefore, we built our text editors putting in mind all the functional and non-functional requirements required to make a project of that scale with features similar to actual applications of that type (Google Docs for example).<br><br>This Project was built with the course topic in mind ***Distributed Computing***, so in order to achieve some-how fully distributed system the system consists of 3 parts:
* Client
* Super Server (**SS**)
* Child Servers (**CS**)

As for how all these parts work together to give us the required performance:
1. User opens the application (**client.py**) which automatically keeps trying to connect to the **SS** until a connection is established.<br><br>
2. **SS** then starts checking on all **CS** to see which of them (if any) is online, upon finding an online server **SS** sends back to the user the IP address and PORT number of that **CS**. <br><br>
3. User is automatically rerouted to the given **CS** and that **CS** handles all of the user's requests which could be:
    * Opening a file for the user to edit.
    * Create a new file in the database.    ***SHOULD WE DELETE OR WE GONNA USE?***
    * Save the new text to the file permenantly. <br><br>

4. User has a thread always listening for replies from a similar thread in the **CS**, if no reply from the server within 15 seconds, The connection is closed and the user is rerouted back to the **SS** repeating step 2. <br><br>
5. When the user opens a file for the first time the **CS** checks if the **SS** has the **file text** stored inside.
    * if it has the text (meaning another server already started a connection) it does nothing.
    * if it doesn't have any text (This is the very connection ever), then a version of the file text is sent to be stored. <br><br>
6. When any user modifies the text, the **CS** sends to check if the new text is already stored inside the **SS**
    * if it is stored (another client made the same change at the same time), then ignore.
    * if it isn't stored then the **SS** publishes the new updated text to all other **CS** to update their text to the newest version.<br><br>

---
<br>

## Prerequisites :
---
<br>

* You need to have python 3 installed on your device, If you don`t have it you can download it from here: <br><br>
    * **Windows**: https://www.python.org/downloads/<br><br>
    * **Ubuntu (VMs)**: Open the terminal and do the following:

        ```
        # sudo apt update
        ```
        Then, write this command:
        ```
        # sudo apt install python3
        ```
        <br>
    * For other devices check the following link: https://www.geeksforgeeks.org/download-and-install-python-3-latest-version/<br><br>

* You also need to have tkinter library installed, If you don`t then do the following: <br><br>
    * **Windows:** Open the command prompt then do the following:<br><br>
        ```
        pip install tk
        ```
        <br>
    * **Ubuntu (Vms)**: Open the terminal then do the following:<br><br>
        ```
        apt-get install python-tk
        or
        apt-get install python3-tk
        ``` 
        <br>
    * For other devices check the following link: https://tkdocs.com/tutorial/install.html<br><br>

---
<br>

## How to run :
---
<br>

* To open the client on your side and connect to our super server you only have to run the global version of the client (**clientG**) and nothing else.<br><br>

* To run the system locally you will have to make some small modifications:<br><br>

    1. In (**superServer.py**):<br><br>
        * Modify child servers ip addresses (lines 115 to 117) to the address of the local machine/s of your choice to host each child.<br><br>

        * Modify the ExternalIP (line 128) address to your global ip address (can be found from this link: http://www.myglobalip.com/)<br><br>

        * Last but not least, you will have to access your router configuration page and open the port (**5050**), and dont forget to make virtual servers for each machine you want to run a child server.<br><br>

    2. In (**server.py**): <br><br>
        * Modify the port number (line 11) to the port number of your choice (the one you chose during opening virtual server and port forwarding)<br><br>

        * Modify the Server adress (line 13) to be the server's machine ip address. <br><br>

        * Modify the SServer adress to be the internal address of the machine running the Super Server. <br><br>

    3. In (**client.py**):<br><br>
        * Change Server address (line 18) to be the same ip address of the machine running the Super Server.<br><br>

---
<br>

## Known Bugs :
---
<br>

* Typing in a fast rate may cause other clients to crash.<br><br>

* Holding backspace to delete causes.desynchronization (in some occasions, it may crash other clients).<br><br>

---
<br>

## Video Link (DEMO)
---
<br>
The video link can be found here:<br>

https://drive.google.com/drive/folders/1jHHzfldHmrPJz8BkbHSQlu66bh4fu1Z2?usp=sharing 
