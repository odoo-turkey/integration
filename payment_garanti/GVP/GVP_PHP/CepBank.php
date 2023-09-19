<html>
<head>
    <title>CepBank</title>
</head>
<body>
    <?php
        $strMode = "PROD";
        $strVersion = "v0.01";
        $strTerminalID = "XXXXXXXXX";
        $strTerminalID_ = "0XXXXXXXX"; //Baþýna 0 eklenerek 9 digite tamamlanmalýdýr.
        $strProvUserID = "PROVAUT";
        $strProvisionPassword = "XXXXXXXX"; //Terminal UserID þifresi
        $strUserID = "XXXXXX";
        $strMerchantID = "XXXXXXXX"; //Üye Ýþyeri Numarasý
        $strCustomerName = "Yahya EKÝNCÝ";
        $strIPAddress = "192.168.1.1";
        $strEmailAddress = "eticaret@garanti.com.tr";
        $strOrderID = "Deneme";
        $strInstallmentCnt = ""; //Taksit Sayýsý. Boþ gönderilirse taksit yapýlmaz
        $strGSMNumber = $_POST['txtGSMNumber'];
        $strPaymentType = $_POST['ddlPaymentType'];
        $strAmount = "100"; //Ýþlem Tutarý
        $strType = "cepbank";
        $strCurrencyCode = "949";
        $strCardholderPresentCode = "0";
        $strMotoInd = "N";
        $strHostAddress = "https://sanalposprov.garanti.com.tr/VPServlet";
        $SecurityData = strtoupper(sha1($strProvisionPassword.$strTerminalID_));
        $HashData = strtoupper(sha1($strOrderID.$strTerminalID.$strNumber.$strAmount.$SecurityData));
        $xml= "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
        <GVPSRequest>
        <Mode>$strMode</Mode><Version>$strVersion</Version>
        <Terminal><ProvUserID>$strProvUserID</ProvUserID><HashData>$HashData</HashData><UserID>$strUserID</UserID><ID>$strTerminalID</ID><MerchantID>$strMerchantID</MerchantID></Terminal>
        <Customer><IPAddress>$strIPAddress</IPAddress><EmailAddress>$strEmailAddress</EmailAddress></Customer>
        <Card><Number></Number><ExpireDate></ExpireDate><CVV2></CVV2></Card>
        <Order><OrderID>$strOrderID</OrderID><GroupID></GroupID></Order>
        <Transaction>
        <Type>$strType</Type><InstallmentCnt>$strInstallmentCnt</InstallmentCnt><Amount>$strAmount</Amount><CurrencyCode>$strCurrencyCode</CurrencyCode><CardholderPresentCode>$strCardholderPresentCode</CardholderPresentCode><MotoInd>$strMotoInd</MotoInd><Description></Description><OriginalRetrefNum></OriginalRetrefNum>
        <CepBank><GSMNumber>$strGSMNumber</GSMNumber><PaymentType>$strPaymentType</PaymentType></CepBank>
        </Transaction>
        </GVPSRequest>";
    
        If ($_POST['IsFormSubmitted'] == ""){
        }
        else {
        
        $ch=curl_init();
        curl_setopt($ch, CURLOPT_URL, $strHostAddress);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_POST, 1) ;
        curl_setopt($ch, CURLOPT_POSTFIELDS, "data=".$xml);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        $results = curl_exec($ch);
        curl_close($ch);

        echo "<b>Giden Ýstek </b><br />";
        echo $xml;
        echo "<br /><b>Gelen Yanýt </b><br />";
        echo $results;
        }
    ?>
    <form action="?" method="post">
        GSM Number: <input name="txtGSMNumber" type="text" />
        <br />
        Payment Type :
        <select name="ddlPaymentType">
            <option value="K">Kredi Kartý</option>
            <option value="D">Debit Kart</option>
            <option value="V">Vadesiz Hesap</option>
        </select>
        <br />
        <input type="hidden" name="IsFormSubmitted" value="submitted" />
        <input id="submit" type="submit" value="Gönder" />
    </form>
</body>
</html>