Workflow
========

Working with Git
----------------

Branching
`````````

Branches are cheap, so use them often.

.. code-block::

  git checkout -b runtime/my-feature
  git push -u origin runtime/my-feature

When you are ready to merge a feature into ``master`` (or ``runtime/master``), open a new pull request with a summary of the changes.
PieCentral's ``CODEOWNERS`` has been configured to automatically notify the managers of the projects whose code you modified.
You may want to include the director to expedite code review.

Committing
``````````

- **Required**: This goes without saying, but above all else, **please write informative commit messages**.
  At a minimum, start with a one-line summary of the change.
  You may add a verbose commit message after the summary with paragraph-style prose or bullet points.
  Try to be detailed enough so that a reviewer can understand the change without needing to read the source.
  Don't be afraid to commit and push often to save your work, but try to make commits self-contained.
- **Required**: Obtain the latest updates to any source branch you're merging into.
  This forces you to make sure your changes are compatible with changes that have occurred since you branched.
  You can do this one of two ways:

  - **Strongly recommended**: Rebase onto the source branch to clean your Git history.

    .. code-block::

      git rebase -i <source>

    First, the base of your current branch is moved onto the ``HEAD`` of the ``<source>`` branch, as if all the branches are merged sequentially.
    Second, an interactive session will start that will allow you to squash many smaller, related commits into one or edit commit messages.
    For large features, this is preferable to squashing the entire branch when merging, since some of the history is preserved.

  - Alternatively, run:

    .. code-block::

      git pull origin <source>

    This forces a merge from the ``HEAD`` (tip) of the `<source>` branch into your current branch.
    This is less desirable, since merging complicates the Git history.

- **Required**: Clean up merged and stale branches to reduce clutter.
  For pull requests, there is an option to revert the change, so it's OK to delete associated branch.
  Remember to run ``git update`` (alias below) to clean up your local history.

- **Required**: Check for secrets (sensitive data) before pushing.
  For example, Slack webhook URLs are secured through randomness; exposing these URLs in GitHub (especially if the repository is open-source) allows anyone with the URL to post in a channel.
  Furthermore, hardcoded secrets are harder to rotate (a code change and review is required).
  Secrets can be passed as environment variables or through the command line.

- **Optional**: Use a prefix ``[Runtime]`` or ``[Lowcar]`` before the one-line summary.
  Branches already delineate what project a commit belongs to, so this convention hasn't been that useful.

Stashing
````````

Often times, you will want to switch branches, but your current changes do not warrant a new commit.
``git stash`` creates and restores temporary "commits", allowing you to clean your staging area and switch branches while resuming work on that stash later.
The stashes are placed on a `stack <https://en.wikipedia.org/wiki/Stack_(abstract_data_type)>`_, where the last stash created is the first one restored.

.. code-block::

  git stash
  git stash pop

Other Notes
```````````

Useful Git aliases:

.. code-block::

  graph = log --graph --oneline --all   # Opens a pager with the Git history in graphical form
  update = fetch --all --prune          # Pulls added/deleted upstream branches
  delta = diff --stat HEAD~1            # What files have changed since the last commit

Delete a branch on the remote from your ``git`` client:

.. code-block::

  git push --delete origin <branch>

Sometimes, you create a bad commit (accidentally staged some files) that you want to amend (overwrite in place):

.. code-block::

  git commit --amend

If the bad commit has already been pushed, you can force GitHub to accept your amended commit with:

.. code-block::

  git push --force

Generally, this is not good practice.
Only amend and force-push if you're the only one working on your branch.

Documentation
-------------

TL;DR: update this guide often.

Testing
-------
