# Commit Message Contents
The first line should begin with `[RUNTIME]`, followed by a space and a one line description of your commit.

This should be followed by a new line.

Then your verbose commit message begins. Feel free to use paragraph-style prose. Bullet points are also okay, if they are sufficiently detailed.

Your commit message should:
1. Describe the feature you have implemented
2. Describe how to use the feature, if applicable

People should be able to understand what this commit does *without* needing to read your code.

# Commit Message Formatting
After typing up your commit message, ensure that it is properly formatted. This makes it easier to read when someone uses `git log`

I assume git is configured to use vim.
If not, see [here](http://stackoverflow.com/questions/2596805/how-do-i-make-git-use-the-editor-of-my-choice-for-commits)

In vim command mode:

1. Set text width to 70 `:set tw=70`
2. Execute the magic case-sensitive formatting command `gggqG`
  * `gg` Skip to the first line of the file
  * `gq` Format command. The next character you type tells it how many lines to format
  * `G` Skip to the last line of the file. Following `gq`, this means format from current cursor to end of file.
3. Make sure your first line is still only a single line. If formatting has split it up, that means it's too long.
4. Edit commit message, repeat formatting as necessary.

# Viewing Runtime commits only
`git log --grep=RUNTIME`

# Rebasing
Sometimes you make a bunch of commits as you're working to simulate saving your code. There is nothing inherently wrong with committing often. However, before you submit a pull request, I ask that you combine all your commits for a particular feature into a single commit, with a single commit message. This makes the code reviewer's job much easier. They should not be writing a commit message for *your* pull request.

To combine multiple commits into a single commit, we use the rebase command.

Suppose we want to combine the last `n` commits into one.

`git rebase -i HEAD~n`

You will be put into a vim session. A file will automatically be open with a list of the commits in this rebase. The oldest commits are at the top of the file; newest commits are at the bottom.

Replace `pick` with `squash` (or `s`) for all commits **EXCEPT THE FIRST ONE**. This will combine all the later commits into that first one.

Write and quit the file (in vim command mode, `:wq`)

Follow the instructions that the command line prints.

After rebasing, you will need to execute `git push -f`. Note the `-f`. It is necessary because rebasing changes the git history, and so github will not be able to merge.

### Reordering commits
If you work with many commits, sometimes when you run the rebase commands in the PieCentral README, your commits may become separated.

Suppose the first commit you have is `n` commits ago

`git rebase -i HEAD~n`

You should be put into a vim session with a file open listing a series of commits. Identify your commits, and simply reorder the lines so all of your commits are in order at the bottom of the list.

If you're feeling adventurous, you can simultaneously squash your commits by replacing `pick` with `squash` for all your commits except te first one.

Remember you will need to push with the `-f` flag.

# Stop Tracking Deleted Remote Branches

`git branch -r` will eventually become polluted with a bunch of deleted branches. This command cleans it. Found [here](http://railsware.com/blog/2014/08/11/git-housekeeping-tutorial-clean-up-outdated-branches-in-local-and-remote-repositories/)

`git remote prune origin`

# Running runtime
In the `runtime` folder:
* Install dependencies: `pip3 install pipenv` and `pipenv install --dev`
* Run the runtime: `python3 runtime.py`
* Run the runtime tests: `python3 runtime.py -t`

# Runtime Documentation
### Runtime Diagram
![Runtime Diagram](https://imgur.com/oz4wExt.png)
