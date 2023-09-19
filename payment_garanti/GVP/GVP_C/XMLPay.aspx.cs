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
    public partial class CCPay : System.Web.UI.Page
    {
        protected void Page_Load(object sender, EventArgs e)
        {
            if (!Page.IsPostBack){
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
            string strTerminalID = "XXXXXXXX"; //8 Haneli TerminalID yazılmalı.
            string _strTerminalID = "0" + strTerminalID;
            string strProvUserID = "PROVAUT";
            string strProvisionPassword = "XXXXXXXX"; //TerminalProvUserID şifresi
            string strUserID = "XXXXXX";
            string strMerchantID = "XXXXXXXX"; //Üye İşyeri Numarası
            string strIPAddress = Request.UserHostAddress; //Kullanıcının IP adresini alır
            string strEmailAddress = "eticaret@garanti.com.tr";
            string strOrderID = "DENEME";
            string strNumber = txtCCNumber.Text;
            string strExpireDate = txtExpDate.Text;
            string strCVV2 = txtCVV2.Text;
            string strAmount = "100"; //İşlem Tutarı 1.00 TL için 100 gönderilmeli
            string strType = "sales";
            string strCurrencyCode = "949";
            string strCardholderPresentCode = "0";
            string strMotoInd = "N";
            string strInstallmentCount = "";
            string strHostAddress = "https://sanalposprov.garanti.com.tr/VPServlet";

            string SecurityData = GetSHA1(strProvisionPassword + _strTerminalID).ToUpper();
            string HashData = GetSHA1(strOrderID + strTerminalID + strNumber + strAmount + SecurityData).ToUpper();

            string strXML = null;
            strXML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + "<GVPSRequest>" + "<Mode>" + strMode + "</Mode>" + "<Version>" + strVersion + "</Version>" + "<Terminal><ProvUserID>" + strProvUserID + "</ProvUserID><HashData>" + HashData + "</HashData><UserID>" + strUserID + "</UserID><ID>" + strTerminalID + "</ID><MerchantID>" + strMerchantID + "</MerchantID></Terminal>" + "<Customer><IPAddress>" + strIPAddress + "</IPAddress><EmailAddress>" + strEmailAddress + "</EmailAddress></Customer>" + "<Card><Number>" + strNumber + "</Number><ExpireDate>" + strExpireDate + "</ExpireDate><CVV2>" + strCVV2 + "</CVV2></Card>" + "<Order><OrderID>" + strOrderID + "</OrderID><GroupID></GroupID><AddressList><Address><Type>S</Type><Name></Name><LastName></LastName><Company></Company><Text></Text><District></District><City></City><PostalCode></PostalCode><Country></Country><PhoneNumber></PhoneNumber></Address></AddressList></Order>" + "<Transaction>" + "<Type>" + strType + "</Type><InstallmentCnt>" + strInstallmentCount + "</InstallmentCnt><Amount>" + strAmount + "</Amount><CurrencyCode>" + strCurrencyCode + "</CurrencyCode><CardholderPresentCode>" + strCardholderPresentCode + "</CardholderPresentCode><MotoInd>" + strMotoInd + "</MotoInd>" + "</Transaction>" + "</GVPSRequest>";

            try
            {
                string data = "data=" + strXML;

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

                //Müşteriye gösterilebilir ama Fraud riski açısından bu değerleri göstermeyelim.
                //responseFromServer

                //GVPSResponse XML'in değerlerini okuyoruz. İstediğiniz geri dönüş değerlerini gösterebilirsiniz.
                string XML = responseFromServer;
                XmlDocument xDoc = new XmlDocument();
                xDoc.LoadXml(XML);

                //ReasonCode
                XmlElement xElement1 = xDoc.SelectSingleNode("//GVPSResponse/Transaction/Response/ReasonCode") as XmlElement;
                //lblResult2.Text = xElement1.InnerText;

                //Message
                //XmlElement xElement2 = xDoc.SelectSingleNode("//GVPSResponse/Transaction/Response/Message") as XmlElement;
                //lblResult2.Text = xElement2.InnerText;

                //ErrorMsg
                XmlElement xElement3 = xDoc.SelectSingleNode("//GVPSResponse/Transaction/Response/ErrorMsg") as XmlElement;
                lblResult2.Text = xElement3.InnerText;

                //00 ReasonCode döndüğünde işlem başarılıdır. Müşteriye başarılı veya başarısız şeklinde göstermeniz tavsiye edilir. (Fraud riski)
                if (xElement1.InnerText == "00")
                {
                    lblResult3.Text = "İşlem Başarılı";
                }
                else
                {
                    lblResult3.Text = "İşlem Başarısız";
                }

            }
            catch (Exception ex)
            {
                lblResult3.Text = ex.Message;
            }

        }

    }
}