<%@ Page Language="vb" AutoEventWireup="false" CodeBehind="SecurityData.aspx.vb" Inherits="$safeprojectname$.SecurityData" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" >
<head runat="server">
    <title>SECURITY DATA</title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
        Terminal ID: <asp:TextBox ID="txtTerminalID" runat="server" />
        <br />
        Password: <asp:TextBox ID="txtPassword" runat="server" />
        <br />
        <asp:Button ID="cmdSubmit" runat="server" Text="Oluştur" />
        <br /><br />
        <asp:Label ID="lblResults" runat="server" />
    </div>
    </form>
</body>
</html>
