const { WebClient } = require('@slack/web-api');

class SlackNotificationClient {
  constructor(logger, token) {
    this.logger = logger;
    this.web = new WebClient(token);
  }

  async postEStop() {
    await this.web.chat.postMessage({
      channel: '#shepherd-bot-testing',
      blocks: [{
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: ':fire: Shepherd has engaged e-stop due to safety issues on the field.'
        }
      }]
    });
  }
}

module.exports = SlackNotificationClient;
