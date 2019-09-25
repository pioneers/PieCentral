# foundry

`foundry` is a PiE project for painlessly managing IT resources like robots, driver stations, and developer environments.
We use [Ansible](https://www.ansible.com/) to automate deployments and version standardized configurations as code in PieCentral.
`foundry` unifies several prior disparate projects: `frankfurter`, `chrommunal`, and `axiom`.

## Setting Up a Development Environment

> ... but it works on my machine.

Anvil is the PiE development environment for all software projects--the means of production.
It saves you the hassle of setting up toolchains and getting them all to work together on a variety of platforms.

In just a few steps, you too can begin hacking away at your first PiE project!

1. Install [Virtualbox](https://www.virtualbox.org/), then [Vagrant](https://www.vagrantup.com/downloads.html).
   This will allow you to provision and run a virtual machine (VM).
   Your native operating system (OS) is called the _host_.
   The nested OS is known as the _guest_.
1. Download [PieCentral](https://github.com/pioneers/PieCentral/archive/master.zip) as a ZIP, then unzip it.
1. Open [`roles/base/defaults/main.yml`](roles/base/defaults/main.yml) in a text editor, and change `name` and `email` to your name and your `_@pioneers.berkeley.edu` email.
1. Open a terminal.
   * If you're using OS X, open the `Terminal` app.
   * If you're using Windows, open `Command Prompt`, or use [GitBash](https://gitforwindows.org/).
   * If you're using Linux, you probably already know how to open a terminal.
1. Your terminal has a current working directory (folder).
   You want to use the **c**hange **d**irectory (`cd`) command to navigate to the `PieCentral/foundry/anvil` directory, like `cd path/to/PieCentral/foundry/anvil`.
1. Run `vagrant up`.
   You should see a bunch of messages being printed to your screen.
   Vagrant is downloading lots of software, so this step might take a while (10 - 20 minutes).
1. Log into your machine with `vagrant ssh`.
   This will give you a shell (command line) inside the VM.
1. If you haven't already, sign up for a [GitHub](https://github.com/) account.
   GitHub hosts all PiE software projects.
   Send your GitHub username to your PM so that you can be invited to the @pioneers organization, and be on the lookout for an email to confirm your membership.
1. Run `cat ~/.ssh/id_rsa.pub`.
   It will print something like: `ssh-rsa <random characters> _@pioneers.berkeley.edu`.
   Copy this line and [follow these instructions](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account) for adding this key to your GitHub account.
   Now, whenever you push code, you won't need to enter a password.

Note that there is no desktop or windows you would normally find on an OS.
Anvil is currently command-line only, meaning all interactions with the machine need to be done through commands you type into your `vagrant ssh` session.

Also, the PieCentral you downloaded on the host will have a synchronized copy on the guest at `/vagrant/PieCentral`.
This means you can use your favorite text editor to make changes, and those changes will be automatically reflected inside Anvil.

Should you run into any issues, ask your peers or project manager.
If all else fails, feel free to submit a [bug report](https://github.com/pioneers/PieCentral/issues/new?assignees=&labels=DevOps,bug&template=bug_report.md&title=).

### Using the Development Environment

* `vagrant up`: Starts the VM if it is not already running.
* `vagrant ssh`: Logs you into the VM. You can always leave with the command `exit`.
* `vagrant halt`: Shuts down the VM.
* `vagrant reload`: Restarts the VM. Like running `vagrant halt`, then `vagrant up`.
* `vagrant provision`: Reruns Anvil setup. Run this whenever there's a new release of `foundry`.
* `vagrant status`: Reports the state of the VM.

Note that all of these commands have to be run on the host from `PieCentral/foundry/anvil`.
If you get a message like the one shown below, that means your current working directory is not `anvil`.
```
A Vagrant environment or target machine is required to run this
command. Run `vagrant init` to create a new Vagrant environment. Or,
get an ID of a target machine from `vagrant global-status` to run
this command on. A final option is to change to a directory with a
Vagrantfile and to try again.
```
