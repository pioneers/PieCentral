import request from 'superagent';
export default {
  // Add methods to handle external API requests
  // to dispatcher. Adapted from
  // https://github.com/schempy/react-flux-api-calls
  get(url) {
    return new Promise(function(resolve, reject) {
      request
        .get(url)
        .end(function(err, res) {
          if (err) {
            reject();
          } else {
            resolve(res.text);
          }
        });
    });
  },
  post(url, data) {
    return new Promise(function(resolve, reject) {
      request
        .post(url)
        .send(data)
        .end(function(err, res) {
          if (err) {
            reject();
          } else {
            resolve();
          }
        })
    })
  }
};
