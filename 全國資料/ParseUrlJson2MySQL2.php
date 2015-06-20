


<?php

//連接資料庫
$con = mysql_connect("localhost:8888/phpmyadmin","","") or die('Could not connect: ' . mysql_error());
    mysql_select_db("test_db", $con);
    mysql_query("SET NAMES UTF8");

if($con){
	echo("成功連接資料庫");
}else{
	die("資料庫連接失敗...");
}


$url = "http://data.coa.gov.tw/Service/OpenData/AnimalOpenData.aspx";
$content = file_get_contents($url);
$json = json_decode($content);
$ArrayLen = count($json);
echo "ArrayLen=" . $ArrayLen ."<br />";


for($i=0;$i<$ArrayLen;$i++){
	$animal_id = $json[$i]->animal_id;
	$province = $json[$i]->animal_area_pkid;	//需查表轉換
	$shelter_name = $json[$i]->shelter_name;
	$animal_opendate = $json[$i]->animal_opendate;
	$animal_kind = $json[$i]->animal_kind;


	//品種N/A
	// $aniaml_pedigree = $json[$i]->
	$animal_age = $json[$i]->animal_age;
	$animal_sex = $json[$i]->animal_sex;
	$animal_colour = $json[$i]->animal_colour;
	$animal_bodytype = $json[$i]->animal_bodytype;
	//是否有晶片N/A
	//$animal_has_chip
	//晶片N/A
	//$animal_chip 
	$animal_sterilization = $json[$i]->animal_sterilization;
	//入所原因N/A	
	//$animal_entry_reason = 
	//個體情況描述N/A
	//$animal_individual_condition = 
	//入所後醫療照護N/A
	//$animal_medical_care = 
	$animal_status = $json[$i]->animal_status;
	$animal_found_place = $json[$i]->animal_foundplace;	
	// $animal_remark = $json[$i]->animal_remark;
	$animal_remark = strstr($json[$i]->animal_remark,"<a href",true); //有些remark有http連結
	$album_file = $json[$i]->album_file;


	$sql = "INSERT INTO animal_table(id,animal_id, province,shelter_name,animal_opendate,animal_kind,animal_age,animal_sex,animal_colour,animal_bodytype,animal_sterilization,animal_status,animal_found_place,animal_remark,album_file)
    VALUES('','$animal_id', '$province', '$shelter_name', '$animal_opendate', '$animal_kind', '$animal_age', 
    	'$animal_sex', '$animal_colour', '$animal_bodytype', '$animal_sterilization', '$animal_status', '$animal_found_place',
    	'$animal_remark', '$album_file')";
     if(!mysql_query($sql,$con))
    {
        die('Error : ' . mysql_error());
    }		

}


mysql_close($con);



