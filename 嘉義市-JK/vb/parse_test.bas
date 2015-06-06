For i = 1 To 7
With ActiveWorkbook.QueryTables.Add("URL;http://www.dog.dias.com.tw/index.php?op=announcement&page=" & i, Destination:=Range("A1"))
        .WebFormatting = xlWebFormattingNone
        .TablesOnlyFromHTML = False
        .RefreshStyle = xlOverwriteCells
        .SaveData = True
        .Refresh 0

End With
Dim k As Integer
k = 2
For j = 0 To 4
工作表2.Cells(k + (i - 1) * 5, 1).Value = Right(ActiveWorkbook.Cells(6 + (k - 2) + (j * 7), 1).Value, 10) '時間'
工作表2.Cells(k + (i - 1) * 5, 2).Value = Right(ActiveWorkbook.Cells(8 + (k - 2) + (j * 7), 1).Value, 1) '犬貓'
工作表2.Cells(k + (i - 1) * 5, 3).Value = Mid(ActiveWorkbook.Cells(8 + (k - 2) + (j * 7), 1).Value, 4, 3) '品種'
工作表2.Cells(k + (i - 1) * 5, 5).Value = Right(ActiveWorkbook.Cells(9 + (k - 2) + (j * 7), 1).Value, 1) '性別'
工作表2.Cells(k + (i - 1) * 5, 6).Value = Right(ActiveWorkbook.Cells(10 + (k - 2) + (j * 7), 1).Value, 2) '體型's
工作表2.Cells(k + (i - 1) * 5, 13).Value = ActiveWorkbook.Cells(11 + (k - 2) + (j * 7), 1).Value & ";" & ActiveWorkbook.Cells(12 + (k - 2) + (j * 7), 1).Value '來源&備註'
k = k + 1
Next
Next
