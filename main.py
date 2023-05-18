import git
from os import path
import os
from tkinter import *
from tkinter.messagebox import showerror, showinfo, showwarning


class App:
    def run(self):
        self.main_window = Tk()
        self.main_window.title(f"Git diff folders generator")
        self.main_window.protocol("WM_DELETE_WINDOW", self._quit)

        self.init_gui()

        self.main_window.mainloop()

    def _quit(self):
        """
        Due to unexpected behaviour when main_window got stuck in mainloop,
        this functions helps destroy the window after closing it.
        """
        self.main_window.quit()
        self.main_window.destroy()

    def init_gui(self):
        self.label_git_repo = Label(self.main_window)
        self.label_git_repo.config(text="git repo path")
        self.label_git_repo.pack()
        self.text_box_git_repo = Entry(self.main_window)
        self.text_box_git_repo.pack()

        self.label_output_dir = Label(self.main_window)
        self.label_output_dir.config(text="output dir")
        self.label_output_dir.pack()
        self.text_box_output_dir = Entry(self.main_window)
        self.text_box_output_dir.pack()

        self.label_ref1 = Label(self.main_window)
        self.label_ref1.config(text="git ref1 - updated version")
        self.label_ref1.pack()
        self.text_box_ref1 = Entry(self.main_window)
        self.text_box_ref1.pack()

        self.label_ref2 = Label(self.main_window)
        self.label_ref2.config(text="git ref2 - original version")
        self.label_ref2.pack()
        self.text_box_ref2 = Entry(self.main_window)
        self.text_box_ref2.pack()

        button = Button(self.main_window)
        button.config(text="GENERATE DIFF")
        button.config(width=60)
        button.config(command=self.proceed_command)
        button.pack()

    def proceed_command(self):
        try:
            repo_path = self.text_box_git_repo.get()
            output_root_dir = self.text_box_output_dir.get()
            ref1 = self.text_box_ref1.get()
            ref2 = self.text_box_ref2.get()

            updated_files = path.join(output_root_dir, "updated-" + ref1)
            original_files = path.join(output_root_dir, "original-" + ref2)

            repo = git.Repo(repo_path)
            full_diff = repo.commit(ref2).diff(ref1)
            added_files = list(full_diff.iter_change_type("A"))
            modified_files = list(full_diff.iter_change_type("M"))
            renamed_files = list(full_diff.iter_change_type("R"))
            deleted_files = list(full_diff.iter_change_type("D"))

            for diff_object in (
                added_files + modified_files + renamed_files + deleted_files
            ):
                if diff_object.a_blob:
                    final_path = path.abspath(
                        path.join(original_files, diff_object.a_path)
                    )
                    os.makedirs(path.dirname(final_path), exist_ok=True)
                    diff_object.a_blob.stream_data(open(final_path, "wb"))
                if diff_object.b_blob:
                    final_path = path.abspath(
                        path.join(updated_files, diff_object.a_path)
                    )
                    os.makedirs(path.dirname(final_path), exist_ok=True)
                    diff_object.b_blob.stream_data(open(final_path, "wb"))
            showinfo(title="SUCCESS", message="Task finished successfully")
        except:
            showerror(title="ERROR", message="Task failed successfully")


if __name__ == "__main__":
    app = App()
    app.run()
