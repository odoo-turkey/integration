<%@ Page Language="C#" AutoEventWireup="true" CodeBehind="CCPay.aspx.cs" Inherits="$safeprojectname$.CCPay" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" >
<head id="Head1" runat="server">
    <title>CC PAY</title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
        Number: <asp:TextBox ID="txtCCNumber" runat="server" />
        <br />
        Expire Date: <asp:TextBox ID="txtExpDate" runat="server" />
        <br />
        CVV2: <asp:TextBox ID="txtCVV2" runat="server" />
        <br />
        <asp:Button ID="cmdSubmit" runat="server" Text="İşlemi Gönder" onclick="cmdSubmit_Click" />
        <br /><br />
        <asp:Label ID="lblResult1" runat="server" />
        <br />
        <asp:Label ID="lblResult2" runat="server" />
        <br />
        <asp:Label ID="lblResult3" runat="server" />
    </div>
    </form>
</body>
</html>