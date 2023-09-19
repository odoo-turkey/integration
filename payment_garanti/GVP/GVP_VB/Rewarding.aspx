<%@ Page Language="vb" AutoEventWireup="false" CodeBehind="Rewarding.aspx.vb" Inherits="$safeprojectname$.Rewarding" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" >
<head runat="server">
    <title>REWARDING</title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
        Terminal ID: <asp:TextBox ID="txtTerminalID" runat="server" />
        <br />
        Password: <asp:TextBox ID="txtPassword" runat="server" />
        <br />
        User ID: <asp:TextBox ID="txtUserID" runat="server" />
        <br />
        Merchant ID: <asp:TextBox ID="txtMerchantID" runat="server" />
        <br />
        Number: <asp:TextBox ID="txtCCNumber" runat="server" />
        <br />
        <asp:Button ID="cmdSubmit" runat="server" Text="İşlemi Gönder" />
        <br /><br />
        <asp:TextBox ID="txtResults" TextMode="MultiLine" Width="100%" Height="100" runat="server" />
    </div>
    </form>
</body>
</html>
