var minimist = require('minimist');
var packager = require('electron-packager');
var exec = require('child_process').exec;

function build() {
  console.log('Packaging with webpack, using the production config');
  var child = exec('npm run-script build', function(err, stdout, stderr) {
    console.log('stderr: ', stderr);
    if (err !== null) {
      console.log('error: ', err);
    }
  });
}

function pack(all, platform, arch, prune) {
  var opts = {}; //packaging options

  if (all) {
    console.log('Packaging for all platforms');
    opts.all = true; // build for all platforms and arch
  } else {
    console.log('Packaging for: ', platform, arch);
    opts.platform = platform;
    opts.arch = arch;
  }
  opts.dir = '.'; // source dir
  opts.name = 'dawn';
  opts.prune = prune; //remove dev dependencies
  opts.icon = './icons/icon';
}

function main() {
  var argv = minimist(process.argv.slice(2));

  if (argv.build) {
    build();
  }

  pack(argv.all, argv.platform, argv.arch, argv.prune);
}

main();
