import os
import base64

import customtkinter
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk



#//////////////////////////////////////////////////////


# تعيين نمط واجهة customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


#//////////////////////////////////////////////////////


# توليد مفتاح عشوائي بناءً على نوع التشفير
def generate_key(algorithm):
    if algorithm == 'AES':
        return os.urandom(32)  # 32 بايت لتوليد مفتاح AES-256
    elif algorithm == 'DES':
        return os.urandom(8)  # 8 بايت لتوليد مفتاح DES
    elif algorithm == 'Blowfish':
        return os.urandom(16)  # 16 بايت لتوليد مفتاح Blowfish
    elif algorithm == '3DES':
        return os.urandom(24)  # 24 بايت لتوليد مفتاح 3DES
    else:
        raise ValueError("Unsupported algorithm")


# إنشاء دالة لتوليد مفتاح باستخدام كلمة مرور
def generate_key_from_password(password):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(password.encode())
    return digest.finalize()


# تشفير الملف باستخدام كلمة مرور
def encrypt_file(file_path, key, algorithm, password=None):
    if password:
        key = generate_key_from_password(password)

    with open(file_path, 'rb') as f:
        file_data = f.read()

    # توليد IV عشوائي
    iv = os.urandom(16)
    if algorithm == 'AES':
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    elif algorithm == 'DES':
        cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv))
    elif algorithm == 'Blowfish':
        cipher = Cipher(algorithms.Blowfish(key), modes.CBC(iv))
    elif algorithm == '3DES':
        cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv))
    else:
        raise ValueError("Unsupported algorithm")

    encryptor = cipher.encryptor()

    # إضافة padding
    padding_length = 16 - (len(file_data) % 16)
    padded_data = file_data + bytes([padding_length]) * padding_length

    # تشفير البيانات
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # حفظ البيانات المشفرة مع IV
    encrypted_file_path = file_path + ".enc"
    with open(encrypted_file_path, 'wb') as f:
        f.write(iv + encrypted_data)

    # حذف الملف الأصلي بعد التشفير
    os.remove(file_path)

    return encrypted_file_path


# فك تشفير الملف باستخدام كلمة مرور
def decrypt_file(file_path, key, algorithm, password=None):
    if password:
        key = generate_key_from_password(password)

    with open(file_path, 'rb') as f:
        file_data = f.read()

    # استخراج IV من البيانات المشفرة
    iv = file_data[:16]
    encrypted_data = file_data[16:]
# انواع التشفير المستخدمة
    if algorithm == 'AES':
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    elif algorithm == 'DES':
        cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv))
    elif algorithm == 'Blowfish':
        cipher = Cipher(algorithms.Blowfish(key), modes.CBC(iv))
    elif algorithm == '3DES':
        cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv))
    else:
        raise ValueError("Unsupported algorithm")

    decryptor = cipher.decryptor()

    # فك تشفير البيانات
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # إزالة padding
    padding_length = decrypted_data[-1]
    decrypted_data = decrypted_data[:-padding_length]

    # حفظ الملف المفكوك
    decrypted_file_path = file_path.replace(".enc", "") # حفظ الملف بعد فك التشفير
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)

    # حذف الملف المشفر بعد فك التشفير
    os.remove(file_path)

    return decrypted_file_path


# حفظ المفتاح في ملف
def save_key(key, file_path):
    key_base64 = base64.b64encode(key).decode('utf-8')
    with open(file_path, 'w') as f:
        f.write(key_base64)


# تحميل المفتاح من ملف
def load_key(file_path):
    with open(file_path, 'r') as f:
        key_base64 = f.read()
    return base64.b64decode(key_base64)


# واجهة المستخدم باستخدام Tkinter
def choose_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        return file_path
    return None


def choose_save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted Files", "*.enc")]) # امتداد التشفير
    if file_path:
        return file_path
    return None


def choose_save_key():
    key_path = filedialog.asksaveasfilename(defaultextension=".key", filetypes=[("Key Files", "*.key")]) # حفظ المفتاح
    if key_path:
        return key_path
    return None


def encrypt_button_clicked():
    file_path = choose_file()
    if file_path:
        algorithm = algorithm_var.get()
        key = generate_key(algorithm)
        password = password_entry.get()  # استخدام كلمة المرور من واجهة المستخدم
        encrypted_file = encrypt_file(file_path, key, algorithm, password)

        # حفظ المفتاح
        key_file_path = choose_save_key()
        if key_file_path:
            save_key(key, key_file_path)

        messagebox.showinfo("Success",
                            f"File encrypted successfully!\n\nEncrypted file: {encrypted_file}\n\n [Original file deleted].",detail='Developer : Mohammed Alaa Mohammed')


def decrypt_button_clicked():
    file_path = choose_file()
    if file_path:
        key_file_path = filedialog.askopenfilename(filetypes=[("Key Files", "*.key")])
        if key_file_path:
            key = load_key(key_file_path)
            algorithm = algorithm_var.get()
            password = password_entry.get()  # استخدام كلمة المرور من واجهة المستخدم
            decrypted_file = decrypt_file(file_path, key, algorithm, password)
            messagebox.showinfo("Success",
                                f"File decrypted successfully!\nDecrypted file: {decrypted_file}\nEncrypted file deleted.")


#//////////////////////////////////////////////////

show_password = 0
def SHOW_PASSWORD ():
    global show_password

    if show_password == 0:
        password_entry.configure(show = '')
        show_password = 1
    else:
        show_password = 0
        password_entry.configure(show="●")

#//////////////////////////////////////////////////

# إعداد واجهة Tkinter
root = ctk.CTk()
root.title("File Encryption and Decryption / M.A.M")
root.iconbitmap(r"C:\Python\Cyber Security\scr.ico")
# root.config(bg="#00000f")  # تغيير الخلفية إلى الأزرق الفاتح
# تنسيق الواجهة
root.geometry("500x400+650+220")  # تعيين حجم الواجهة
root.resizable(False,False)
root.focus()
root.update()
root.overrideredirect(None)
root.focus_set()


# إعداد العناوين
label = tk.Label(root, text="Encrypt or Decrypt Files", font=("Arial", 16), bg="#222324",fg="#FFF")
label.pack(pady=20)

# إعداد قائمة لاختيار نوع التشفير
algorithm_var = tk.StringVar(value='AES')
algorithm_label = tk.Label(root, text="Select Encryption Algorithm", font=("Arial", 14), bg="#222324",fg="#FFF")
algorithm_label.pack(pady=10)

algorithm_menu = tk.OptionMenu(root, algorithm_var, 'AES', 'DES', 'Blowfish', '3DES')
algorithm_menu.configure(bg='#222324',fg='#FFF')
algorithm_menu.config(width=15, font=("Arial", 12))
algorithm_menu.pack(pady=10)

# إعداد إدخال كلمة المرور
password_label = tk.Label(root, text="Enter Password (Optional)", font=("Arial", 12), bg="#222324",fg='#FFF')
password_label.pack(pady=10)

password_entry =customtkinter.CTkEntry(root, font=("Arial", 14), show="●",corner_radius=3,width=200,height=35,placeholder_text="Set Password")
password_entry.pack(pady=10)

# عرض كلمة المرور
set_show_password = customtkinter.CTkButton(root,text='👁',command=SHOW_PASSWORD,width=40,height=30, font=("Arial", 20))
set_show_password.place(y=182,x=360)


# إعداد الأزرار
encrypt_button = customtkinter.CTkButton(root, text="Encrypt File", command=encrypt_button_clicked, width=180, height=45,  font=("Arial", 15,'bold')
,corner_radius=5,border_width=2,border_color='#a29bfe',text_color='#fffccc',fg_color='#222324',hover_color='#000')
encrypt_button.pack(pady=10)

decrypt_button = customtkinter.CTkButton(root, text="Decrypt File", command=decrypt_button_clicked, width=180, height=45,font=("Arial", 15,'bold')
,corner_radius=5,border_width=2,border_color='#54a0ff',text_color='#FFF',fg_color='#576574',hover_color='#000')
decrypt_button.pack(pady=10)


by_me = customtkinter.CTkLabel(root,text='Developer : Mohammed Alaa Mohammed V.2 Last Update  ',font=("",12,'bold')).place(x=2,y=374)
# بدء واجهة Tkinter
root.mainloop()
