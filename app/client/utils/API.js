import request from 'superagent';

// Adapted from
// https://github.com/schempy/react-flux-api-calls
export default {
  get(url) {
    return new Promise(function(resolve, reject) {
      request
        .get(url)
        .end(function(err, res) {
          if(res.status == 404) {
            reject('Not found');
          }
          else if(res.status == 500) {
            reject('Internal error');
          }
          else {
            resolve(res.text);
          }
        });
    });
  },
  post(url) {
  }
};
