import tkinter as tk
import subprocess
import customtkinter
import os
import signal

# Function to start the script
def start_script():
    global process
    
    script_path = "C:\\VIT FOLDER\\Network Security\\Datasets\\Grindwall\\grindwall.py"  
    
    if not process or process.poll() is not None:
        process = subprocess.Popen(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Grindwall started on port 1234.")
    else:
        print("Grindwall is already running.")

# Function to stop the script
def stop_script():
    global process
    if process and process.poll() is None:
        # Terminate the script
        os.kill(process.pid, signal.SIGTERM)
        process.communicate()
        print("Grindwall stopped.")
    else:
        print("Grindwall  is not running.")

# Create the main window
customtkinter.set_default_color_theme('green')
root = customtkinter.CTk()
root.title("Grindwall GUI")

root.geometry("300x400")
# Create a button to start the script
# start_button = tk.Button(root, text="Start Script", command=start_script)
start_button = customtkinter.CTkButton(master=root,text="Start GrindWall",command=start_script)
start_button.place(relx =0.5, rely=0.4, anchor='center')

# Create a button to stop the script
stop_button = customtkinter.CTkButton(master=root,text="Stop GrindWall",command=stop_script)
stop_button.place(relx =0.5, rely=0.6, anchor='center')

# Initialize the process variable
process = None

root.mainloop()
