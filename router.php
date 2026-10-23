<?php
/**
 * Router for the PHP built-in development server:
 *   php -S localhost:8000 router.php
 */

$root = __DIR__;
$path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';

// Internal modules end up here via API (routes / not the front controller design),
// and legacy *.html mirrors route to the front controller's 301 redirects.
$internal = preg_match('~^/(pages|includes)/~', $path)
    || preg_match('~\.html$~i', $path)
    || ($path[1] ?? '') === '_';
if (!$internal && $path !== '/' && is_file($root . $path)) {
    return false;  // let php -S serve the static file directly
}

require __DIR__ . '/api/index.php';
