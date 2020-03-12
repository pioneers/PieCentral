# Welcome to the PiE Central Repo!
![PiE Logo](docs/figures/logo.png)

[![Build Status](https://travis-ci.org/pioneers/PieCentral.svg?branch=master)](https://travis-ci.org/pioneers/PieCentral)

## What is the Central Repo?
PieCentral is the central repository that hosts all kit software projects:
- Hibike: our lightweight communications protocol designed for passing sensor data with the PiE robotics kit.
- Dawn: our cross-platform frontend for the PiE robotics control system.
- Runtime: the code that handles communication, state, and student code execution.
- DevOps: oversees the deployment pipeline from GitHub to Travis CI to Beaglebone boards.
- Shepherd: our full-stack field control software used during the competition.

If you want to learn more about these projects, check out their directories!

## Contributing to PieCentral
Note: You don't have to fork!
Instead, make your own branch in the central repo once you join the organization.

### Setting up PieCentral
```sh
$ cd "<directory of your choice>"
$ git clone https://github.com/pioneers/PieCentral.git
$ cd PieCentral
```

### Creating a Branch
Follow the naming convention `<project>/<feature>`.
Without the `<project>` name, your branch will not be built by Travis.
Feel free to name the `<feature>` anything or use more slashes.

Examples: `dawn/UDPintegration`, `runtime/andy/UDPintegration`
```sh
$ git checkout master  # Switch to default `master` branch
$ git checkout -b "<project>/<feature>"  # Create and switch to feature branch
$ git push -u origin "<project>/<feature>"
```

### Adding new code to master
Make sure any local changes to your code is pushed to your branch.

```sh
$ git add "<file1>" "<file2>"
$ git commit -m "<description>"
$ git push  # Pushes to `origin/<project>/<feature>` because of `-u` flag earlier
```

Open a pull request to `master`. Code will be reviewed by PMs.

Code will be rebased onto master.
(Choose "Squash and Merge" instead of "Create a merge commit".)
Make sure when merging your pull request you include a useful commit header and message.
