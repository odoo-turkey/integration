<html>
<head>
    <title></title>
</head>
<body>
<?php
    $strMDStatus = $_POST["mdstatus"];

    if($strMDStatus == "1"){
    echo "Tam Doðrulama";
    }if($strMDStatus == "2"){
    echo "Kart Sahibi veya bankasý sisteme kayýtlý deðil";
    }if($strMDStatus == "3"){
    echo "Kartýn bankasý sisteme kayýtlý deðil";
    }if($strMDStatus == "4"){
    echo "Doðrulama denemesi, kart sahibi sisteme daha sonra kayýt olmayý seçmiþ";
    }if($strMDStatus == "5"){
    echo "Doðrulama yapýlamýyor";
    }if($strMDStatus == "7"){
    echo "Sistem Hatasý";
    }if($strMDStatus == "8"){
    echo "Bilinmeyen Kart No";
    }if($strMDStatus == "0"){
    echo "Doðrulama Baþarýsýz, 3-D Secure imzasý geçersiz.";
    }
    
    //Tam Doðrulama, Kart Sahibi veya bankasý sisteme kayýtlý deðil, Kartýn bankasý sisteme kayýtlý deðil
    //Doðrulama denemesi, kart sahibi sisteme daha sonra kayýt olmayý seçmiþ responselarýný alan
    //iþlemler için Provizyon almaya çalýþýyoruz
    if ($strMDStatus == "1" || $strMDStatus == "2" || $strMDStatus == "3" || $strMDStatus == "4") 
    {
        $strMode = $_POST['mode'];
        $strVersion = $_POST['apiversion'];
        $strTerminalID = $_POST['clientid'];
        $strTerminalID_ = "0".$_POST['clientid'];
        $strProvisionPassword = "s2LaPfe3"; //Terminal UserID þifresi
        $strProvUserID = $_POST['terminalprovuserid'];
        $strUserID = $_POST['terminaluserid'];
        $strMerchantID = $_POST['terminalmerchantid'];
        $strIPAddress = $_POST['customeripaddress'];
        $strEmailAddress = $_POST['customeremailaddress'];
        $strOrderID = $_POST['orderid'];
        $strNumber = ""; //Kart bilgilerinin boþ gitmesi gerekiyor
        $strExpireDate = ""; //Kart bilgilerinin boþ gitmesi gerekiyor
        $strCVV2 = ""; //Kart bilgilerinin boþ gitmesi gerekiyor
        $strAmount = $_POST['txnamount'];
        $strCurrencyCode = $_POST['txncurrencycode'];
        $strInstallmentCount = $_POST['txninstallmentcount'];
        $strCardholderPresentCode = "13"; //3D Model iþlemde bu deðer 13 olmalý
        $strType = $_POST['txntype'];
        $strMotoInd = "N";
        $strAuthenticationCode = $_POST['cavv'];
        $strSecurityLevel = $_POST['eci'];
        $strTxnID = $_POST['xid'];
        $strMD = $_POST['md'];
        $SecurityData = strtoupper(sha1($strProvisionPassword.$strTerminalID_));
        $HashData = strtoupper(sha1($strOrderID.$strTerminalID.$strAmount.$SecurityData)); //Daha kýsýtlý bilgileri HASH ediyoruz.
        $strHostAddress = "https://sanalposprov.garanti.com.tr/VPServlet"; //Provizyon için xml'in post edileceði adres

        //Provizyona Post edilecek XML Þablonu
        $strXML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
                    <GVPSRequest>
                    <Mode>$strMode</Mode>
                    <Version>$strVersion</Version>
                    <ChannelCode></ChannelCode>
                    <Terminal><ProvUserID>$strProvUserID</ProvUserID><HashData>$HashData</HashData><UserID>$strUserID</UserID><ID>$strTerminalID</ID><MerchantID>$strMerchantID</MerchantID></Terminal>
                    <Customer><IPAddress>$strIPAddress</IPAddress><EmailAddress>$strEmailAddress</EmailAddress></Customer>
                    <Card><Number></Number><ExpireDate></ExpireDate><CVV2></CVV2></Card>
                    <Order><OrderID>$strOrderID</OrderID><GroupID></GroupID><AddressList><Address><Type>B</Type><Name></Name><LastName></LastName><Company></Company><Text></Text><District></District><City></City><PostalCode></PostalCode><Country></Country><PhoneNumber></PhoneNumber></Address></AddressList></Order><Transaction><Type>$strType</Type><InstallmentCnt>$strInstallmentCount</InstallmentCnt><Amount>$strAmount</Amount><CurrencyCode>$strCurrencyCode</CurrencyCode><CardholderPresentCode>$strCardholderPresentCode</CardholderPresentCode><MotoInd>$strMotoInd</MotoInd><Secure3D><AuthenticationCode>$strAuthenticationCode</AuthenticationCode><SecurityLevel>$strSecurityLevel</SecurityLevel><TxnID>$strTxnID</TxnID><Md>$strMD</Md></Secure3D>
                    </Transaction>
                    </GVPSRequest>";

        $ch=curl_init();
        curl_setopt($ch, CURLOPT_URL, $strHostAddress);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_POST, 1) ;
        curl_setopt($ch, CURLOPT_POSTFIELDS, "data=".$strXML);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        $results = curl_exec($ch);
        curl_close($ch);

        echo "<b>Giden Ýstek </b><br />";
        echo $strXML;
        echo "<br /><b>Gelen Yanýt </b><br />";
        echo $results;
    }

	foreach($_POST as $key => $value)
	{
	    echo "<br>".$key." : ".$value;
	}
?>
</body>
</html>