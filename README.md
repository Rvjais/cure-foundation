# Cure Foundation — Website

PHP conversion of the Cure Foundation India website. The original static
WordPress mirror of 317 `.html` files was ported to PHP with shared
includes, exact 1:1 visual and structural fidelity (verified page-by-page),
clean URLs, and Vercel deployment support.

## Structure

```
api/index.php          Front controller (used by Vercel)
router.php             php -S local router (dev only)
index.php              Homepage (rendered at /)
404.php                Fallback 404 page
includes/
  config.php           Route table, HTML shell constants, per-page menu overrides
  functions.php        Dispatch, current-menu marking, menu-override helpers
  bootstrap.php        Session/load-time bootstrapping
  head-common.php      Shared <head> elements
  tail-common.php      Shared scripts/closing elements
  header-1.php         Header variant 1 (<header> + navigation)
  header-2.php         Header variant 2 (logo markup differs only)
  footer.php           Shared <footer>
pages/                 268 page modules + 50 iCal/Outlook HTTP-204 stubs
assets/                All CSS/JS/fonts/images (unchanged from the original)
genmod/                Python generator that produced the above from the
                       original HTML mirror (kept for future regeneration)
```

Pages live in `pages/` with mirror filenames where `__` stands for `/`:
`pages/events__category__children__2026-09.php` serves
`/events/category/children/2026-09/`.

## Local development

```
php -S localhost:8000 router.php
```

## Deployment (Vercel)

`vercel.json` routes:

- `/assets/(.*)` → served statically
- everything else → `api/index.php` (runtime `vercel-php@0.9.0`, PHP 8.5)

`includeFiles` bundles `includes/`, `pages/`, `index.php` and `404.php` into
the function. The front controller does the clean-URL routing, issues the
301 redirects (legacy `*.html` URLs, no-trailing-slash paths) and serves the
iCal calendar stubs as `HTTP 204`.

## Runtime behaviour

- Clean URLs derived from the original mirror permalink structure.
- Legacy paths (`/index.html`, `/pages/<slug>.html`) 301-redirect to the
  clean URL; non-slashed clean paths redirect to the slashed variant.
- `/includes/` and `/pages/` are never served directly (`.htaccess` locally,
  route table on Vercel).
- Event calendar exports (`?ical=1`, `?outlook-ical=1`) return `HTTP 204`
  with `Content-Type: text/calendar`, as the intended behaviour for stubs.
- WordPress/UberMenu "current menu item" classes are applied at runtime
  (`mark_current_menu()` in `includes/functions.php`); the few pages
  whose classes depend on the WordPress object graph replay their recorded
  tokens from `$CURE_MENU_OVERRIDES` in `includes/config.php`.
- The header search widget from the original design is intentionally not
  rendered.

## Regenerating the PHP output

If the content ever needs to be re-ported (new pages added to the original
window), the full pipeline lives in `genmod/`:

```
python -m genmod.run     # requires the original HTML mirror + reference copy
```

## History

The original static HTML mirror and every intermediate state are preserved
in git history: the static site at `3b6bff4`, the PHP conversion at
`6063b9f`, and the mirror removal by `git rm` afterwards.
