import git
from os import path
import os
from tkinter import *
from tkinter.messagebox import showerror, showinfo, showwarning
from tkinter.filedialog import askdirectory


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
        # row 1
        label_git_repo = Label(self.main_window)
        label_git_repo.config(text="Git repo path: ")
        label_git_repo.grid(row=1, column=1, sticky="E")
        self.text_box_git_repo = Entry(self.main_window)
        self.text_box_git_repo.config(width=50)
        self.text_box_git_repo.grid(row=1, column=2)
        browse_repo_button = Button(self.main_window)
        browse_repo_button.config(text="Browse...")
        browse_repo_button.config(width=10)
        browse_repo_button.config(
            command=lambda: self.fill_folder_path(self.text_box_git_repo)
        )
        browse_repo_button.grid(row=1, column=3)

        # row 2
        label_output_dir = Label(self.main_window)
        label_output_dir.config(text="Output dir: ")
        label_output_dir.grid(row=2, column=1, sticky="E")
        self.text_box_output_dir = Entry(self.main_window)
        self.text_box_output_dir.config(width=50)
        self.text_box_output_dir.grid(row=2, column=2)
        browse_output_dir_button = Button(self.main_window)
        browse_output_dir_button.config(text="Browse...")
        browse_output_dir_button.config(width=10)
        browse_output_dir_button.config(
            command=lambda: self.fill_folder_path(self.text_box_output_dir)
        )
        browse_output_dir_button.grid(row=2, column=3)

        # row 3
        label_ref1 = Label(self.main_window)
        label_ref1.grid(row=3, column=1, sticky="E")
        label_ref1.config(
            text="Git ref1 - updated version (branch, tag, commit hash): "
        )
        self.text_box_ref1 = Entry(self.main_window)
        self.text_box_ref1.config(width=50)
        self.text_box_ref1.grid(row=3, column=2)

        # row 4
        label_ref2 = Label(self.main_window)
        label_ref2.grid(row=4, column=1, sticky="E")
        label_ref2.config(
            text="Git ref2 - original version (branch, tag, commit hash): "
        )
        self.text_box_ref2 = Entry(self.main_window)
        self.text_box_ref2.config(width=50)
        self.text_box_ref2.grid(row=4, column=2)

        # row 5
        generate_button = Button(self.main_window)
        generate_button.config(text="GENERATE DIFF")
        generate_button.config(width=60)
        generate_button.config(command=self.proceed_command)
        generate_button.grid(row=5, column=1, columnspan=3)

    def fill_folder_path(self, entry_to_fill):
        dir_path = askdirectory(title="Select folder")
        if dir_path:
            entry_to_fill.delete(0, END)
            entry_to_fill.insert(0, dir_path)

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
