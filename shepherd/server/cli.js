const { Command, flags } = require('@oclif/command');
const FieldControlEngine = require('./index');

class ServerCommand extends Command {
  async run() {
    const { flags } = this.parse(ServerCommand);
    let engine = new FieldControlEngine(flags);
    await engine.runForever();
  }
}

ServerCommand.flags = {
  version: flags.version({ char: 'v' }),
  help: flags.help({ char: 'h' }),
  host: flags.string({
    char: 'n',
    env: 'HOST',
    description: 'Host to bind the server to',
    default: '127.0.0.1',
  }),
  port: flags.string({
    char: 'p',
    env: 'PORT',
    description: 'Port to bind the server to',
    default: 8100,
  }),
  log: flags.string({
    char: 'l',
    description: 'Log path',
    default: 'log/aggregate.log',
  }),
  mode: flags.string({
    char: 'm',
    env: 'NODE_ENV',
    default: 'development',
    description: 'Mode',
    options: ['development', 'production'],
  }),
  'slack-token': flags.string({
    char: 's',
    env: 'SLACK_TOKEN',
    description: 'Slack token'
  }),
  'slack-channel': flags.string({
    env: 'SLACK_CHANNEL',
    default: '#shepherd-bot-testing',
    description: 'Slack channel'
  })
};

module.exports = ServerCommand;
