<%@ Page Language="vb" AutoEventWireup="false" MasterPageFile="~/GVPS.Master" CodeBehind="3DOOSPay_MasterPage.aspx.vb" Inherits="$safeprojectname$._3DOOSPay_MasterPage" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="server">
    <asp:Button ID="submit" runat="server" PostBackUrl="https://sanalposprov.garanti.com.tr/servlet/gt3dengine" Text="Gonder" />
    <div runat="server" id="GVPSTest"></div>
</asp:Content>