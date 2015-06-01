
<?php
require_once 'reader.php'; 
header('Content-Type:text/html;charset=utf-8');
error_reporting(E_ALL);
// 資料存入資料庫需用到
	// define('DB_HOST','localhost');
	// define('DB_USER','root');
	// define('DB_PWD','123456');
	// define('DB_NAME','mydata');
// 連接 mysql
	// $conn = mysql_connect(DB_HOST,DB_USER,DB_PWD) or die('mysql connected error cause: '.mysql_error());
	// // 設置字符集
	// mysql_select_db(DB_NAME) or die('db selected error cause: '.mysql_error());
	// mysql_query('SET NAMES UTF8') or die('set names error cause: '.mysql_error());
// 創建一個讀取 excel 表單的實例
$excelobj = new Spreadsheet_Excel_Reader();
$excelobj->setOutputEncoding('UTF-8');
// 載入要讀取的檔案
$excelobj->read('1040529.xls');  

$fpw=fopen("1040529.csv","w");
//2. 這是 csv 的標頭欄位
$top_body = "區域編碼,所在地,動物類型(狗/貓/[其他-自行定義]),動物性別(公/母/未知),動物體型(迷你型/小型/中型/大型),動物毛色,動物年紀(幼年/成年),是否有節紮(是/否),尋獲地點或來源,";
//fputs($fpw,$top_body."\r\n");
fputs($fpw,mb_convert_encoding($top_body,"Big5","UTF-8")."\r\n"); //這是要轉成UTF-8編碼的語法/

// 依序讀出表單內容
for ($i = 1; $i <= $excelobj->sheets[0]['numRows']; $i++) {
	 
     for ($j = 1; $j <= $excelobj->sheets[0]['numCols']; $j++) {
		  // excel 表裡的第 i 列(row), 第 j 行(column)
          $celldata = $excelobj->sheets[0]['cells'][$i][$j];
		  // 判斷內容為空
		  // if ($celldata == "")		// 跳到下一列
				// $j = $excelobj->sheets[0]['numCols'];
		  // else
		  // {		// 取出內容後看是要顯示在螢幕還是放進 資料庫

				// 直接螢幕列出結果
				//echo "row=".$i.",col=".$j.",data=".$celldata;   // display on screen
				mb_convert_encoding($v[j],"UTF-8","Big5");	
				$v[$j] = $celldata;	
				// 插入資料庫
					// $query = "INSERT INTO MYDB (db-field) values ('".$celldata;
					// $result = @mysql_query($query)or die('select data failed cause: '.mysql_error());
				if($j==$excelobj->sheets[0]['numCols'] && $i>2){
					$vv="$v[1],$v[2],$v[3],$v[4],$v[5],$v[6],$v[7],$v[8],$v[9],$v[10]";
					//fputs($fpw,$vv."\r\n");
					fputs($fpw,mb_convert_encoding($vv,"Big5","UTF-8")."\r\n"); //這是要轉成UTF-8編碼的語法
				}
     }
	 

}
fclose($fpw);


?>

