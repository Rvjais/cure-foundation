<?php
/**
 * Front controller (Vercel via vercel.json, Apache via .htaccess,
 * PHP built-in server via router.php).
 */

require_once dirname(__DIR__) . '/includes/bootstrap.php';
cure_dispatch();
