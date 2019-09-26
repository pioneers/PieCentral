# foundry

`foundry` is a PiE project for painlessly managing IT resources like robots, driver stations, and developer environments.
We use [Ansible](https://www.ansible.com/) to automate deployments and version standardized configurations as code in PieCentral.
`foundry` unifies several prior disparate projects: `frankfurter`, `chrommunal`, and `axiom`.

## Setting Up a Development Environment

> ... but it works on my machine.

Anvil is the PiE development environment for all software projects--the means of production.
It saves you the hassle of setting up toolchains and getting them all to work together on a variety of platforms.

In just a few steps, you too can begin hacking away at your first PiE project!

1. If you haven't already, sign up for a [GitHub](https://github.com/) account.
GitHub hosts all PiE software projects.
   Send your GitHub username to your PM so that you can be invited to the @pioneers organization, and be on the lookout for an email to confirm your membership.
1. Install [Virtualbox](https://www.virtualbox.org/), then [Vagrant](https://www.vagrantup.com/downloads.html).
   This will allow you to provision and run a virtual machine (VM).
   Your native operating system (OS) is called the _host_.
   The nested OS is known as the _guest_.
1. Download [`https://raw.githubusercontent.com/pioneers/PieCentral/master/foundry/provisioning/anvil-install.sh`](https://raw.githubusercontent.com/pioneers/PieCentral/master/foundry/provisioning/anvil-install.sh).
1. Open a terminal.
   * If you're using OS X, open the `Terminal` app.
   * If you're using Windows, install, then open, [GitBash](https://gitforwindows.org/).
   * If you're using Linux, you probably already know how to open a terminal.
1. Install [`git`](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
   If you're using GitBash, you already have `git` installed.
1. Use `cd` to navigate to the directory (folder) where you downloaded the install script.
1. Execute the install script with `bash anvil-install.sh`.
   Vagrant is now downloading a lot of software.
   Setup should take about 10 minutes.
1. When the install script succeeds, it will print something like: `ssh-rsa <random characters> _@pioneers.berkeley.edu`.
   Copy this line and [follow these instructions](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account) for adding this key to your GitHub account.
   Now, whenever you push code, you won't need to enter a password.

Note that there is no desktop or windows you would normally find on an OS.
Anvil is currently command-line only, meaning all interactions with the machine need to be done through commands you type into a shell.
To log into the guest, use `vagrant ssh`.
You can log out with the command `exit`.

Also, the PieCentral the install script downloaded on the host will have a synchronized copy on the guest at `/vagrant/PieCentral`.
This means you can use your favorite text editor to make changes, and those changes will be automatically reflected inside Anvil.

Should you run into any issues, ask your peers or project manager.
If all else fails, feel free to submit a [bug report](https://github.com/pioneers/PieCentral/issues/new?assignees=&labels=DevOps,bug&template=bug_report.md&title=).

### Using the Development Environment

* `vagrant up`: Starts the VM if it is not already running.
* `vagrant ssh`: Logs you into the VM.
* `vagrant halt`: Shuts down the VM.
* `vagrant reload`: Restarts the VM. Like running `vagrant halt`, then `vagrant up`.
* `vagrant provision`: Reruns Anvil setup. Run this whenever there's a new release of `foundry`.
* `vagrant status`: Reports the state of the VM.
* `vagrant destroy`: Wipes out your VM.

Note that all of these commands have to be run on the host from `PieCentral/foundry/anvil`.
If you get a message like the one shown below, that means your current working directory is not `anvil`.
```
A Vagrant environment or target machine is required to run this
command. Run `vagrant init` to create a new Vagrant environment. Or,
get an ID of a target machine from `vagrant global-status` to run
this command on. A final option is to change to a directory with a
Vagrantfile and to try again.
```
