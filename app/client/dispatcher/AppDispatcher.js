import assign from 'object-assign';
import request from 'superagent';
import {Dispatcher} from 'flux';
import {ActionTypes} from '../constants/Constants'


export default assign(new Dispatcher(), {
  // Add methods to handle external API requests
  // to dispatcher. Adapted from
  // https://github.com/schempy/react-flux-api-calls
  get(url) {
    return new Promise(function(resolve, reject) {
      request
        .get(url)
        .end(function(err, res) {
          if(res.status == 404) {
            reject('Not found');
          } else if(res.status == 500) {
            reject('Internal error');
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
          if (res.status == 404) {
            reject('Not found');
          } else if (res.status == 500) {
            reject('Internal error');
          } else if (res.status == 413) {
            reject('Request too large');
          } else {
            resolve();
          }
        })
    })
  }
});
