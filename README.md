# Cure Foundation — Website

PHP version of the Cure Foundation India website.

Every page is a **single `.php` file in the web root**. There are no
per-page folders, no `pages/` folder, no router, no rewrite rules and no
front controller. Any Apache / LiteSpeed / Nginx-PHP host serves it as-is.

## URL scheme

The file name is the page's path with `/` replaced by `__`:

| URL | File |
|---|---|
| `/` | `index.php` |
| `/about-us.php` | `about-us.php` |
| `/donate.php` | `donate.php` |
| `/events.php` | `events.php` |
| `/events__category__children__2026-09.php` | `events__category__children__2026-09.php` |
| `/author__cureweb__page__2.php` | `author__cureweb__page__2.php` |

`__` was chosen because the original slugs already used it for nested
pages, so the mapping is unambiguous.

Trailing slashes are gone: `/about-us/` is not a valid URL any more,
`/about-us.php` is. Every link inside the site was rewritten accordingly
(4,400+ links: navigation, footer, in-content links, comment links,
canonical/alternate tags and the Give donation form actions).

## Structure

```
index.php                 homepage (/)
404.php                   friendly 404 page
about-us.php              /about-us.php
donate.php                /donate.php
events.php                /events.php
events__category__*.php   calendar views
...                       268 page files in total
includes/                 shared PHP library (never served directly)
  bootstrap.php           loads config + functions
  config.php              HTML shell + menu overrides
  functions.php           rendering helpers, menu "current item" logic
  head-common.php         shared <head>
  tail-common.php         shared closing scripts
  header-1.php header-2.php
  footer.php
  .htaccess               denies direct HTTP access (Apache only)
assets/                   all CSS / JS / fonts / images
genmod/                   original conversion generator (historical)
```

There is **no required configuration**. `.htaccess` is optional and only
adds `ErrorDocument 404 /404.php`; routing works without it.

## Runtime behaviour

- **Calendar exports**: `?ical=1` and `?outlook-ical=1` on any page return
  `HTTP 204` with `Content-Type: text/calendar`. Handled in
  `cure_render_page()` in `includes/functions.php`.
- **Menu highlighting**: `mark_current_menu()` compares the page's logical
  URL (`$page['url']`, e.g. `/author/cureweb/page/2/`) with the hrefs in the
  shared header/footer. `cure_norm_path()` strips `.php` and turns `__` back
  into `/`, so `/author__cureweb__page__2.php` still matches the paginated
  archive logic.
- Pages whose "current item" classes only the WordPress object graph could
  compute replay recorded tokens from `$CURE_MENU_OVERRIDES` in
  `includes/config.php` (keyed by the logical URL).

## Local development

```
php -S localhost:8000
```

Then open <http://localhost:8000/>. No router argument is needed.

## Deployment

Upload the whole tree to the document root:

- no `vercel.json`
- no `router.php`
- no rewrite rules
- `.htaccess` optional

When updating an existing server, delete leftovers from earlier layouts:
the old `pages/` folder, `api/`, `router.php`, `vercel.json`, and any
per-page folders such as `about-us/index.php`.

## Known leftovers from the static mirror

A few links still point at things this static export does not contain and
were already dead before the flattening: WordPress feeds (`/feed`,
`/comments/feed`, `/events/feed`), `/xmlrpc.php`, `/wp-comments-post.php`,
and calendar day links for dates that were never exported. They are left
as-is because there is nothing to point them at.

## Regenerating the PHP output

`genmod/` holds the Python generator used for the original HTML → PHP
conversion. It requires the original static mirror, which is no longer in
the repository, and it emits the old `pages/*.php` layout. Treat it as
historical reference — the flat tree described above is the source of
truth.
