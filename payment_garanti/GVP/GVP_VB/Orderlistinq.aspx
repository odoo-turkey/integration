<%@ Page Language="vb" AutoEventWireup="false" CodeBehind="Orderlistinq.aspx.vb" Inherits="$safeprojectname$.Orderlistinq" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" >
<head runat="server">
    <title>Sipariş Listesi (Tarih Bazında)</title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
        Start Date: <asp:TextBox ID="txtStartDate" Text="01/01/2011 00:00" runat="server" />
        <br />
        End Date: <asp:TextBox ID="txtEndDate" Text="01/02/2011 23:59" runat="server" />
        <br />
        <asp:Button ID="cmdSubmit" runat="server" Text="Sorgula" />
        <br /><br />
        <asp:Label ID="lblResult1" runat="server" />
    </div>
    </form>
</body>
</html>
