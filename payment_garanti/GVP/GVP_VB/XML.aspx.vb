Imports System
Imports System.Net
Imports System.Xml
Imports System.Security.Cryptography
Imports System.IO

Partial Public Class CCPay
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
        Dim strTerminalID As String = "xxxxxxxx" 'TerminalID yazılmalı.
        Dim _strTerminalID As String = "0" & strTerminalID
        Dim strProvUserID As String = "PROVAUT"
        Dim strProvisionPassword As String = "xxxxxxxx" 'TerminalProvUserID şifresi"
        Dim strUserID As String = "XXXXX"
        Dim strMerchantID As String = "xxxxxxxx" 'Üye İşyeri Numarası
        Dim strIPAddress As String = Request.UserHostAddress 'Kullanıcının IP adresini alır
        Dim strEmailAddress As String = "eticaret@garanti.com.tr"
        Dim strOrderID As String = "DENEME1234"
        Dim strNumber As String = txtCCNumber.Text
        Dim strExpireDate As String = txtExpDate.Text
        Dim strCVV2 As String = txtCVV2.Text
        Dim strAmount As String = "100" 'İşlem Tutarı 1.00 TL için 100 gönderilmelidir. 
        Dim strType As String = "sales"
        Dim strCurrencyCode As String = "949"
        Dim strCardholderPresentCode As String = "0"
        Dim strMotoInd As String = "N"
        Dim strInstallmentCount As String = ""
        Dim strHostAddress As String = "https://sanalposprov.garanti.com.tr/VPServlet"

        Dim SecurityData As String = UCase(GetSHA1(strProvisionPassword + _strTerminalID))
        Dim HashData As String = UCase(GetSHA1(strOrderID + strTerminalID + strNumber + strAmount + SecurityData))

        Dim strXML As String
        strXML = "<?xml version=""1.0"" encoding=""UTF-8""?>" & _
                 "<GVPSRequest>" & _
                 "<Mode>" & strMode & "</Mode>" & _
                 "<Version>" & strVersion & "</Version>" & _
                 "<Terminal><ProvUserID>" & strProvUserID & "</ProvUserID><HashData>" & HashData & "</HashData><UserID>" & strUserID & "</UserID><ID>" & strTerminalID & "</ID><MerchantID>" & strMerchantID & "</MerchantID></Terminal>" & _
                 "<Customer><IPAddress>" & strIPAddress & "</IPAddress><EmailAddress>" & strEmailAddress & "</EmailAddress></Customer>" & _
                 "<Card><Number>" & strNumber & "</Number><ExpireDate>" & strExpireDate & "</ExpireDate><CVV2>" & strCVV2 & "</CVV2></Card>" & _
                 "<Order>" & _
                 "<OrderID>" & strOrderID & "</OrderID>" & _
                 "<GroupID></GroupID>" & _
                 "<AddressList>" & _
                 "<Address>" & _
                 "<Type>S</Type>" & _
                 "<Name></Name>" & _
                 "<LastName></LastName>" & _
                 "<Company></Company>" & _
                 "<Text></Text>" & _
                 "<District></District>" & _
                 "<City></City>" & _
                 "<PostalCode></PostalCode>" & _
                 "<Country></Country>" & _
                 "<PhoneNumber></PhoneNumber>" & _
                 "</Address>" & _
                 "</AddressList>" & _
                 "</Order>" & _
                 "<Transaction>" & _
                 "<Type>" & strType & "</Type><InstallmentCnt>" & strInstallmentCount & "</InstallmentCnt><Amount>" & strAmount & "</Amount><CurrencyCode>" & strCurrencyCode & "</CurrencyCode><CardholderPresentCode>" & strCardholderPresentCode & "</CardholderPresentCode><MotoInd>" & strMotoInd & "</MotoInd>" & _
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

            lblResult0.Text = strXML
            lblResult1.Text = responseFromServer

            'Müşteriye gösterilebilir ama Fraud riski açısından bu değerleri göstermeyelim.
            'Response.Write(responseFromServer)

            'GVPSResponse XML'in değerlerini okuyoruz. İstediğiniz geri dönüş değerlerini gösterebilirsiniz.
            Dim XML As String = responseFromServer
            Dim xDoc As New XmlDocument()
            xDoc.LoadXml(XML)

            'ReasonCode
            Dim xElement1 As XmlElement = TryCast(xDoc.SelectSingleNode("//GVPSResponse/Transaction/Response/ReasonCode"), XmlElement)
            'Message
            'Dim xElement2 As XmlElement = TryCast(xDoc.SelectSingleNode("//GVPSResponse/Transaction/Response/Message"), XmlElement)

            'ErrorMsg
            Dim xElement3 As XmlElement = TryCast(xDoc.SelectSingleNode("//GVPSResponse/Transaction/Response/ErrorMsg"), XmlElement)
            lblResult2.Text = xElement3.InnerText

            '00 ReasonCode döndüğünde işlem başarılıdır. Müşteriye başarılı veya başarısız şeklinde göstermeniz tavsiye edilir. (Fraud riski)
            If xElement1.InnerText = "00" Then
                lblResult3.Text = "İşlem Başarılı"
            Else
                lblResult3.Text = "İşlem Başarısız"
            End If

        Catch ex As Exception
            lblResult3.Text = ex.Message
        End Try

    End Sub

End Class