import os
import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from util import recognize


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        # Add buttons
        self.login_button_main_window = self.get_button(self.main_window, 'Login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)

        self.logout_button_main_window = self.get_button(self.main_window, 'Logout', 'red', self.logout)
        self.logout_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = self.get_button(self.main_window, 'Register New User', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        # Webcam
        self.webcam_label = self.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        # Directories
        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)
        self.log_path = './log.txt'

    def add_webcam(self, label):
        self.cap = cv2.VideoCapture(0)  # Initialize webcam
        if not self.cap.isOpened():
            raise Exception("Webcam not accessible.")
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        if ret:
            self.most_recent_capture_arr = frame
            img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
            self.most_recent_capture_pil = Image.fromarray(img_)
            imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
            self._label.imgtk = imgtk
            self._label.configure(image=imgtk)
        self._label.after(20, self.process_webcam)

    def login(self):
        name = recognize(self.most_recent_capture_arr, self.db_dir)
        if name == 'unknown_person':
            messagebox.showinfo("Error", "Unknown user. Please register or try again.")
        elif name == 'no_persons_found':
            messagebox.showinfo("Error", "No face detected. Please try again.")
        else:
            messagebox.showinfo("Welcome!", f"Hello, {name}!")
            with open(self.log_path, 'a') as f:
                f.write(f'{name},{datetime.datetime.now()},in\n')

    def logout(self):
        name = recognize(self.most_recent_capture_arr, self.db_dir)
        if name == 'unknown_person':
            messagebox.showinfo("Error", "Unknown user. Please register or try again.")
        else:
            messagebox.showinfo("Goodbye!", f"See you soon, {name}!")
            with open(self.log_path, 'a') as f:
                f.write(f'{name},{datetime.datetime.now()},out\n')

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.capture_label = self.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = tk.Text(self.register_new_user_window, height=2, width=15, font=("Arial", 32))
        self.entry_text_register_new_user.place(x=750, y=150)

        self.text_label_register_new_user = tk.Label(self.register_new_user_window, text="Enter Username:", font=("sans-serif", 21))
        self.text_label_register_new_user.place(x=750, y=70)

        self.accept_button_register_new_user_window = self.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = self.get_button(self.register_new_user_window, 'Try Again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)
        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def accept_register_new_user(self):
        name = self.entry_text_register_new_user.get(1.0, "end-1c").strip()
        if not name:
            messagebox.showinfo("Error", "Please enter a valid username.")
            return

        try:
            # Save the current frame (captured face) to the database
            user_image_path = os.path.join(self.db_dir, f"{name}.jpg")
            cv2.imwrite(user_image_path, self.register_new_user_capture)

            messagebox.showinfo("Success", f"User '{name}' registered successfully!")
        except Exception as e:
            messagebox.showinfo("Error", f"An error occurred: {e}")
        finally:
            self.register_new_user_window.destroy()

    def get_button(self, window, text, color, command, fg='white'):
        return tk.Button(window, text=text, activebackground="black", activeforeground="white", fg=fg, bg=color, command=command, height=2, width=20, font=('Helvetica bold', 20))

    def get_img_label(self, window):
        label = tk.Label(window)
        label.grid(row=0, column=0)
        return label

    def start(self):
        self.main_window.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
