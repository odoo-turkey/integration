<%@ Page Language="vb" AutoEventWireup="false" CodeBehind="OOSPay.aspx.vb" Inherits="$safeprojectname$.OOSPay" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" >
<head runat="server">
    <title>OOS PAY</title>
</head>
<body>
    <form id="form1" runat="server">
    <div>
        <asp:Button ID="submit" runat="server" PostBackUrl="https://sanalposprov.garanti.com.tr/servlet/gt3dengine" Text="Gonder" />
        <asp:HiddenField ID="mode" runat="server" />
        <asp:HiddenField ID="secure3dsecuritylevel" Value="OOS_PAY" runat="server" />
        <asp:HiddenField ID="apiversion" runat="server" />
        <asp:HiddenField ID="terminalprovuserid" runat="server" />
        <asp:HiddenField ID="terminaluserid" runat="server" />
        <asp:HiddenField ID="terminalid" runat="server" />
        <asp:HiddenField ID="terminalmerchantid" runat="server" />
        <asp:HiddenField ID="orderid" runat="server" />
        <asp:HiddenField ID="customeremailaddress" runat="server" />
        <asp:HiddenField ID="customeripaddress" runat="server" />
        <asp:HiddenField ID="txntype" runat="server" />
        <asp:HiddenField ID="txnamount" runat="server" />
        <asp:HiddenField ID="txncurrencycode" runat="server" />
        <asp:HiddenField ID="companyname" runat="server" />
        <asp:HiddenField ID="txninstallmentcount" runat="server" />
        <asp:HiddenField ID="successurl" runat="server" />
        <asp:HiddenField ID="errorurl" runat="server" />
        <asp:HiddenField ID="secure3dhash" runat="server" />
        <asp:HiddenField ID="lang" runat="server" />
        <asp:HiddenField ID="txntimestamp" runat="server" />
        <asp:HiddenField ID="refreshtime" runat="server" />
    </div>
    </form>
</body>
</html>
