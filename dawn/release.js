const fs = require('fs-extra');
const JSZip = require('jszip');
const minimist = require('minimist');
const packager = require('electron-packager');
const path = require('path');
const { execSync } = require('child_process');

async function pack(platform, arch) {
  const packageOptions = {
    dir: __dirname, // source dir
    name: 'dawn',
    icon: './icons/pieicon',
    asar: true,
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

  const appPaths = await packager(packageOptions);
  for (const folderPath of appPaths) {
    console.log('Zipping: ', folderPath);
    const zip = new JSZip().folder(folderPath);
    const zipContents = await zip.generateAsync({
      type: 'nodebuffer',
    });

    await fs.writeFile(`${folderPath}.zip`, zipContents);
  }
}

// General release command: 'node release.js --prod'.
// For a specific target: 'node release.js --platform=... --arch=...'
async function main() {
  const argv = minimist(process.argv.slice(2));
  try {
    await pack(argv.platform, argv.arch);
    console.log('Packaging successful');
  } catch (err) {
    console.log('Packaging error: ', err);
  }
}

main();
