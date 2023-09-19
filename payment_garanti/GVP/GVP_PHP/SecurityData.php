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
        $SecurityData = strtoupper(sha1($strProvisionPassword.$strTerminalID_));
        
        echo($SecurityData);
        }
    ?>
    <form action="?" method="post">
        Terminal ID: <input name="txtTerminalID" value="123456" type="text" />
        <br />
        Password: <input name="txtPassword" value="Abq12x46" type="text" />
        <br />
        <input id="cmdSubmit" type="submit" value="Oluþtur" />
        <input type="hidden" name="IsFormSubmitted" value="submitted" />
    </form>
</body>
</html>