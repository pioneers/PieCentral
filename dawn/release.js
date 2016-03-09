var minimist = require('minimist');
var packager = require('electron-packager');
var execSync = require('child_process').execSync;
var path = require('path');

function build() {
  console.log('Packaging with webpack, using the production config');
  var child = execSync('npm run-script build', function(err, stdout, stderr) {
    console.log('stderr: ', stderr);
    if (err !== null) {
      console.log('error: ', err);
    }
  });
}

function pack(platform, arch, noprune) {
  var opts = {}; //packaging options

  if (!platform || !arch) {
    console.log('Packaging for all platforms');
    opts.all = true; // build for all platforms and arch
  } else {
    console.log('Packaging for: ', platform, arch);
    opts.platform = platform;
    opts.arch = arch;
  }

  opts.dir = __dirname; // source dir
  opts.name = 'dawn';
  opts.prune = !noprune; //remove dev dependencies unless noprune is set
  opts.icon = './icons/pieicon';
  opts.asar = true;
  opts.version = '0.36.2';
  opts.out = path.resolve('..'); // build in the parent dir

  packager(opts, function(err, appPath) {
    if (err) {
      console.log('Packaging error: ', err);
    } else {
      if (typeof appPath === 'string') {
	console.log('Zipping: ', appPath);
	execSync(`7z a -tzip ${appPath}.zip ${appPath}`, function(err, stdout, stderr) {
	  if (err !== null) {
	    console.log('error: ', err);
	  }
	});
      } else {
	appPath.forEach(function(folderPath) {
	console.log('Zipping: ', folderPath);
	  execSync(`7z a -tzip ${folderPath}.zip ${folderPath}`, function(err, stdout, stderr) {
	    if (err !== null) {
	      console.log('error: ', err);
	    }
	  });
	});
      }
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

  pack(argv.platform, argv.arch, argv.noprune);
}

main();
