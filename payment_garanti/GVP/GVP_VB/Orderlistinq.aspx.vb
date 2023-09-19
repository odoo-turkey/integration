Imports System
Imports System.Net
Imports System.Xml
Imports System.Security.Cryptography
Imports System.IO

Partial Public Class Orderlistinq
    Inherits System.Web.UI.Page

    Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
        If Not Page.IsPostBack Then
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


    Protected Sub cmdSubmit_Click(ByVal sender As Object, ByVal e As EventArgs) Handles cmdSubmit.Click

        Dim strMode As String = "PROD"
        Dim strVersion As String = "v0.01"
        Dim strTerminalID As String = "XXXXXXXX" '8 Haneli TerminalID yazılmalı.
        Dim _strTerminalID As String = "0" & strTerminalID
        Dim strProvUserID As String = "PROVAUT"
        Dim strProvisionPassword As String = "XXXXXXXX" 'Terminal UserID şifresi"
        Dim strUserID As String = "XXXXX"
        Dim strMerchantID As String = "XXXXXX" 'Üye İşyeri Numarası
        Dim strIPAddress As String = Request.UserHostAddress 'Kullanıcının IP adresini alır
        Dim strStartDate As String = txtStartDate.Text
        Dim strEndDate As String = txtEndDate.Text
        Dim strAmount As String = "1"
        Dim strType As String = "orderlistinq"
        Dim strCurrencyCode As String = "949"
        Dim strCardholderPresentCode As String = "0"
        Dim strMotoInd As String = "N"
        Dim strHostAddress As String = "https://sanalposprov.garanti.com.tr/VPServlet"

        Dim SecurityData As String = UCase(GetSHA1(strProvisionPassword + _strTerminalID))
        Dim HashData As String = UCase(GetSHA1(strTerminalID + strAmount + SecurityData))

        Dim strXML As String
        strXML = "<?xml version=""1.0"" encoding=""UTF-8""?>" & _
                 "<GVPSRequest>" & _
                 "<Mode>" & strMode & "</Mode>" & _
                 "<Version>" & strVersion & "</Version>" & _
                 "<Terminal><ProvUserID>" & strProvUserID & "</ProvUserID><HashData>" & HashData & "</HashData><UserID>" & strUserID & "</UserID><ID>" & strTerminalID & "</ID><MerchantID>" & strMerchantID & "</MerchantID></Terminal>" & _
                 "<Customer><IPAddress>" & strIPAddress & "</IPAddress><EmailAddress></EmailAddress></Customer>" & _
                 "<Card><Number></Number><ExpireDate></ExpireDate><CVV2></CVV2></Card>" & _
                 "<Order>" & _
                 "<OrderID></OrderID>" & _
                 "<GroupID></GroupID>" & _
                 "<StartDate>" & strStartDate & "</StartDate>" & _
                 "<EndDate>" & strEndDate & "</EndDate>" & _
                 "</Order>" & _
                 "<Transaction>" & _
                 "<Type>" & strType & "</Type><InstallmentCnt></InstallmentCnt><Amount>" & strAmount & "</Amount><CurrencyCode>" & strCurrencyCode & "</CurrencyCode><CardholderPresentCode>" & strCardholderPresentCode & "</CardholderPresentCode><MotoInd>" & strMotoInd & "</MotoInd>" & _
                 "</Transaction>" & _
                 "</GVPSRequest>"
        Try

            Dim data As String = "data=" + strXML

            Dim _WebRequest As WebRequest = WebRequest.Create(strHostAddress)
            _WebRequest.Method = "POST"

            Dim byteArray As Byte() = Encoding.UTF8.GetBytes(data)
            _WebRequest.ContentType = "application/x-www-form-urlencoded"
            _WebRequest.ContentLength = byteArray.Length

            Dim dataStream As Stream = _WebRequest.GetRequestStream()
            dataStream.Write(byteArray, 0, byteArray.Length)
            dataStream.Close()

            Dim _WebResponse As WebResponse = _WebRequest.GetResponse()
            Console.WriteLine(CType(_WebResponse, HttpWebResponse).StatusDescription)
            dataStream = _WebResponse.GetResponseStream()

            Dim reader As New StreamReader(dataStream)
            Dim responseFromServer As String = reader.ReadToEnd()

            Console.WriteLine(responseFromServer)

            lblResult1.Text = responseFromServer

        Catch ex As Exception
            lblResult1.Text = ex.Message
        End Try

    End Sub

End Class