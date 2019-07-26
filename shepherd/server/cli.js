const { Command, flags } = require('@oclif/command');
const winston = require('winston');
const app = require('./views');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'shepherd' }
});

class ServerCommand extends Command {
  configureLogger(flags) {
    switch (flags.mode) {
      case 'production':
        logger.add(new winston.transports.File({
          filename: flags.log
        }));
        break;
      default:
        logger.add(new winston.transports.Console({
          level: 'debug',
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.printf(info => `${new Date().toISOString()} [${info.level}]: ${info.message}`)
          )
        }));
        break;
    }
  }

  async run() {
    const { flags } = this.parse(ServerCommand);
    this.configureLogger(flags);
    logger.debug('Logging initialized');
    app.listen(flags.port, flags.host, () => {
      logger.info(`Server listening on ${flags.host}:${flags.port}`, {
        host: flags.host,
        port: flags.port,
      });
    });
  }
}

ServerCommand.flags = {
  version: flags.version({ char: 'v' }),
  help: flags.help({ char: 'h' }),
  host: flags.string({
    char: 'n',
    description: 'Host to bind the server to',
    default: '127.0.0.1',
  }),
  port: flags.string({
    char: 'p',
    description: 'Port to bind the server to',
    default: 6060,
  }),
  log: flags.string({
    char: 'l',
    description: 'Log path',
    default: 'log/aggregate.log',
  }),
  mode: flags.string({
    mode: 'm',
    env: 'NODE_ENV',
    default: 'development',
    description: 'Mode',
    options: ['development', 'production'],
  }),
};

module.exports = ServerCommand;
