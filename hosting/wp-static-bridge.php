<?php
/* SEZAM11_MANAGED_BRIDGE: additive route handler; WordPress and its database stay intact. */
if (!defined('ABSPATH')) { exit; }
$sezamRoot = dirname(rtrim(ABSPATH, '/')).'/.sezam11-production';
if (!is_file($sezamRoot.'/production.enabled')) { return; }
$sezamSite = realpath($sezamRoot.'/current');
if (!$sezamSite || dirname($sezamSite) !== $sezamRoot.'/releases') { return; }
$sezamPath = rawurldecode(parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/');
if (strpos($sezamPath, "\0") !== false || in_array('..', explode('/', $sezamPath), true)) { return; }
$sezamRoutes = json_decode(file_get_contents($sezamSite.'/routes.json'), true);
if (!isset($sezamRoutes[$sezamPath])) { return; } // Historical WP routes still handled by WP.
$sezamFile = $sezamSite.'/'.$sezamRoutes[$sezamPath];
if (!is_file($sezamFile)) { return; }
http_response_code(200);
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store, max-age=0');
header('X-Sezam11-Commit: '.json_decode(file_get_contents($sezamSite.'/deployment.json'), true)['commit']);
readfile($sezamFile);
exit;
