# foundry

`foundry` is a PiE project for painlessly managing IT resources like robots, driver stations, and developer environments.
We use [Ansible](https://www.ansible.com/) to automate deployments and version standardized configurations as code in PieCentral.
`foundry` unifies several prior disparate projects: `frankfurter`, `chrommunal`, and `axiom`.

## Development Environment

### Setup

> ... but it works on my machine.

Anvil is the PiE development environment for all software projects--it's the means of production.
It saves you the hassle of setting up toolchains and getting them all to work together on a variety of platforms.

:warning: **At this time, Anvil is currently an experimental project, so it's not unlikely for installation to fail. Please submit a [bug report](https://github.com/pioneers/PieCentral/issues/new?assignees=&labels=DevOps,bug&template=bug_report.md&title=) as needed with your terminal output and Virtualbox logs.**

In just a few steps, you too can begin hacking away at your first PiE project!

1. If you haven't already, sign up for a [GitHub](https://github.com/) account.
GitHub hosts all PiE software projects.
   Send your GitHub username to your PM so that you can be invited to the @pioneers organization, and be on the lookout for an email to confirm your membership.
1. Install [Virtualbox](https://www.virtualbox.org/), then [Vagrant](https://www.vagrantup.com/downloads.html).
   This will allow you to provision and run a virtual machine (VM).
   Your native operating system (OS) is called the _host_.
   The nested OS is known as the _guest_.
1. Open a terminal.
   * If you're using macOS, open the `Terminal` app.
   * If you're using Windows, install, then open, [GitBash](https://gitforwindows.org/).
   * If you're using Linux, you probably already know how to open a terminal.
1. Install [`git`](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
   If you're using GitBash, you already have `git` installed.
1. Use `cd` to navigate to the directory (folder) where you would like to download PieCentral.
1. Run `export NAME="<your name here>"` and `export EMAIL="<your email>@pioneers.berkeley.edu"`.
1. Run `bash -c "$(curl -fsSL https://raw.githubusercontent.com/pioneers/PieCentral/master/foundry/provisioning/anvil-install.sh)"`.
   Vagrant is now downloading a lot of software.
   Setup is fully autonomous, and should take about 10 minutes.
1. When the install script succeeds, it will print something like: `ssh-rsa <random characters> _@pioneers.berkeley.edu`.
   Copy this line and [follow these instructions](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account) for adding this key to your GitHub account.
   Now, whenever you push code, you won't need to enter a password.

Note that there is no desktop or windows you would normally find on an OS.
Anvil is currently command-line only, meaning all interactions with the machine need to be done through commands you type into a shell.
To log into the guest, use `vagrant ssh`.
You can log out with the command `exit`.

Also, the PieCentral repo the install script cloned on the host will have a synchronized copy on the guest at `/home/vagrant/PieCentral`.
This means you can use your favorite text editor on the host to make changes, and those changes will be automatically reflected inside Anvil.

### Usage

| Command | Result |
| --- | -- |
| `vagrant up` | Starts the VM if it is not already running and provisions resources. |
| `vagrant ssh` | Logs you into the VM. |
| `vagrant halt` | Shuts down the VM. |
| `vagrant reload` | Restarts the VM. Like running `vagrant halt`, then `vagrant up`. |
| `vagrant provision` | Reruns Anvil setup. Run this whenever there's a new release of `foundry`. |
| `vagrant status` | Reports the state of the VM. |
| `vagrant destroy` | Wipes out your VM from disk. |

Note that all of these commands have to be run on the host from `PieCentral/foundry/provisioning`.
If you get a message like the one shown below, that means your current working directory is not `provisioning`.
```
A Vagrant environment or target machine is required to run this
command. Run `vagrant init` to create a new Vagrant environment. Or,
get an ID of a target machine from `vagrant global-status` to run
this command on. A final option is to change to a directory with a
Vagrantfile and to try again.
```

Anvil's `Vagrantfile` accepts the following environment variables:

| Name | Result |
| --- | --- |
| `MOUNT_SYNCED` | Set to `no` to disable PieCentral on the host being mounted on the guest. |
| `PRIVATE_IP` | Give the machine an IP address like `10.10.10.10`. |
| `FORWARDED_PORTS` | Binds certain ports from the guest to the host. Comma-separated list of integers. |
| `NAME` | Configures your name during provisioning for `git`. |
| `EMAIL` | Configures your email during provisioning for `git`. |
| `DESKTOP` | Runs and provisions Anvil with a desktop. |

### Troubleshooting

* If you get an error along the lines of "`curl` is not a command", then you should:
   * Follow [this link](https://raw.githubusercontent.com/pioneers/PieCentral/master/foundry/provisioning/anvil-install.sh) in your browser.
   * Copy-and-paste the contents of the file into a text editor.
   * Save your file as `anvil-install.sh`.
   * Run `bash anvil-install.sh` from wherever you saved the script.
* If your internet connection fails midway through running `anvil-install.sh`, you may need to delete PieCentral and start over from step (7).
