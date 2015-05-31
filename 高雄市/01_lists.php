<?php

$tmpPath = dirname(__DIR__) . '/tmp/ks';

if (!file_exists($tmpPath)) {
    mkdir($tmpPath, 0777, true);
}

$currentPage = 1;
$totalPages = 1;
$totalPagesGot = false;

$fh = fopen($tmpPath . '/list.csv', 'w');
$lineHeaders = false;

for (; $currentPage <= $totalPages; $currentPage++) {
    $listUrl = 'http://asms.wsn.com.tw/KS/ieland/el_LoseList.aspx?Page=' . $currentPage;
    $tmpList = $tmpPath . '/list_' . $currentPage;
    if (!file_exists($tmpList)) {
        file_put_contents($tmpList, file_get_contents($listUrl));
    }
    $listHtml = file_get_contents($tmpList);

    if (false === $totalPagesGot) {
        /*
         * try to get page number
         */
        $pos = strpos($listHtml, '<span id="showpage">');
        if (false !== $pos) {
            $totalPages = intval(strip_tags(substr($listHtml, $pos, strpos($listHtml, '</span>', $pos))));
            $totalPagesGot = true;
        } else {
            die("can't find showpage!\n");
        }
    }

    $pos = strpos($listHtml, '<table id="DataList1"');
    if (false !== $pos) {
        $listHtml = substr($listHtml, $pos);
        $listHtml = str_replace('\\', '', $listHtml);
        $lines = explode('</tr>', $listHtml);
        foreach ($lines AS $line) {
            $blocks = explode('</td>', $line);
            foreach ($blocks AS $block) {
                $record = array(
                    'id' => false,
                );
                $fields = explode('</li>', $block);
                if (count($fields) === 8) {
                    foreach ($fields AS $fieldKey => $field) {
                        switch ($fieldKey) {
                            case 3:
                                $field = explode('&nbsp;&nbsp;&nbsp;&nbsp;', trim(strip_tags($field)));
                                $record[trim($field[0])] = trim($field[1]);
                                break;
                            case 6:
                                $field = explode('?ID=', $field);
                                $record['id'] = substr($field[1], 0, strpos($field[1], '&'));
                                $record['url'] = 'http://asms.wsn.com.tw/KS/ieland/el_LoseDetail.aspx?ID=' . $record['id'] . '&fn=Photo&tn=SheltersReco';
                                break;
                            case 7:
                                $field = explode('../Upload/', $field);
                                $record['image_url'] = '';
                                if (isset($field[1])) {
                                    $record['image_url'] = 'http://asms.wsn.com.tw/KS/Upload/' . substr($field[1], 0, strpos($field[1], '"'));
                                }
                                break;
                            default:
                                $field = explode('：', trim(strip_tags($field)));
                                $record[trim($field[0])] = trim($field[1]);
                        }
                    }
                }
                if (false !== $record['id']) {
                    if (false === $lineHeaders) {
                        $lineHeaders = true;
                        fputcsv($fh, array_keys($record));
                    }
                    fputcsv($fh, $record);
                }
            }
        }
    } else {
        die("page {$currentPage} can't find DataList1!\n");
    }
}