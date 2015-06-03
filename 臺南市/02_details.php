<?php

$tmpPath = dirname(__DIR__) . '/tmp/tainan/details';

if (!file_exists($tmpPath)) {
    mkdir($tmpPath, 0777, true);
}

$currentPage = 1;
$totalPages = 1;
$totalPagesGot = false;

$fh = fopen(dirname($tmpPath) . '/list.csv', 'r');
$allFh = fopen(__DIR__ . '/all.csv', 'w');
$lineHeaders = false;

/*
 * Array
  (
  [0] => id
  [1] => 編號
  [2] => 性別
  [3] => 捕獲
  [4] => 地點
  [5] => 位置
  [6] => 籠舍
  [7] => url
  [8] => image_url
  )
 */
fgets($fh, 512);
while ($line = fgetcsv($fh, 2048)) {
    if(!isset($line[7])) {
        print_r($line);
        exit();
    }
    $tmpFile = $tmpPath . '/' . $line[0];
    if (!file_exists($tmpFile) || filesize($tmpFile) <= 0) {
        file_put_contents($tmpFile, file_get_contents($line[7]));
    }
    $detail = file_get_contents($tmpFile);
    $pos = strpos($detail, '收容編號');
    $pos = strpos($detail, '收容編號', $pos + 1);
    if (false !== $pos) {
        $dataLine = array();
        $detail = substr($detail, $pos, strpos($detail, '<table', $pos) - $pos);
        $blockLines = explode('<br/>', $detail);
        foreach ($blockLines AS $blockLineKey => $blockLine) {
            $cols = explode('：', $blockLine);
            if (isset($cols[1])) {
                $dataLine[trim($cols[0])] = trim($cols[1]);
            }
        }
        $dataLine['url'] = $line[7];
        $dataLine['image_url'] = $line[8];
        if (false === $lineHeaders) {
            $lineHeaders = true;
            fputcsv($allFh, array_keys($dataLine));
        }
        fputcsv($allFh, $dataLine);
    }
}