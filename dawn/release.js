const minimist = require('minimist');
const packager = require('electron-packager');
const path = require('path');
const { execSync } = require('child_process');

function build() {
  console.log('Packaging with webpack, using the production config');
  execSync('yarn run build', (err, stdout, stderr) => {
    console.log('stderr: ', stderr);
    if (err !== null) {
      console.log('error: ', err);
    }
  });
}

function pack(platform, arch, noprune) {
  const opts = {}; // packaging options

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
  opts.prune = !noprune; // remove dev dependencies unless noprune is set
  opts.icon = './icons/pieicon';
  opts.asar = true;
  opts.out = path.resolve('..'); // build in the parent dir

  packager(opts, (err, appPath) => {
    if (err) {
      console.log('Packaging error: ', err);
      return;
    }
    if (typeof appPath === 'string') {
      console.log('Zipping: ', appPath);
      execSync(`7z a -tzip ${appPath}.zip ${appPath}`, (err, stdout, stderr) => {
        if (err !== null) {
          console.log('error: ', err);
        }
      });
    } else {
      appPath.forEach((folderPath) => {
        console.log('Zipping: ', folderPath);
        execSync(`7z a -tzip ${folderPath}.zip ${folderPath}`, (err, stdout, stderr) => {
          if (err !== null) {
            console.log('error: ', err);
          }
        });
      });
    }
  });
}

// General release command: 'node release.js --prod'.
// If you already ran build: 'node release.js --prod --prebuilt'
// For a specific target: 'node release.js --platform=... --arch=...'
function main() {
  const argv = minimist(process.argv.slice(2));

  if (!argv.prebuilt) {
    build();
  }

  pack(argv.platform, argv.arch, argv.noprune);
}

main();
