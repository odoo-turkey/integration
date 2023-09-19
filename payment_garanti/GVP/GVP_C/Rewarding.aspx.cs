using System;
using System.Net;
using System.Text;
using System.IO;
using System.Xml;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Security.Cryptography;

namespace $safeprojectname$
{
    public partial class Rewarding : System.Web.UI.Page
    {
        protected void Page_Load(object sender, EventArgs e)
        {
            if (!Page.IsPostBack)
            {
            }
        }

        public string GetSHA1(string SHA1Data)
        {
            SHA1 sha = new SHA1CryptoServiceProvider();
            string HashedPassword = SHA1Data;
            byte[] hashbytes = Encoding.GetEncoding("ISO-8859-9").GetBytes(HashedPassword);
            byte[] inputbytes = sha.ComputeHash(hashbytes);
            return GetHexaDecimal(inputbytes);
        }

        public string GetHexaDecimal(byte[] bytes)
        {
            StringBuilder s = new StringBuilder();
            int length = bytes.Length;
            for (int n = 0; n <= length - 1; n++)
            {
                s.Append(String.Format("{0,2:x}", bytes[n]).Replace(" ", "0"));
            }
            return s.ToString();
        }

        protected void cmdSubmit_Click(object sender, EventArgs e)
        {
            string strMode = "PROD";
            string strVersion = "v0.01";
            string strTerminalID = txtTerminalID.Text;
            string _strTerminalID = "0" + txtTerminalID.Text;
            string strProvUserID = "PROVAUT";
            string strProvisionPassword = txtPassword.Text;
            string strUserID = txtUserID.Text;
            string strMerchantID = txtMerchantID.Text;
            string strIPAddress = "192.168.1.1";
            string strEmailAddress = "test@test.com";
            string strOrderID = "DENEME";
            string strInstallmentCnt = ""; //Taksit sayısı peşin işlem için boş gönderilmeli.
            string strNumber = txtCCNumber.Text;
            string strExpireDate = "";
            string strCVV2 = "";
            string strAmount = "100";
            string strType = "rewardinq";
            string strCurrencyCode = "949";
            string strCardholderPresentCode = "0";
            string strMotoInd = "N";
            string strHostAddress = "https://sanalposprov.garanti.com.tr/VPServlet";

            string SecurityData = GetSHA1(strProvisionPassword + _strTerminalID).ToUpper();
            string HashData = GetSHA1(strOrderID + strTerminalID + strNumber + strAmount + SecurityData).ToUpper();

            System.Xml.XmlDocument doc = new System.Xml.XmlDocument();
            System.Xml.XmlDeclaration dec = null;
            dec = doc.CreateXmlDeclaration("1.0", "UTF-8", "yes");
            doc.AppendChild(dec);

            System.Xml.XmlElement GVPSRequest = null;
            GVPSRequest = doc.CreateElement("GVPSRequest");
            doc.AppendChild(GVPSRequest);

            System.Xml.XmlElement Mode = null;
            Mode = doc.CreateElement("Mode");
            Mode.AppendChild(doc.CreateTextNode(strMode));
            GVPSRequest.AppendChild(Mode);

            System.Xml.XmlElement Version = null;
            Version = doc.CreateElement("Version");
            Version.AppendChild(doc.CreateTextNode(strVersion));
            GVPSRequest.AppendChild(Version);

            System.Xml.XmlElement Terminal = null;
            Terminal = doc.CreateElement("Terminal");
            GVPSRequest.AppendChild(Terminal);

            System.Xml.XmlElement ProvUserID = null;
            ProvUserID = doc.CreateElement("ProvUserID");
            ProvUserID.AppendChild(doc.CreateTextNode(strProvUserID));
            Terminal.AppendChild(ProvUserID);

            System.Xml.XmlElement HashData_ = null;
            HashData_ = doc.CreateElement("HashData");
            HashData_.AppendChild(doc.CreateTextNode(HashData));
            Terminal.AppendChild(HashData_);

            System.Xml.XmlElement UserID = null;
            UserID = doc.CreateElement("UserID");
            UserID.AppendChild(doc.CreateTextNode(strUserID));
            Terminal.AppendChild(UserID);

            System.Xml.XmlElement ID = null;
            ID = doc.CreateElement("ID");
            ID.AppendChild(doc.CreateTextNode(strTerminalID));
            Terminal.AppendChild(ID);

            System.Xml.XmlElement MerchantID = null;
            MerchantID = doc.CreateElement("MerchantID");
            MerchantID.AppendChild(doc.CreateTextNode(strMerchantID));
            Terminal.AppendChild(MerchantID);

            System.Xml.XmlElement Customer = null;
            Customer = doc.CreateElement("Customer");
            GVPSRequest.AppendChild(Customer);

            System.Xml.XmlElement IPAddress = null;
            IPAddress = doc.CreateElement("IPAddress");
            IPAddress.AppendChild(doc.CreateTextNode(strIPAddress));
            Customer.AppendChild(IPAddress);

            System.Xml.XmlElement EmailAddress = null;
            EmailAddress = doc.CreateElement("EmailAddress");
            EmailAddress.AppendChild(doc.CreateTextNode(strEmailAddress));
            Customer.AppendChild(EmailAddress);

            System.Xml.XmlElement Card = null;
            Card = doc.CreateElement("Card");
            GVPSRequest.AppendChild(Card);

            System.Xml.XmlElement Number = null;
            Number = doc.CreateElement("Number");
            Number.AppendChild(doc.CreateTextNode(strNumber));
            Card.AppendChild(Number);

            System.Xml.XmlElement ExpireDate = null;
            ExpireDate = doc.CreateElement("ExpireDate");
            ExpireDate.AppendChild(doc.CreateTextNode(strExpireDate));
            Card.AppendChild(ExpireDate);

            System.Xml.XmlElement CVV2 = null;
            CVV2 = doc.CreateElement("CVV2");
            CVV2.AppendChild(doc.CreateTextNode(strCVV2));
            Card.AppendChild(ExpireDate);

            System.Xml.XmlElement Order = null;
            Order = doc.CreateElement("Order");
            GVPSRequest.AppendChild(Order);

            System.Xml.XmlElement OrderID = null;
            OrderID = doc.CreateElement("OrderID");
            OrderID.AppendChild(doc.CreateTextNode(strOrderID));
            Order.AppendChild(OrderID);

            System.Xml.XmlElement GroupID = null;
            GroupID = doc.CreateElement("GroupID");
            GroupID.AppendChild(doc.CreateTextNode(""));
            Order.AppendChild(GroupID);

            System.Xml.XmlElement Description = null;
            Description = doc.CreateElement("Description");
            Description.AppendChild(doc.CreateTextNode(""));
            Order.AppendChild(Description);

            System.Xml.XmlElement Transaction = null;
            Transaction = doc.CreateElement("Transaction");
            GVPSRequest.AppendChild(Transaction);

            System.Xml.XmlElement Type = null;
            Type = doc.CreateElement("Type");
            Type.AppendChild(doc.CreateTextNode(strType));
            Transaction.AppendChild(Type);

            System.Xml.XmlElement InstallmentCnt = null;
            InstallmentCnt = doc.CreateElement("InstallmentCnt");
            InstallmentCnt.AppendChild(doc.CreateTextNode("strInstallmentCnt"));
            Transaction.AppendChild(InstallmentCnt);

            System.Xml.XmlElement Amount = null;
            Amount = doc.CreateElement("Amount");
            Amount.AppendChild(doc.CreateTextNode(strAmount));
            Transaction.AppendChild(Amount);

            System.Xml.XmlElement CurrencyCode = null;
            CurrencyCode = doc.CreateElement("CurrencyCode");
            CurrencyCode.AppendChild(doc.CreateTextNode(strCurrencyCode));
            Transaction.AppendChild(CurrencyCode);

            System.Xml.XmlElement CardholderPresentCode = null;
            CardholderPresentCode = doc.CreateElement("CardholderPresentCode");
            CardholderPresentCode.AppendChild(doc.CreateTextNode(strCardholderPresentCode));
            Transaction.AppendChild(CardholderPresentCode);

            System.Xml.XmlElement MotoInd = null;
            MotoInd = doc.CreateElement("MotoInd");
            MotoInd.AppendChild(doc.CreateTextNode(strMotoInd));
            Transaction.AppendChild(MotoInd);

            System.Xml.XmlElement _Description = null;
            _Description = doc.CreateElement("Description");
            _Description.AppendChild(doc.CreateTextNode(""));
            Transaction.AppendChild(_Description);

            System.Xml.XmlElement OriginalRetrefNum = null;
            OriginalRetrefNum = doc.CreateElement("OriginalRetrefNum");
            OriginalRetrefNum.AppendChild(doc.CreateTextNode(""));
            Transaction.AppendChild(OriginalRetrefNum);

            try
            {
                string data = "data=" + doc.OuterXml;

                WebRequest _WebRequest = WebRequest.Create(strHostAddress);
                _WebRequest.Method = "POST";

                byte[] byteArray = Encoding.UTF8.GetBytes(data);
                _WebRequest.ContentType = "application/x-www-form-urlencoded";
                _WebRequest.ContentLength = byteArray.Length;

                Stream dataStream = _WebRequest.GetRequestStream();
                dataStream.Write(byteArray, 0, byteArray.Length);
                dataStream.Close();

                WebResponse _WebResponse = _WebRequest.GetResponse();
                Console.WriteLine(((HttpWebResponse)_WebResponse).StatusDescription);
                dataStream = _WebResponse.GetResponseStream();

                StreamReader reader = new StreamReader(dataStream);
                string responseFromServer = reader.ReadToEnd();

                Console.WriteLine(responseFromServer);

                txtResults.Text = "Gelen Yanıt :" + responseFromServer;
            }
            catch (Exception ex)
            {
                txtResults.Text = ex.Message;
            }
        }
    }
}
