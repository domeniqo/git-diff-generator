import os
import re
import shutil
from os import path
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import askyesnocancel, showerror, showinfo, showwarning
from tkinter.ttk import Combobox

import git
import git.exc

version="2.2"

class App:
    
    options=["Generate ref diff", "Generate merge diff"]
    
    def run(self):
        self.main_window = Tk()
        self.main_window.title(f"Git diff folders generator v{version}")
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
        label_action = Label(self.main_window)
        label_action.config(text="Choose action: ")
        label_action.grid(row=1, column=1, sticky="E")
        self.dropdown_menu = Combobox(values=self.options, state="readonly")
        self.dropdown_menu.config(width=50)
        self.dropdown_menu.grid(row=1, column=2)
        self.dropdown_menu.current(0)
        self.dropdown_menu.bind("<<ComboboxSelected>>", self.check_dropdown_change)
        
        # row 2
        label_git_repo = Label(self.main_window)
        label_git_repo.config(text="Git repo path: ")
        label_git_repo.grid(row=2, column=1, sticky="E")
        self.text_box_git_repo = Entry(self.main_window)
        self.text_box_git_repo.config(width=50)
        self.text_box_git_repo.grid(row=2, column=2)
        browse_repo_button = Button(self.main_window)
        browse_repo_button.config(text="Browse...")
        browse_repo_button.config(width=10)
        browse_repo_button.config(
            command=lambda: self.fill_folder_path(self.text_box_git_repo)
        )
        browse_repo_button.grid(row=2, column=3)

        # row 3
        label_output_dir = Label(self.main_window)
        label_output_dir.config(text="Output dir: ")
        label_output_dir.grid(row=3, column=1, sticky="E")
        self.text_box_output_dir = Entry(self.main_window)
        self.text_box_output_dir.config(width=50)
        self.text_box_output_dir.grid(row=3, column=2)
        browse_output_dir_button = Button(self.main_window)
        browse_output_dir_button.config(text="Browse...")
        browse_output_dir_button.config(width=10)
        browse_output_dir_button.config(
            command=lambda: self.fill_folder_path(self.text_box_output_dir)
        )
        browse_output_dir_button.grid(row=3, column=3)

        # row 4
        label_ref1 = Label(self.main_window)
        label_ref1.grid(row=4, column=1, sticky="E")
        label_ref1.config(
            text="Git ref1 - updated version (branch, tag, commit hash): "
        )
        self.text_box_ref1 = Entry(self.main_window)
        self.text_box_ref1.config(width=50)
        self.text_box_ref1.grid(row=4, column=2)

        # row 5
        label_ref2 = Label(self.main_window)
        label_ref2.grid(row=5, column=1, sticky="E")
        label_ref2.config(
            text="Git ref2 - original version (branch, tag, commit hash): "
        )
        self.text_box_ref2 = Entry(self.main_window)
        self.text_box_ref2.config(width=50)
        self.text_box_ref2.grid(row=5, column=2)

        # row 6
        label_regex = Label(self.main_window)
        label_regex.grid(row=6, column=1, sticky="E")
        label_regex.config(text="Regex to filter out files (match==include): ")
        self.text_box_regex = Entry(self.main_window)
        self.text_box_regex.config(width=50)
        self.text_box_regex.grid(row=6, column=2)
        self.var1 = BooleanVar()
        self.ignore_case = Checkbutton(
            self.main_window,
            text="Ignore case",
            variable=self.var1,
            onvalue=True,
            offvalue=False,
        )
        self.ignore_case.grid(row=6, column=3, sticky="W")

        # row 7
        generate_button = Button(self.main_window)
        generate_button.config(text="PROCEED WITH ACTION")
        generate_button.config(width=60)
        generate_button.config(command=self.process_command)
        generate_button.grid(row=7, column=1, columnspan=3)

    def fill_folder_path(self, entry_to_fill):
        dir_path = askdirectory(title="Select folder")
        if dir_path:
            entry_to_fill.delete(0, END)
            entry_to_fill.insert(0, dir_path)

    def check_dropdown_change(self, event):
        
        action = event.widget.get()

        if action == self.options[0]:
            self.text_box_ref1.config(state="normal")
            self.text_box_ref2.config(state="normal")
            self.text_box_regex.config(state="normal")
        elif action == self.options[1]:
            self.text_box_ref1.config(state="disabled")
            self.text_box_ref2.config(state="disabled")
            self.text_box_regex.config(state="disabled")
            
    def process_command(self):
        action = self.dropdown_menu.get()
        if action == self.options[0]:
            self.generate_refs_diff()
        elif action == self.options[1]:
            self.generate_merge_diff()
            
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
        generate_empty_file = askyesnocancel("Empty file generation", "Would you like to generate empty " +
                                             "files when file is not present at given revision?\n" +
                                             "This will create matching folder structure for all output folders.")
        if generate_empty_file == None:
            return
        list_of_files = []
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
            original_branch = None
            original_commit = None
            conflicting_files = None
            # remember where the repo was before
            try:
                original_branch = repo.active_branch
                original_commit = repo.active_branch.commit
            except TypeError:
                original_commit = repo.head.commit
            if len(original_commit.parents) != 2:
                # not a 3 way merge, not supported
                showinfo(title="INFO", message="Git repository is not switched to reference with merge commit.")
                return
            # select dest/source commits that resulted in merge commit
            dest_commit = original_commit.parents[0]
            source_commit = original_commit.parents[1]
            repo.git.checkout(dest_commit)
            try:
                repo.git.merge(source_commit)
                showinfo(title="INFO", message=f"No merge conflict or any problem detected while merging references \n"+
                         f"SOURCE:{source_commit}\n"+
                         f"TARGET:{dest_commit}")
                # checkout back to original state
                if original_branch != None:
                    repo.git.checkout(original_branch, "--force")
                else:
                    repo.git.checkout(original_commit, "--force")
                return
            except git.exc.GitCommandError:
                conflicting_files=repo.index.unmerged_blobs()
                
            if conflicting_files != None and len(conflicting_files) > 0:
                os.makedirs(output_root_dir, exist_ok=True)
            else:
                showinfo(title="INFO", message="No merge conflicts found in given repository.")
                return
            for file_path in conflicting_files:
                # create dictionary where key is number 1-3 where 
                # 1 == base (common ancestor), 2 == head (current revision), 3 == merge_head (revision for merge)
                ref_blob_dict = {pair[0]:pair[1] for pair in conflicting_files[file_path]}
                for key in range(1,4):
                    if key == 1:
                        location = "base"
                    elif key == 2:
                        location = "destination"
                    elif key == 3:
                        location = "source"
                    
                    final_path = os.path.join(output_root_dir, location, os.path.normpath(file_path))
                    list_of_files.append(os.path.join(location, os.path.normpath(file_path)))
                    os.makedirs(path.dirname(final_path), exist_ok=True)
                    try:
                        blob = ref_blob_dict[key]
                        blob.stream_data(open(final_path, "wb"))
                    except:
                        #log the error if needed (file/blob is not present in revision with current key)
                        if generate_empty_file:
                            open(final_path, "wb")
            # checkout back to original state
            if original_branch != None:
                repo.git.checkout(original_branch, "--force")
            else:
                repo.git.checkout(original_commit, "--force")
            # locate files in final commit and make a copy to output folder
            for file_path in conflicting_files:
                location = "final-resolution"
                resolved_file_path = os.path.abspath(os.path.join(repo_path, file_path))
                final_path = os.path.join(output_root_dir, location, os.path.normpath(file_path))
                list_of_files.append(os.path.join(location, os.path.normpath(file_path)))
                os.makedirs(path.dirname(final_path), exist_ok=True)
                if os.path.exists(resolved_file_path):
                    shutil.copy(resolved_file_path, final_path)
                else:
                    if generate_empty_file:
                        open(final_path, "wb")
            # generate complete list of generated files in output folder
            with open(os.path.join(output_root_dir, "README.txt"), "wb") as file:
                list_of_files.sort()
                list_of_files = [bytes(path + os.linesep, "utf-8") for path in list_of_files]
                file.writelines(list_of_files)
            showinfo(
                title="SUCCESS",
                message=f"Task finished successfully.",
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

if __name__ == "__main__":
    app = App()
    app.run()
