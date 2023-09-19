<%@ Page Language="vb" AutoEventWireup="false" CodeBehind="CepBank.aspx.vb" Inherits="$safeprojectname$.CepBank" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" >
<head id="Head1" runat="server">
    <title>CEPBANK</title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
        GSM Number: <asp:TextBox ID="txtGSMNumber" runat="server" />
        <br />
        Payment Type :
        <asp:DropDownList ID="ddlPaymentType" runat="server">
            <asp:ListItem Value="K" Text="Kredi Kartı" />
            <asp:ListItem Value="D" Text="Debit Kart" />
            <asp:ListItem Value="V" Text="Vadesiz Hesap" />
        </asp:DropDownList>
        <br />
        <asp:Button ID="cmdSubmit" runat="server" Text="Gonder" />
        <br /><br />
        <asp:TextBox ID="txtResults1" TextMode="MultiLine" Width="100%" Height="100" runat="server" />
        <br /><br />
        <asp:TextBox ID="txtResults2" TextMode="MultiLine" Width="100%" Height="100" runat="server" />
    </div>
    </form>
</body>
</html>
