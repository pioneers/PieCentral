const winston = require('winston');
const buildServer = require('./views');
const SlackNotificationClient = require('./notification');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'shepherd' }
});

class FieldControlEngine {
  constructor(flags) {
    this.flags = flags;
    this.app = buildServer(logger, flags);
    this.slackClient = new SlackNotificationClient(logger, flags['slack-token']);
  }

  configureLogger() {
    switch (this.flags.mode) {
      case 'production':
        logger.add(new winston.transports.File({
          filename: this.flags.log
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

  async runForever() {
    this.configureLogger();
    logger.debug(`Running server with mode "${this.flags.mode}"`);
    logger.debug('Logging initialized');

    let host = this.flags.host, port = this.flags.port;
    this.app.listen(port, host, () => {
      logger.info(`Server listening on ${host}:${port}`, {host, port});
    });
  }
}

module.exports = FieldControlEngine;
