<?php
/**
 * 404 page, rendered through the shared header/footer.
 */

if (!defined('CURE_ROOT')) {
    require_once __DIR__ . '/includes/bootstrap.php';
}

cure_render_page(array(
    'url'        => '/__404__',
    'wp_id'      => null,
    'body_class' => 'error404',
    'head_dyn'   => array(),
    'head_extra' => array(),
    'content'    => <<<'CURE_404_EOF'
<div class="content-area">
    <div class="container">
        <div style="padding:64px 0;text-align:center;">
            <h1>Page not found</h1>
            <p>The page you requested could not be found.</p>
            <p><a href="/">Back to the home page</a></p>
        </div>
    </div>
</div>
CURE_404_EOF,
    'tail_dyn'   => array(),
    'tail_extra' => array(),
));
