<html>
<head>
    <title></title>
</head>
<body>
    <?php
        $strMode = "PROD";
        $strApiVersion = "v0.01";
        $strTerminalProvUserID = "PROVOOS";
        $strType = "sales";
        $strAmount = "100"; //Ýþlem Tutarý 1.00 TL için 100 girilmelidir. 
        $strCurrencyCode = "949";
        $strInstallmentCount = ""; //Taksit Sayýsý. Boþ gönderilirse taksit yapýlmaz
        $strTerminalUserID = "XXXXXX";
        $strOrderID = "DENEME";  //her iþlemde farklý bir deðer gönderilmeli
        $strcompanyname = "TradeSiS";
        $strcustomeremailaddress = "eticaret@garanti.com.tr";
        $strCustomeripaddress = "127.0.0.1";
        $strTerminalID = "XXXXXXXX";
        $strTerminalID_ = "0XXXXXXXX"; //Baþýna 0 eklenerek 9 digite tamamlanmalýdýr.
        $strTerminalMerchantID = "XXXXXX"; //Üye Ýþyeri Numarasý
        $strStoreKey = "XXXXXX"; //3D Secure þifreniz
        $strProvisionPassword = "XXXXXX"; //TerminalProvUserID þifresi
        $strSuccessURL = "https://<sunucu_adresi>/Gate3DEngineCallBack.php";
        $strErrorURL = "https://<sunucu_adresi>/Gate3DEngineCallBack.php";
        $strtimestamp = "XXXXXX"; //Random ve Unique bir deðer olmalý
        $strLang = "tr";
        $SecurityData = strtoupper(sha1($strProvisionPassword.$strTerminalID_));
        $HashData = strtoupper(sha1($strTerminalID.$strOrderID.$strAmount.$strSuccessURL.$strErrorURL.$strType.$strInstallmentCount.$strStoreKey.$SecurityData));
    ?>
    <form action="https://sanalposprov.garanti.com.tr/servlet/gt3dengine" method="post">
        3D Security Level: 
        <select name="secure3dsecuritylevel">
            <option value="OOS_PAY">OOS_PAY</option>
        </select>
        <br />
        Refresh Time: <input name="refreshtime" type="text" />
        <br />
        <input id="submit" type="submit" value="Ýþlemi Gönder" />
        <input type="hidden" name="mode" value="<?php echo $strMode ?>" />
        <input type="hidden" name="apiversion" value="<?php echo $strApiVersion ?>" />
        <input type="hidden" name="terminalprovuserid" value="<?php echo $strTerminalProvUserID ?>" />
        <input type="hidden" name="terminaluserid" value="<?php echo $strTerminalUserID ?>" />
        <input type="hidden" name="terminalid" value="<?php echo $strTerminalID ?>" />
        <input type="hidden" name="terminalmerchantid" value="<?php echo $strTerminalMerchantID ?>" />
        <input type="hidden" name="orderid" value="<?php echo $strOrderID ?>" />
        <input type="hidden" name="customeremailaddress" value="<?php echo $strcustomeremailaddress ?>" />
        <input type="hidden" name="customeripaddress" value="<?php echo $strCustomeripaddress ?>" />
        <input type="hidden" name="txntype" value="<?php echo $strType ?>" />
        <input type="hidden" name="txnamount" value="<?php echo $strAmount ?>" />
        <input type="hidden" name="txncurrencycode" value="<?php echo $strCurrencyCode ?>" />
        <input type="hidden" name="companyname" value="<?php echo $strcompanyname ?>" />
        <input type="hidden" name="txninstallmentcount" value="<?php echo $strInstallmentCount ?>" />
        <input type="hidden" name="successurl" value="<?php echo $strSuccessURL ?>" />
        <input type="hidden" name="errorurl" value="<?php echo $strErrorURL ?>" />
        <input type="hidden" name="secure3dhash" value="<?php echo $HashData ?>" />
        <input type="hidden" name="lang" value="<?php echo $strLang ?>" />
        <input type="hidden" name="txntimestamp" value="<?php echo $strtimestamp ?>" />
        <!---
        'Sipariþe yönelik Fatura bilgilerini göndermek için ekteki opsiyonel alanlar kullanýlabilir.
        'Eðer birden çok Fatura detayý gönderilecekse orderaddresscount=2 yapýlarak
        'Tüm element isimlerindeki 1 rakamý 2 yapýlmalýdýr. Örn; orderaddresscity2 gibi...
        <input type="hidden" name="orderaddresscount" value="1" />
        <input type="hidden" name="orderaddresscity1" value="xxx" />
        <input type="hidden" name="orderaddresscompany1" value="xxx" />
        <input type="hidden" name="orderaddresscountry1" value="xxx" />
        <input type="hidden" name="orderaddressdistrict1" value="xxx" />
        <input type="hidden" name="orderaddressfaxnumber1" value="xxx" />
        <input type="hidden" name="orderaddressgsmnumber1" value="xxx" />
        <input type="hidden" name="orderaddresslastname1" value="xxx" />
        <input type="hidden" name="orderaddressname1" value="xxx" />
        <input type="hidden" name="orderaddressphonenumber1" value="xxx" />
        <input type="hidden" name="orderaddresspostalcode1" value="xxx" />
        <input type="hidden" name="orderaddresstext1" value="xxx" />
        <input type="hidden" name="orderaddresstype1" value="xxx" />
        --->
    </form>
</body>
</html>