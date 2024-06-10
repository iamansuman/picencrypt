from os import path, environ
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from re import match as regexMatch
# from concurrent.futures import ThreadPoolExecutor
from core import Encrypt, Decrypt

#GUI Setup
ctk.set_appearance_mode('system')

root = ctk.CTk()
root.geometry("300x400")
root.resizable(width=False, height=False)
root.title("PicEncrypt")
root.iconbitmap("./picencrypt.ico")

tabView = ctk.CTkTabview(root, width=270, height=380)
tabView.pack()
tabView.add("Encrypt")
tabView.add("Decrypt")
tabView.set("Encrypt")

#custom vars, commands and functions
enFileName, enFilePath, enSaveFilePath, deFileName, deFilePath, deSaveFilePath = str(), str(), str(path.join(environ['USERPROFILE'], 'Desktop')), str(), str(), str(path.join(environ['USERPROFILE'], 'Desktop'))
epk, esk, dpk, dsk = ctk.StringVar(), ctk.StringVar(), ctk.StringVar(), ctk.StringVar()
end_file_type = ctk.StringVar(value='zip')

def validateRegex(string): return bool(regexMatch(r"^[a-zA-Z0-9!@#$%^&*-=_+]+$", string))

def obtainEFilePath():
    global enFileName, enFilePath
    enFilePath = str(ctk.filedialog.askopenfilename())
    enFileName = enFilePath.split('/')[::-1][0]
    encCurrFile.configure(text=enFileName if enFilePath != "" else "__NO_FILE_SELECTED__")

def obtainDFilePath():
    global deFileName, deFilePath
    deFilePath = str(ctk.filedialog.askopenfilename())
    deFileName = deFilePath.split('/')[::-1][0]
    decCurrFile.configure(text=deFileName if deFilePath != "" else "__NO_FILE_SELECTED__")

def obtainEncSaveDir():
    global enSaveFilePath
    enSaveFilePath = str(ctk.filedialog.askdirectory())
    if (enSaveFilePath == ''): enSaveFilePath = str(path.join(environ['USERPROFILE'], 'Desktop'))
    encDestDir.configure(text = enSaveFilePath)


def obtainDecSaveDir():
    global deSaveFilePath
    deSaveFilePath = str(ctk.filedialog.askdirectory())
    if (deSaveFilePath == ''): deSaveFilePath = str(path.join(environ['USERPROFILE'], 'Desktop'))
    decDestDir.configure(text = deSaveFilePath)

def encrypt():
    keys = [str(encPrimaryKey.get()).strip(), str(encSecondaryKey.get()).strip()]
    
    if enFilePath == "":
        CTkMessagebox(title="Error", icon='cancel', message="No File is selected")
        return
    if len(keys[0]) < 8 or len(keys[1]) < 8:
        CTkMessagebox(title="Error", icon='cancel', message="Length of keys/ passwords must be 8 or greater")
        return
    if not validateRegex(keys[0]) or not validateRegex(keys[1]):
        CTkMessagebox(title="Error", icon='cancel', message="Only A-Z a-z 0-9 and !@#$%^&*_+-= are allowed in keys")
        return
    
    payload = [enFileName, enFilePath, enSaveFilePath, end_file_type, keys]
    
    # ThreadPoolExecutor.submit(Encrypt)

    EncStatus = Encrypt(payload)

    if EncStatus == "OK":
        msgbox = CTkMessagebox(title="Info", icon="check", message="Success", option_2="Save keys in Desktop", sound=True, option_focus=1)
        if msgbox.get() == "Save keys in Desktop":
            for i in range(1, 3):
                with open(path.join(environ['USERPROFILE'], 'Desktop', f'{i}.txt'), 'w') as f: f.writelines(keys[i-1])
    else: CTkMessagebox(title="Error", icon='cancel', message="Unexpected Error")

def decrypt():
    global dpk, dsk
    keys = [dpk.get(), dsk.get()]

    if deFilePath == "":
        CTkMessagebox(title="Error", icon='cancel', message="No File is selected")
        return
    if len(keys[0]) < 8 or len(keys[1]) < 8:
        CTkMessagebox(title="Error", icon='cancel', message="Length of keys must be 8 or greater")
        return
    if not validateRegex(keys[0]) or not validateRegex(keys[1]):
        CTkMessagebox(title="Error", icon='cancel', message="Only A-Z a-z 0-9 and !@#$%^&*_+-= are allowed in keys")
        return

    payload = [deFileName, deFilePath, deSaveFilePath, keys]

    DecStatus = Decrypt(payload)

    if DecStatus == "OK": CTkMessagebox(title="Info", icon="check", message="Decryption Success", sound=True)
    elif DecStatus == "Wrong Password": CTkMessagebox(title="Error", icon='cancel', message="Key(s) is/are invalid")
    else: CTkMessagebox(title="Error", icon='cancel', message="Unexpected Error")

#Encryption
ENframe = tabView.tab("Encrypt")

enSourceFileButton = ctk.CTkButton(ENframe, text="Pick a File to Encrypt", command=obtainEFilePath)
enSourceFileButton.pack(padx=10, pady=6)

encCurrFile = ctk.CTkLabel(ENframe, text="__NO_FILE_SELECTED__", wraplength=200)
encCurrFile.pack(padx=10, pady=6)

encPrimaryKey = ctk.CTkEntry(ENframe, placeholder_text="Primary Key", show='*')
encPrimaryKey.pack(padx=10, pady=6)

encSecondaryKey = ctk.CTkEntry(ENframe, placeholder_text="Secondary Key", show='*')
encSecondaryKey.pack(padx=10, pady=6)

# endFileTypeOptionMenu = ctk.CTkOptionMenu(ENframe, values=['zip', 'mp4'], variable=end_file_type)
endFileTypeOptionMenu = ctk.CTkOptionMenu(ENframe, values=['zip'], variable=end_file_type)
endFileTypeOptionMenu.pack(padx=10, pady=6)

enDestDirButton = ctk.CTkButton(ENframe, text="Choose where to save", command=obtainEncSaveDir)
enDestDirButton.pack(padx=10, pady=6)

encDestDir = ctk.CTkLabel(ENframe, text=enSaveFilePath, wraplength=200)
encDestDir.pack(padx=10, pady=6)

encButton = ctk.CTkButton(ENframe, text="Encrypt", command=encrypt)
encButton.pack(padx=10, pady=6)


#Decryption
DEframe = tabView.tab("Decrypt")

deSourceFileButton = ctk.CTkButton(DEframe, text="Pick a File to Decrypt", command=obtainDFilePath)
deSourceFileButton.pack(padx=10, pady=6)

decCurrFile = ctk.CTkLabel(DEframe, text="__NO_FILE_SELECTED__", wraplength=200)
decCurrFile.pack(padx=10, pady=6)

decPrimaryKey = ctk.CTkEntry(DEframe, placeholder_text="Primary Key", textvariable=dpk)
decPrimaryKey.pack(padx=10, pady=6)

decSecondaryKey = ctk.CTkEntry(DEframe, placeholder_text="Secondary Key", textvariable=dsk)
decSecondaryKey.pack(padx=10, pady=6)

deDestDirButton = ctk.CTkButton(DEframe, text="Choose where to save", command=obtainDecSaveDir)
deDestDirButton.pack(padx=10, pady=6)

decDestDir = ctk.CTkLabel(DEframe, text=deSaveFilePath, wraplength=200)
decDestDir.pack(padx=10, pady=6)

decButton = ctk.CTkButton(DEframe, text="Decrypt", command=decrypt)
decButton.pack(padx=10, pady=6)



#Run App
root.mainloop()