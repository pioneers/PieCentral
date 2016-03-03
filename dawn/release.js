var minimist = require('minimist');
var packager = require('electron-packager');
var execSync = require('child_process').execSync;

function build() {
  console.log('Packaging with webpack, using the production config');
  var child = execSync('npm run-script build', function(err, stdout, stderr) {
    console.log('stderr: ', stderr);
    if (err !== null) {
      console.log('error: ', err);
    }
  });
}

function pack(prod, platform, arch) {
  var opts = {}; //packaging options

  if (prod) {
    console.log('Packaging for all platforms');
    opts.all = true; // build for all platforms and arch
  } else {
    console.log('Packaging for: ', platform, arch);
    opts.platform = platform;
    opts.arch = arch;
  }

  opts.dir = __dirname; // source dir
  opts.name = 'dawn';
  opts.prune = true; //remove dev dependencies
  opts.icon = './icons/icon';
  opts.version = '0.36.2';
  opts.out = '../..'

  packager(opts, function(err, appPath) {
    if (err) {
      console.log('Packaging error: ', err);
    } else {
      console.log(appPath);
    }
  });
}

// General release command: 'node release.js --prod'.
// If you already ran build: 'node release.js --prod --prebuilt'
// For a specific target: 'node release.js --platform=... --arch=...'
function main() {
  var argv = minimist(process.argv.slice(2));

  if (!argv.prebuilt) {
    build();
  }

  pack(argv.prod, argv.platform, argv.arch);
}

main();
