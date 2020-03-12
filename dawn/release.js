const minimist = require('minimist');
const packager = require('electron-packager');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

/* General release command: 'node release.js'
 * For a specific target: 'node release.js --platform=... --arch=...'
 */
function pack(platform, arch) {
  const packageOptions = {
    dir: __dirname, // source dir
    name: 'dawn',
    icon: './icons/pieicon',
    asar: true,
    packageManager: 'yarn',
    out: path.resolve('..'), // build in the parent dir
  };

  if (!platform || !arch) {
    console.log('Packaging for all platforms');
    packageOptions.all = true; // build for all platforms and arch
  } else {
    console.log('Packaging for: ', platform, arch);
    packageOptions.platform = platform;
    packageOptions.arch = arch;
  }

  packager(packageOptions)
    .then(appPaths => Promise.all(appPaths.map(appPath => {
      if (appPath === true) {
        return;
      }
      console.log(`Zipping ${appPath}`);
      return promisify(exec)(`cd .. && zip -r ${appPath}.zip ${path.basename(appPath)}`);
    })))
    .catch(err => {
      console.log(err);
    });
}

function main() {
  const argv = minimist(process.argv.slice(2));
  pack(argv.platform, argv.arch);
  console.log('Packaging Done');
}

main();
