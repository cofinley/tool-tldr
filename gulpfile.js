'use strict';
var staticPath = "./app/static/";

var jsFileOrder = [
	staticPath + 'js/app/utils.js',
	staticPath + 'js/lib/tree.jquery.js',
	staticPath + 'js/app/explore_tree.js',
	staticPath + 'js/app/alert.js',
	staticPath + 'js/app/autocomplete.js',
	staticPath + 'js/app/diff_radio_buttons.js',
	staticPath + 'js/app/edit_page.js'
];

var gulp = require('gulp');

var cleanCSS = require('gulp-clean-css');
var jshint = require('gulp-jshint');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');

// Lint Task, only lint my js files
gulp.task('lint', function () {
    return gulp.src(staticPath + "js/app/*.js")
        .pipe(jshint())
        .pipe(jshint.reporter('default'));
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
        .pipe(gulp.dest(staticPath + 'dist'));
});

//Watch task
gulp.task('watch', function () {
	gulp.watch(staticPath + 'js/**/*.js', ['lint', 'scripts']);
    gulp.watch(staticPath + 'scss/**/*.scss', ['sass', 'minify-css']);
});

// Default Task
gulp.task('default', ['lint', 'sass', 'scripts', 'minify-css', 'watch']);
