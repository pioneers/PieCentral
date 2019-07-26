const { Command, flags } = require('@oclif/command');

class ServerCommand extends Command {
  async run() {
    const { flags } = this.parse(ServerCommand);
    let port = flags.port;
    console.log(port);
  }
}

ServerCommand.flags = {
  version: flags.version({ char: 'v' }),
  help: flags.help({ char: 'h' }),
  port: flags.string({
    char: 'p',
    description: 'Port to run the server on',
    default: 6060,
  }),
};

module.exports = ServerCommand;
