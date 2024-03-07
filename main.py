import git
from os import path
import os
from tkinter import *
from tkinter.messagebox import showerror, showinfo, showwarning
from tkinter.filedialog import askdirectory
import re


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
        label_regex = Label(self.main_window)
        label_regex.grid(row=5, column=1, sticky="E")
        label_regex.config(text="Regex to filter out files (match==include): ")
        self.text_box_regex = Entry(self.main_window)
        self.text_box_regex.config(width=50)
        self.text_box_regex.grid(row=5, column=2)
        self.var1 = BooleanVar()
        self.ignore_case = Checkbutton(
            self.main_window,
            text="Ignore case",
            variable=self.var1,
            onvalue=True,
            offvalue=False,
        )
        self.ignore_case.grid(row=5, column=3, sticky="W")

        # row 6
        generate_button = Button(self.main_window)
        generate_button.config(text="GENERATE REFS DIFF")
        generate_button.config(width=60)
        generate_button.config(command=self.generate_refs_diff)
        generate_button.grid(row=6, column=1, columnspan=3)
        
        # row 7
        generate_button2 = Button(self.main_window)
        generate_button2.config(text="GENERATE MERGE DIFF")
        generate_button2.config(width=60)
        generate_button2.config(command=self.generate_merge_diff)
        generate_button2.grid(row=7, column=1, columnspan=3)

    def fill_folder_path(self, entry_to_fill):
        dir_path = askdirectory(title="Select folder")
        if dir_path:
            entry_to_fill.delete(0, END)
            entry_to_fill.insert(0, dir_path)

    def generate_refs_diff(self):
        try:
            repo_path = self.text_box_git_repo.get()
            output_root_dir = self.text_box_output_dir.get()
            ref1 = self.text_box_ref1.get()
            ref2 = self.text_box_ref2.get()
            regex = self.text_box_regex.get()
            if regex != "":
                try:
                    re.compile(regex)
                except re.error:
                    showwarning(
                        title="WARNING",
                        message="Not a valid regex. Searching for all files",
                    )
                    regex = ".*"
            else:
                regex = ".*"

            updated_files = path.join(
                output_root_dir,
                "updated-" + ref1.replace(os.sep, "_").replace("/", "_"),
            )
            original_files = path.join(
                output_root_dir,
                "original-" + ref2.replace(os.sep, "_").replace("/", "_"),
            )

            try:
                repo = git.Repo(repo_path)
            except git.InvalidGitRepositoryError:
                showerror(
                    title="Invalid repo",
                    message="Provided git repo path is not a valid git repository.",
                )
                raise
            try:
                full_diff = repo.commit(ref2).diff(ref1)
            except git.BadName:
                showerror(
                    title="Invalid reference",
                    message="Provided references do not exist in git repo.",
                )
                raise
            added_files = list(full_diff.iter_change_type("A"))
            modified_files = list(full_diff.iter_change_type("M"))
            renamed_files = list(full_diff.iter_change_type("R"))
            deleted_files = list(full_diff.iter_change_type("D"))

            full_list = added_files + modified_files + renamed_files + deleted_files
            expected_count = (
                len(added_files)
                + len(deleted_files)
                + 2 * len(renamed_files)
                + 2 * len(modified_files)
            )
            counter = 0
            for diff_object in full_list:
                if diff_object.a_blob and re.match(
                    pattern=regex,
                    string=diff_object.a_path,
                    flags=re.IGNORECASE if self.var1.get() else 0,
                ):
                    final_path = path.abspath(
                        path.join(original_files, diff_object.a_path)
                    )
                    os.makedirs(path.dirname(final_path), exist_ok=True)
                    diff_object.a_blob.stream_data(open(final_path, "wb"))
                    counter += 1
                if diff_object.b_blob and re.match(
                    pattern=regex,
                    string=diff_object.b_path,
                    flags=re.IGNORECASE if self.var1.get() else 0,
                ):
                    final_path = path.abspath(
                        path.join(updated_files, diff_object.b_path)
                    )
                    os.makedirs(path.dirname(final_path), exist_ok=True)
                    diff_object.b_blob.stream_data(open(final_path, "wb"))
                    counter += 1
            showinfo(
                title="SUCCESS",
                message=f"Task finished successfully.\n{counter}/{expected_count}",
            )
        except Exception as e:
            if not any(
                [
                    isinstance(e, handled_exception)
                    for handled_exception in [
                        git.InvalidGitRepositoryError,
                        git.BadName,
                    ]
                ]
            ):
                showerror(
                    title="ERROR",
                    message="Task failed successfully for unhandled reason.",
                )

    def generate_merge_diff(self):
        try:
            repo_path = self.text_box_git_repo.get()
            output_root_dir = self.text_box_output_dir.get()
            try:
                repo = git.Repo(repo_path)
            except git.InvalidGitRepositoryError:
                showerror(
                    title="Invalid repo",
                    message="Provided git repo path is not a valid git repository.",
                )
                raise
            
            conflicted_files = repo.index.unmerged_blobs()
            if len(conflicted_files) > 0:
                os.makedirs(output_root_dir, exist_ok=True)
            for file_path in conflicted_files:
                try:
                    # Get the base file version (closest common parent for this file)
                    base_blob = conflicted_files[file_path][0][1]
                    final_path = os.path.join(output_root_dir, 'base', os.path.normpath(file_path))
                    os.makedirs(path.dirname(final_path), exist_ok=True)
                    base_blob.stream_data(open(final_path, "wb"))
                except Exception as e:
                    #print(f"can't locate file {file_path} in base versions")
                    #log the error
                    pass
                
                try:
                    # Get the file version from HEAD (your current repository state)
                    head_blob = conflicted_files[file_path][1][1]
                    final_path = os.path.join(output_root_dir, 'head', os.path.normpath(file_path))
                    os.makedirs(path.dirname(final_path), exist_ok=True)
                    head_blob.stream_data(open(final_path, "wb"))
                except:
                    #print(f"can't locate file {file_path} in head versions")
                    #log the error
                    pass
                
                try:
                    # Get the file version from MERGE_HEAD (what you are merging)
                    merge_head_blob = conflicted_files[file_path][2][1]
                    final_path = os.path.join(output_root_dir, 'merge_head', os.path.normpath(file_path))
                    os.makedirs(path.dirname(final_path), exist_ok=True)
                    merge_head_blob.stream_data(open(final_path, "wb"))
                except:
                    #print(f"can't locate file {file_path} in merge_head versions")
                    #log the error
                    pass

        except Exception as e:
            if not any(
                [
                    isinstance(e, handled_exception)
                    for handled_exception in [
                        git.InvalidGitRepositoryError,
                        git.BadName,
                    ]
                ]
            ):
                showerror(
                    title="ERROR",
                    message="Task failed successfully for unhandled reason.",
                )

if __name__ == "__main__":
    app = App()
    app.run()
