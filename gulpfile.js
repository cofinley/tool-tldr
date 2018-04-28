'use strict';
var staticPath = "./app/static/";

var jsFileOrder = [
    staticPath + 'js/lib/**/*.js',
    '!' + staticPath + 'js/lib/webfont_loader.js',
    staticPath + 'js/app/**/*.js'
];

var gulp = require('gulp');

var cleanCSS = require('gulp-clean-css');
var jshint = require('gulp-jshint');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');
var sassLint = require('gulp-sass-lint');

// Lint Task, only lint my js files
gulp.task('js-lint', function () {
    return gulp.src(staticPath + "js/app/**/*.js")
        .pipe(jshint())
        .pipe(jshint.reporter('default'));
});

gulp.task('sass-lint', function () {
    return gulp.src(staticPath + 'scss/**/*.s+(a|c)ss')
        .pipe(sassLint({
            rules: {
                'no-ids': 0,
                'property-sort-order': 0,
                'nesting-depth': 0,
                'no-important': 0
            }
        }))
        .pipe(sassLint.format())
        .pipe(sassLint.failOnError());
});

gulp.task('sass', function () {
    return gulp.src(staticPath + 'scss/app/style.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest(staticPath + 'css'));
});

gulp.task('minify-css', ['sass'], function () {
    return gulp.src(staticPath + 'css/**/*.css')
        .pipe(concat('all.css'))
        .pipe(gulp.dest(staticPath + 'dist'))
        .pipe(rename('all.min.css'))
        .pipe(cleanCSS({level: {1: {specialComments: 0}}}))
        .pipe(gulp.dest(staticPath + 'dist'));
});

// Concatenate & Minify JS
gulp.task('scripts', function () {
    return gulp.src(jsFileOrder)
        .pipe(concat('all.js'))
        .pipe(gulp.dest(staticPath + 'dist'))
        .pipe(rename('all.min.js'))
        .pipe(uglify())
        .on('error', function (err) {
            console.log(err.toString());
            this.emit('end');
        })
        .pipe(gulp.dest(staticPath + 'dist'));
});

//Watch task
gulp.task('watch', function () {
    gulp.watch(staticPath + 'js/**/*.js', ['js-lint', 'scripts']);
    gulp.watch(staticPath + 'css/**/*.css', ['minify-css']);
    gulp.watch(staticPath + 'scss/**/*.scss', ['sass', 'minify-css']);
});

// Default Task
gulp.task('default', ['js-lint', 'sass-lint', 'sass', 'scripts', 'minify-css', 'watch']);

// Compile (default without watch)
gulp.task('compile', ['js-lint', 'sass', 'scripts', 'minify-css']);
