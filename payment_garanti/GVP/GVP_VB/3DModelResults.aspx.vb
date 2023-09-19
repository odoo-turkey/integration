Imports System
Imports System.Net
Imports System.Xml
Imports System.Security.Cryptography
Imports System.IO

Partial Public Class _3DModelResults
    Inherits System.Web.UI.Page

    Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load

        If Not Page.IsPostBack Then

            Dim strMode As String = Request.Form.Get("mode")
            Dim strApiVersion As String = Request.Form.Get("apiversion")
            Dim strTerminalProvUserID As String = Request.Form.Get("terminalprovuserid")
            Dim strType As String = Request.Form.Get("txntype")
            Dim strAmount As String = Request.Form.Get("txnamount")
            Dim strCurrencyCode As String = Request.Form.Get("txncurrencycode")
            Dim strInstallmentCount As String = Request.Form.Get("txninstallmentcount")
            Dim strTerminalUserID As String = Request.Form.Get("terminaluserid")
            Dim strOrderID As String = Request.Form.Get("oid")
            Dim strCustomeripaddress As String = Request.Form.Get("customeripaddress")
            Dim strcustomeremailaddress As String = Request.Form.Get("customeremailaddress")
            Dim strTerminalID As String = Request.Form.Get("clientid")
            Dim _strTerminalID As String = "0" & strTerminalID
            Dim strTerminalMerchantID As String = Request.Form.Get("terminalmerchantid")
            Dim strStoreKey As String = "xxxxxxxx" 'HASH doğrulaması için 3D Secure şifreniz
            Dim strProvisionPassword As String = "xxxxxxxx" 'HASH doğrulaması için Terminal UserID şifresini tekrar yazıyoruz
            Dim strSuccessURL As String = Request.Form.Get("successurl")
            Dim strErrorURL As String = Request.Form.Get("errorurl")
            Dim strCardholderPresentCode As String = "13" '3D Model işlemde bu değer 13 olmalı
            Dim strMotoInd As String = "N"
            Dim strNumber As String = "" 'Kart bilgilerinin boş gitmesi gerekiyor
            Dim strExpireDate As String = "" 'Kart bilgilerinin boş gitmesi gerekiyor
            Dim strCVV2 As String = "" 'Kart bilgilerinin boş gitmesi gerekiyor
            Dim strAuthenticationCode As String = Server.UrlEncode(Request.Form.Get("cavv"))
            Dim strSecurityLevel As String = Server.UrlEncode(Request.Form.Get("eci"))
            Dim strTxnID As String = Server.UrlEncode(Request.Form.Get("xid"))
            Dim strMD As String = Server.UrlEncode(Request.Form.Get("md"))
            Dim strMDStatus As String = Request.Form.Get("mdstatus")
            Dim strMDStatusText As String = Request.Form.Get("mdErrorMsg")
            Dim strHostAddress As String = "https://sanalposprov.garanti.com.tr/VPServlet" 'Provizyon için xml'in post edileceği adres
            Dim SecurityData As String = UCase(GetSHA1(strProvisionPassword + _strTerminalID))
            Dim HashData As String = UCase(GetSHA1(strOrderID + strTerminalID + strAmount + SecurityData)) 'Daha kısıtlı bilgileri HASH ediyoruz.

            If strMDStatus = 1 Then
                strMDStatusText = "Tam Doğrulama"
            ElseIf strMDStatus = 2 Then
                strMDStatusText = "Kart Sahibi veya bankası sisteme kayıtlı değil"
            ElseIf strMDStatus = 3 Then
                strMDStatusText = "Kartın bankası sisteme kayıtlı değil"
            ElseIf strMDStatus = 4 Then
                strMDStatusText = "Doğrulama denemesi, kart sahibi sisteme daha sonra kayıt olmayı seçmiş"
            ElseIf strMDStatus = 5 Then
                strMDStatusText = "Doğrulama yapılamıyor"
            ElseIf strMDStatus = 6 Then
                strMDStatusText = "3-D Secure Hatası"
            ElseIf strMDStatus = 7 Then
                strMDStatusText = "Sistem Hatası"
            ElseIf strMDStatus = 8 Then
                strMDStatusText = "Bilinmeyen Kart No"
            ElseIf strMDStatus = 0 Then
                strMDStatusText = "Doğrulama Başarısız, 3-D Secure imzası geçersiz."
            End If

            'Hashdata kontrolü için bankadan dönen secure3dhash değeri alınıyor.
            Dim strHashData As String = Request.Form.Get("secure3dhash")
            Dim ValidateHashData As String = UCase(GetSHA1(strTerminalID + strOrderID + strAmount + strSuccessURL + strErrorURL + strType + strInstallmentCount + strStoreKey + SecurityData))

            'İlk gönderilen ve bankadan dönen HASH değeri yeni üretilenle eşleşiyorsa;
            If strHashData = ValidateHashData Then

                lblResult1.Text = "Sayısal Imza Geçerli"

                'Tam Doğrulama, Kart Sahibi veya bankası sisteme kayıtlı değil, Kartın bankası sisteme kayıtlı değil
                'Doğrulama denemesi, kart sahibi sisteme daha sonra kayıt olmayı seçmiş responselarını alan
                'işlemler için Provizyon almaya çalışıyoruz
                If strMDStatus = 1 Or strMDStatus = 2 Or strMDStatus = 3 Or strMDStatus = 4 Then

                    'Provizyona Post edilecek XML Şablonu
                    Dim strXML As String
                    strXML = "<?xml version=""1.0"" encoding=""UTF-8""?>" & _
                             "<GVPSRequest>" & _
                             "<Mode>" & strMode & "</Mode>" & _
                             "<Version>" & strApiVersion & "</Version>" & _
                             "<ChannelCode></ChannelCode>" & _
                             "<Terminal><ProvUserID>" & strTerminalProvUserID & "</ProvUserID><HashData>" & HashData & "</HashData><UserID>" & strTerminalUserID & "</UserID><ID>" & strTerminalID & "</ID><MerchantID>" & strTerminalMerchantID & "</MerchantID></Terminal>" & _
                             "<Customer><IPAddress>" & strCustomeripaddress & "</IPAddress><EmailAddress>" & strcustomeremailaddress & "</EmailAddress></Customer>" & _
                             "<Card><Number></Number><ExpireDate></ExpireDate><CVV2></CVV2></Card>" & _
                             "<Order><OrderID>" & strOrderID & "</OrderID><GroupID></GroupID><AddressList><Address><Type>S</Type><Name></Name><LastName></LastName><Company></Company><Text></Text><District></District><City></City><PostalCode></PostalCode><Country></Country><PhoneNumber></PhoneNumber></Address></AddressList></Order>" & _
                             "<Transaction>" & _
                             "<Type>" & strType & "</Type><InstallmentCnt>" & strInstallmentCount & "</InstallmentCnt><Amount>" & strAmount & "</Amount><CurrencyCode>" & strCurrencyCode & "</CurrencyCode><CardholderPresentCode>" & strCardholderPresentCode & "</CardholderPresentCode><MotoInd>" & strMotoInd & "</MotoInd>" & _
                             "<Secure3D><AuthenticationCode>" & strAuthenticationCode & "</AuthenticationCode><SecurityLevel>" & strSecurityLevel & "</SecurityLevel><TxnID>" & strTxnID & "</TxnID><Md>" & strMD & "</Md></Secure3D>" & _
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

                        '00 ReasonCode döndüğünde işlem başarılıdır. Müşteriye başarılı veya başarısız şeklinde göstermeniz tavsiye edilir. (Fraud riski)
                        If responseFromServer.Contains("<ReasonCode>00</ReasonCode>") Then
                            lblResult2.Text = strMDStatusText
                            lblResult3.Text = "İşlem Başarılı"
                        Else
                            lblResult2.Text = strMDStatusText
                            lblResult3.Text = "İşlem Başarısız"
                        End If

                    Catch ex As Exception
                        lblResult2.Text = strMDStatusText
                        lblResult3.Text = ex.Message
                    End Try

                Else

                    lblResult2.Text = strMDStatusText
                    lblResult3.Text = "İşlem Başarısız"

                End If

            Else
                lblResult1.Text = "Güvenlik Uyarısı. Sayısal Imza Geçerli Degil"
                lblResult2.Text = strMDStatusText
                lblResult3.Text = " İşlem Başarısız"
            End If

            'Dönen değerlerin detayını almak isterseniz alttaki kod bloğunu kullanabilirsiniz.
            'Dim f As IEnumerator = Request.Form.GetEnumerator()
            'While (f.MoveNext())
            '    Dim xkey As String = f.Current.ToString
            '    Dim xval As String = Request.Form.Get(xkey)
            '    lblResult3.Text = lblResult3.Text + (xkey & " : " & xval & vbCrLf)
            'End While

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