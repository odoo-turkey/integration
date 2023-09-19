Imports System
Imports System.Net
Imports System.Xml
Imports System.Security.Cryptography
Imports System.IO

Partial Public Class _3DOOSPay_MasterPage
    Inherits System.Web.UI.Page

    Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load

        If Not Page.IsPostBack Then

            Dim strMode As String = "PROD"
            Dim strApiVersion As String = "v0.01"
            Dim strsecure3dsecuritylevel As String = "3D_OOS_FULL" '3D_OOS_PAY - 3D_OOS_HALF
            Dim strTerminalProvUserID As String = "PROVOOS" 'Ortak ödeme sayfasý kullanýcýsý
            Dim strType As String = "sales"
            Dim strAmount As String = "100" 'Ýþlem Tutarý 1.00 TL için 100 gönderilmeli
            Dim strCurrencyCode As String = "949"
            Dim strInstallmentCount As String = "" 'Taksit Sayýsý. Boþ gönderilirse taksit yapýlmaz
            Dim strTerminalUserID As String = ""
            Dim strOrderID As String = "DENEME" 'her iþlemde farklý bir deðer gönderilmeli
            Dim strCustomeripaddress As String = Request.UserHostAddress 'Kullanýcýnýn IP adresini alýr
            Dim strcustomerEmailAddress As String = "eticaret@garanti.com.tr"
            Dim strTerminalID As String = "XXXXXXXX" '8 Haneli TerminalID yazýlmalý.
            Dim _strTerminalID As String = "0" & strTerminalID
            Dim strTerminalMerchantID As String = "XXXXXXXX" 'Üye Ýþyeri Numarasý
            Dim strStoreKey As String = "XXXXXXXX" '3D Secure þifreniz
            Dim strProvisionPassword As String = "XXXXXXXX" 'PROVOOS Terminal UserID þifresi
            Dim strSuccessURL As String = "http://<sunucu_adresi>/3DOOSPayResults.aspx"
            Dim strErrorURL As String = "http://<sunucu_adresi>/3DOOSPayResults.aspx"
            Dim strCompanyName As String = "TEST MAGAZASI"
            Dim strlang As String = "tr"
            Dim strRefreshTime As String = "10"
            Dim strtimestamp As String = Date.Now 'Random ve Unique bir deðer olmalý

            Dim SecurityData As String = UCase(GetSHA1(strProvisionPassword + _strTerminalID))
            Dim HashData As String = UCase(GetSHA1(strTerminalID + strOrderID + strAmount + strSuccessURL + strErrorURL + strType + strInstallmentCount + strStoreKey + SecurityData))

            Dim strHiddenHTML

            strHiddenHTML = "<input type=""hidden"" name=""secure3dsecuritylevel"" id=""secure3dsecuritylevel"" value=""" & strsecure3dsecuritylevel & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""mode"" id=""mode"" value=""" & strMode & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""apiversion"" id=""apiversion"" value=""" & strApiVersion & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""terminalprovuserid"" id=""terminalprovuserid"" value=""" & strTerminalProvUserID & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""txntype"" id=""txntype"" value=""" & strType & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""txnamount"" id=""txnamount"" value=""" & strAmount & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""txncurrencycode"" id=""txncurrencycode"" value=""" & strCurrencyCode & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""txninstallmentcount"" id=""txninstallmentcount"" value=""" & strInstallmentCount & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""terminaluserid"" id=""terminaluserid"" value=""" & strTerminalUserID & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""orderid"" id=""orderid"" value=""" & strOrderID & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""customeripaddress"" id=""customeripaddress"" value=""" & strCustomeripaddress & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""customeremailaddress"" id=""customeremailaddress"" value=""" & strcustomerEmailAddress & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""terminalid"" id=""terminalid"" value=""" & strTerminalID & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""terminalmerchantid"" id=""terminalmerchantid"" value=""" & strTerminalMerchantID & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""storekey"" id=""storekey"" value=""" & strStoreKey & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""provisionpassword"" id=""provisionpassword"" value=""" & strProvisionPassword & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""successurl"" id=""successurl"" value=""" & strSuccessURL & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""errorurl"" id=""errorurl"" value=""" & strErrorURL & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""companyname"" id=""companyname"" value=""" & strCompanyName & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""lang"" id=""lang"" value=""" & strlang & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""refreshtime"" id=""refreshtime"" value=""" & strRefreshTime & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""txntimestamp"" id=""txntimestamp"" value=""" & strtimestamp & """ />"
            strHiddenHTML = strHiddenHTML & "<input type=""hidden"" name=""secure3dhash"" id=""secure3dhash"" value=""" & HashData & """ />"

            GVPSTest.InnerHtml = strHiddenHTML

        End If

    End Sub

    Public Function GetSHA1(ByVal SHA1Data As String) As String

        Dim sha As SHA1 = New SHA1CryptoServiceProvider()
        Dim HashedPassword As String = SHA1Data
        Dim hashbytes As Byte() = Encoding.GetEncoding("ISO-8859-9").GetBytes(HashedPassword)
        Dim inputbytes As Byte() = sha.ComputeHash(hashbytes)
        Return GetHexaDecimal(inputbytes)

    End Function

    Public Shared Function GetHexaDecimal(ByVal bytes As Byte()) As String

        Dim s As New StringBuilder()
        Dim length As Integer = bytes.Length
        For n As Integer = 0 To length - 1
            s.Append([String].Format("{0,2:x}", bytes(n)).Replace(" ", "0"))
        Next
        Return s.ToString()

    End Function

End Class