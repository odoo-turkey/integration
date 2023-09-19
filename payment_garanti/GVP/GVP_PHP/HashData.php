<html>
<head>
    <title></title>
</head>
<body>
    <?php
        If ($_POST['IsFormSubmitted'] == ""){
        }
        else {
        $strTerminalID = $_POST['txtTerminalID'];
        $strTerminalID_ = "000".$_POST['txtTerminalID'];
        $strProvisionPassword = $_POST['txtPassword'];
        $strOrderID = $_POST['txtOrderID'];
        $strNumber = $_POST['txtCCNumber'];
        $strAmount = $_POST['txtAmount'];
        $strSearch = array('.',',');
        $strReplace = array('',''); 
        $strAmount_ = str_replace($strSearch,$strReplace,$strAmount);
        $SecurityData = strtoupper(sha1($strProvisionPassword.$strTerminalID_));
        $HashData = strtoupper(sha1($strOrderID.$strTerminalID.$strNumber.$strAmount_.$SecurityData));
        
        echo($HashData);
        }
    ?>
    <form action="?" method="post">
        Terminal ID: <input name="txtTerminalID" value="123456" type="text" />
        <br />
        Password: <input name="txtPassword" value="Abq12x46" type="text" />
        <br />
        Order ID: <input name="txtOrderID" value="1" type="text" />
        <br />
        Number: <input name="txtCCNumber" value="4242424242424242" type="text" />
        <br />
        Amount: <input name="txtAmount" value="175,92" type="text" />
        <br />
        <input id="cmdSubmit" type="submit" value="Oluþtur" />
        <input type="hidden" name="IsFormSubmitted" value="submitted" />
    </form>
</body>
</html>