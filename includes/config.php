<?php
/**
 * Configuration for the generated PHP site.
 * $CURE_HTML_SHELL / $CURE_END_HTML hold the shared page shell.
 * $CURE_MENU_OVERRIDES holds per-page menu "current item" class tokens for
 * the few pages whose classes only the WordPress object graph can compute
 * (single-post pages under a category, non-anchor page wrappers).
 */

defined('CURE_ROOT') || define('CURE_ROOT', dirname(__DIR__));


$CURE_HTML_SHELL = '<!DOCTYPE html>

<html lang="en-US">
<head>
';
$CURE_END_HTML   = '</body>
</html>
';

$CURE_MENU_OVERRIDES = array(
    '/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/about-us/' => array(
        '13993' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-8923 ubermenu-current_page_item',
        '19739' => 'current-menu-item page_item page-item-8923 current_page_item',
    ),
    '/anti-tobacco-programs/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18799' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18676 ubermenu-current_page_item',
        '19746' => 'current-menu-item page_item page-item-18676 current_page_item',
    ),
    '/awareness-events/' => array(
        '17343' => 'ubermenu-current-menu-ancestor',
        '17344' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent ubermenu-current_page_parent ubermenu-current_page_ancestor',
        '18972' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18962 ubermenu-current_page_item',
        '19747' => 'current-menu-item page_item page-item-18962 current_page_item',
    ),
    '/awareness-program/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '19533' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-19527 ubermenu-current_page_item',
        '19748' => 'current-menu-item page_item page-item-19527 current_page_item',
    ),
    '/become-a-volunteer/' => array(
        '17365' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '17366' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-9102 ubermenu-current_page_item',
    ),
    '/cancer-crusaders-golf-cup/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '19069' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-19061 ubermenu-current_page_item',
        '19750' => 'current-menu-item page_item page-item-19061 current_page_item',
    ),
    '/category/events/cancer-conferences/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '19389' => 'ubermenu-current-menu-item',
    ),
    '/category/events/cancer-survivors-day/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '19468' => 'ubermenu-current-menu-item',
    ),
    '/charter/' => array(
        '17228' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-9104 ubermenu-current_page_item',
    ),
    '/contact-us/' => array(
        '17137' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-9110 ubermenu-current_page_item',
        '19740' => 'current-menu-item page_item page-item-9110 current_page_item',
    ),
    '/digital/' => array(
        '17343' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18809' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-9112 ubermenu-current_page_item',
    ),
    '/donate/' => array(
        '17365' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18876' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18861 ubermenu-current_page_item',
    ),
    '/early-screening-and-detection/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18975' => 'ubermenu-current-menu-item',
    ),
    '/for-children/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18459' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18449 ubermenu-current_page_item',
        '19742' => 'current-menu-item page_item page-item-18449 current_page_item',
    ),
    '/for-children/page/2/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18459' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18449 ubermenu-current_page_item',
        '19742' => 'current-menu-item page_item page-item-18449 current_page_item',
    ),
    '/for-women/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18798' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18793 ubermenu-current_page_item',
        '19743' => 'current-menu-item page_item page-item-18793 current_page_item',
    ),
    '/for-women/page/2/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18798' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18793 ubermenu-current_page_item',
        '19743' => 'current-menu-item page_item page-item-18793 current_page_item',
    ),
    '/honoured-cancer-survivors-at-apollo-cancer-centre-hyderabad/' => array(
        '19468' => 'ubermenu-current-post-ancestor ubermenu-current-menu-parent ubermenu-current-post-parent',
    ),
    '/i-am-a-aurvivor/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '19060' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-19055 ubermenu-current_page_item',
        '19744' => 'current-menu-item page_item page-item-19055 current_page_item',
    ),
    '/ocular-oncology-workshop/' => array(
        '19389' => 'ubermenu-current-post-ancestor ubermenu-current-menu-parent ubermenu-current-post-parent',
    ),
    '/our-history/' => array(
        '19741' => 'current-menu-item page_item page-item-9100 current_page_item',
    ),
    '/page/12/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/13/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/14/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/15/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/16/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/2/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/3/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/4/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/5/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/6/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/page/7/' => array(
        '17378' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-6267 ubermenu-current_page_item',
        '19738' => 'current-menu-item page_item page-item-6267 current_page_item',
    ),
    '/print/' => array(
        '17343' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18808' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-17650 ubermenu-current_page_item',
    ),
    '/videos/' => array(
        '17343' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '17344' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-9116 ubermenu-current_page_item ubermenu-current-menu-ancestor ubermenu-current-menu-parent ubermenu-current_page_parent ubermenu-current_page_ancestor',
        '18971' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-9116 ubermenu-current_page_item',
        '19749' => 'current-menu-item page_item page-item-9116 current_page_item',
    ),
    '/world-cancer-day/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18460' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18352 ubermenu-current_page_item',
        '19745' => 'current-menu-item page_item page-item-18352 current_page_item',
    ),
    '/world-cancer-day/page/2/' => array(
        '13994' => 'ubermenu-current-menu-ancestor ubermenu-current-menu-parent',
        '18460' => 'ubermenu-current-menu-item ubermenu-page_item ubermenu-page-item-18352 ubermenu-current_page_item',
        '19745' => 'current-menu-item page_item page-item-18352 current_page_item',
    ),
);
