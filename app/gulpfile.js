var gulp = require('gulp');
var browserify = require('browserify');
var watchify = require('watchify');
var source = require('vinyl-source-stream');
var buffer = require('vinyl-buffer');
var uglify = require('gulp-uglify');

gulp.task('default', ['watch']);
gulp.task('build', ['scripts']);

gulp.task('scripts', function () {
  return browserify({
    entries: ['./client.js'],
    transform: [['coffee-reactify', {coffeeout: true}], 'coffeeify', 'reactify'],
    extensions: ['.coffee'],
    cache: {}, packageCache: {}, fullPaths: true
  })
    .bundle()
    .pipe(source('bundle.js'))
    .pipe(buffer())
    .pipe(uglify())
    .pipe(gulp.dest('./public/'));
});

gulp.task('watchscripts', function () {

  // http://stackoverflow.com/questions/24190351/using-gulp-browserify-for-my-react-js-modules-im-getting-require-is-not-define
  var bundler = browserify({
    entries: ['./client.js'],
    transform: [['coffee-reactify', {coffeeout: true}], 'coffeeify', 'reactify'],
    extensions: ['.coffee'],
    debug: true,
    cache: {}, packageCache: {}, fullPaths: true
  })
  var watcher  = watchify(bundler);

  return watcher
  .on('update', function () {
    var updateStart = Date.now();
    console.log('Scripts updating...');
    watcher.bundle()
    .pipe(source('bundle.js'))
    .pipe(gulp.dest('./public/'));
    console.log('Updated!', (Date.now() - updateStart) + 'ms');
  })
  .bundle() // Create the initial bundle when starting the task
  .pipe(source('bundle.js'))
  .pipe(gulp.dest('./public/'));

});

gulp.task('watch', ['watchscripts']);
