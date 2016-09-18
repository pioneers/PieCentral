# Welcome to the PiE Central Repo!

![alt text][logo]

## What is the Central Repo?
 - The PiE Central Repo is our main central repository that contains a bunch of other PiE repositories, including...
 
     - Hibike, our lightweight communications protocol designed for the passing of sensor data for the PiE Robotics Kit
     - Dawn, our cross-platform frontend for the PiE robotics control system
     - Atalanta, the runtime code in our beaglebones
     - Protos, our protocol buffers used by Dawn and runtime
     - DevOps, which oversees axiom, frankfurter, and chrommunal
    
    ***Note that Hibike and Dawn are currently using the develop branch***

### If you want to learn more about these repositories, check out their directories!

## Contributing to PieCentral
### Setting up PieCentral

```
$ cd {directory of your choice}
$ git clone https://github.com/pioneers/PieCentral.git
$ cd PieCentral
```

### Creating a Branch
Naming convention: project_name/feature_name

Feel free to name "feature_name" anything and/or use more slashes.

e.g. dawn/UDPintegration, atalanta/andy/UDPintegration
```
$ git branch {project_name/feature_name}
$ git checkout {project_name/feature_name}
$ git push origin {project_name/feature_name}
```

### Adding new code to master
All code is rebased onto master, meaning new commits are added directly onto master, creating a linear commit history.

Merge conflicts may arise when rebasing, make sure to fix conflicts before continuing.

```
$ git fetch origin master
$ git rebase master
$ git push {project_name/feature_name}
```
Open a pull request to master.

Code will be code reviewed by PMs.

Code will be rebased onto master. (Choose "Squash and Merge" instead of "Create a merge commit")

[logo]: https://upload.wikimedia.org/wikipedia/en/e/e4/Pioneers_in_Engineering_Logo_1.png "Logo"
