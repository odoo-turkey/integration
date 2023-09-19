Imports System
Imports System.Net
Imports System.Xml
Imports System.Security.Cryptography
Imports System.IO

Partial Public Class CepBank_Void
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
        Dim strProvUserID As String = "PROVRFN" 'İptal / İade kullanıcısı
        Dim strProvisionPassword As String = "XXXXXX" 'PROVRFN (İptal / İade kullanıcısı) şifresi
        Dim strUserID As String = "XXXXXX"
        Dim strMerchantID As String = "XXXXXX" 'Üye İşyeri Numarası
        Dim strCustomerName As String = "Yahya EKİNCİ"
        Dim strIPAddress As String = Request.UserHostAddress 'Kullanıcının IP adresini alır
        Dim strEmailAddress As String = "eticaret@garanti.com.tr"
        Dim strOrderID As String = "deneme1" 'Satış işleminin gerçekleştiği OrderID gönderilmeli.
        Dim strGSMNumber As String = txtGSMNumber.Text
        Dim strAmount As String = "100" 'Satış işleminin gerçekleştiği gerçek tutar gönderilmeli.
        Dim strType As String = "cepbankvoid" 'CepBank sorgulama işlemleri için bu type kullanılmalı
        Dim strCurrencyCode As String = "949"
        Dim strCardholderPresentCode As String = "0"
        Dim strMotoInd As String = "N"
        Dim strInstallmentCount As String = "" 'Taksit Sayısı. Boş gönderilirse taksit yapılmaz
        Dim strHostAddress As String = "https://sanalposprov.garanti.com.tr/VPServlet"

        Dim SecurityData As String = UCase(GetSHA1(strProvisionPassword + _strTerminalID))
        Dim HashData As String = UCase(GetSHA1(strOrderID + strTerminalID + strAmount + SecurityData))

        Dim doc As New System.Xml.XmlDocument
        Dim dec As System.Xml.XmlDeclaration
        dec = doc.CreateXmlDeclaration("1.0", "UTF-8", "yes")
        doc.AppendChild(dec)

        Dim GVPSRequest As System.Xml.XmlElement
        GVPSRequest = doc.CreateElement("GVPSRequest")
        doc.AppendChild(GVPSRequest)

        Dim Mode As System.Xml.XmlElement
        Mode = doc.CreateElement("Mode")
        Mode.AppendChild(doc.CreateTextNode(strMode))
        GVPSRequest.AppendChild(Mode)

        Dim Version As System.Xml.XmlElement
        Version = doc.CreateElement("Version")
        Version.AppendChild(doc.CreateTextNode(strVersion))
        GVPSRequest.AppendChild(Version)

        Dim Terminal As System.Xml.XmlElement
        Terminal = doc.CreateElement("Terminal")
        GVPSRequest.AppendChild(Terminal)

        Dim ProvUserID As System.Xml.XmlElement
        ProvUserID = doc.CreateElement("ProvUserID")
        ProvUserID.AppendChild(doc.CreateTextNode(strProvUserID))
        Terminal.AppendChild(ProvUserID)

        Dim HashData_ As System.Xml.XmlElement
        HashData_ = doc.CreateElement("HashData")
        HashData_.AppendChild(doc.CreateTextNode(HashData))
        Terminal.AppendChild(HashData_)

        Dim UserID As System.Xml.XmlElement
        UserID = doc.CreateElement("UserID")
        UserID.AppendChild(doc.CreateTextNode(strUserID))
        Terminal.AppendChild(UserID)

        Dim ID As System.Xml.XmlElement
        ID = doc.CreateElement("ID")
        ID.AppendChild(doc.CreateTextNode(strTerminalID))
        Terminal.AppendChild(ID)

        Dim MerchantID As System.Xml.XmlElement
        MerchantID = doc.CreateElement("MerchantID")
        MerchantID.AppendChild(doc.CreateTextNode(strMerchantID))
        Terminal.AppendChild(MerchantID)

        Dim Customer As System.Xml.XmlElement
        Customer = doc.CreateElement("Customer")
        GVPSRequest.AppendChild(Customer)

        Dim IPAddress As System.Xml.XmlElement
        IPAddress = doc.CreateElement("IPAddress")
        IPAddress.AppendChild(doc.CreateTextNode(strIPAddress))
        Customer.AppendChild(IPAddress)

        Dim EmailAddress As System.Xml.XmlElement
        EmailAddress = doc.CreateElement("EmailAddress")
        EmailAddress.AppendChild(doc.CreateTextNode(strEmailAddress))
        Customer.AppendChild(EmailAddress)

        Dim Card As System.Xml.XmlElement
        Card = doc.CreateElement("Card")
        GVPSRequest.AppendChild(Card)

        Dim Number As System.Xml.XmlElement
        Number = doc.CreateElement("Number")
        Number.AppendChild(doc.CreateTextNode(""))
        Card.AppendChild(Number)

        Dim ExpireDate As System.Xml.XmlElement
        ExpireDate = doc.CreateElement("ExpireDate")
        ExpireDate.AppendChild(doc.CreateTextNode(""))
        Card.AppendChild(ExpireDate)

        Dim CVV2 As System.Xml.XmlElement
        CVV2 = doc.CreateElement("CVV2")
        CVV2.AppendChild(doc.CreateTextNode(""))
        Card.AppendChild(CVV2)

        Dim Order As System.Xml.XmlElement
        Order = doc.CreateElement("Order")
        GVPSRequest.AppendChild(Order)

        Dim OrderID As System.Xml.XmlElement
        OrderID = doc.CreateElement("OrderID")
        OrderID.AppendChild(doc.CreateTextNode(strOrderID))
        Order.AppendChild(OrderID)

        Dim GroupID As System.Xml.XmlElement
        GroupID = doc.CreateElement("GroupID")
        GroupID.AppendChild(doc.CreateTextNode(""))
        Order.AppendChild(GroupID)

        Dim Description As System.Xml.XmlElement
        Description = doc.CreateElement("Description")
        Description.AppendChild(doc.CreateTextNode(""))
        Order.AppendChild(Description)

        Dim Transaction As System.Xml.XmlElement
        Transaction = doc.CreateElement("Transaction")
        GVPSRequest.AppendChild(Transaction)

        Dim Type As System.Xml.XmlElement
        Type = doc.CreateElement("Type")
        Type.AppendChild(doc.CreateTextNode(strType))
        Transaction.AppendChild(Type)

        Dim InstallmentCnt As System.Xml.XmlElement
        InstallmentCnt = doc.CreateElement("InstallmentCnt")
        InstallmentCnt.AppendChild(doc.CreateTextNode(strInstallmentCount))
        Transaction.AppendChild(InstallmentCnt)

        Dim Amount As System.Xml.XmlElement
        Amount = doc.CreateElement("Amount")
        Amount.AppendChild(doc.CreateTextNode(strAmount))
        Transaction.AppendChild(Amount)

        Dim CurrencyCode As System.Xml.XmlElement
        CurrencyCode = doc.CreateElement("CurrencyCode")
        CurrencyCode.AppendChild(doc.CreateTextNode(strCurrencyCode))
        Transaction.AppendChild(CurrencyCode)

        Dim CardholderPresentCode As System.Xml.XmlElement
        CardholderPresentCode = doc.CreateElement("CardholderPresentCode")
        CardholderPresentCode.AppendChild(doc.CreateTextNode(strCardholderPresentCode))
        Transaction.AppendChild(CardholderPresentCode)

        Dim MotoInd As System.Xml.XmlElement
        MotoInd = doc.CreateElement("MotoInd")
        MotoInd.AppendChild(doc.CreateTextNode(strMotoInd))
        Transaction.AppendChild(MotoInd)

        Dim _Description As System.Xml.XmlElement
        _Description = doc.CreateElement("Description")
        _Description.AppendChild(doc.CreateTextNode(""))
        Transaction.AppendChild(_Description)

        Dim OriginalRetrefNum As System.Xml.XmlElement
        OriginalRetrefNum = doc.CreateElement("OriginalRetrefNum")
        OriginalRetrefNum.AppendChild(doc.CreateTextNode(""))
        Transaction.AppendChild(OriginalRetrefNum)

        Dim CepBank As System.Xml.XmlElement
        CepBank = doc.CreateElement("CepBank")
        Transaction.AppendChild(CepBank)

        Dim GSMNumber As System.Xml.XmlElement
        GSMNumber = doc.CreateElement("GSMNumber")
        GSMNumber.AppendChild(doc.CreateTextNode(strGSMNumber))
        CepBank.AppendChild(GSMNumber)

        Dim PaymentType As System.Xml.XmlElement
        PaymentType = doc.CreateElement("PaymentType")
        PaymentType.AppendChild(doc.CreateTextNode(""))
        CepBank.AppendChild(PaymentType)

        Try

            Dim data As String = "data=" + doc.OuterXml

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

            txtResults1.Text = "Giden Talep :" & doc.OuterXml
            txtResults2.Text = "Gelen Yanıt :" & responseFromServer

        Catch ex As Exception
            txtResults2.Text = ex.Message
        End Try

    End Sub

End Class