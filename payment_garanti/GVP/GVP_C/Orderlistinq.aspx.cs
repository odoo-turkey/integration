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
    public partial class Orderlistinq : System.Web.UI.Page
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
            string strStartDate = txtStartDate.Text;
            string strEndDate = txtEndDate.Text;
            string strAmount = "1";
            string strType = "orderlistinq";
            string strCurrencyCode = "949";
            string strCardholderPresentCode = "0";
            string strMotoInd = "N";
            string strHostAddress = "https://sanalposprov.garanti.com.tr/VPServlet";

            string SecurityData = GetSHA1(strProvisionPassword + _strTerminalID).ToUpper();
            string HashData = GetSHA1(strTerminalID + strAmount + SecurityData).ToUpper();

            string strXML = null;
            strXML = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?><GVPSRequest><Mode>" + strMode + "</Mode><Version>" + strVersion + "</Version><Terminal><ProvUserID>" + strProvUserID + "</ProvUserID><HashData>" + HashData + "</HashData><UserID>" + strUserID + "</UserID><ID>" + strTerminalID + "</ID><MerchantID>" + strMerchantID + "</MerchantID></Terminal><Customer><IPAddress>" + strIPAddress + "</IPAddress><EmailAddress></EmailAddress></Customer><Card><Number></Number><ExpireDate></ExpireDate><CVV2></CVV2></Card><Order><OrderID></OrderID><GroupID></GroupID><StartDate>" + strStartDate + "</StartDate><EndDate>" + strEndDate + "</EndDate></Order><Transaction><Type>" + strType + "</Type><InstallmentCnt></InstallmentCnt><Amount>" + strAmount + "</Amount><CurrencyCode>" + strCurrencyCode + "</CurrencyCode><CardholderPresentCode>" + strCardholderPresentCode + "</CardholderPresentCode><MotoInd>" + strMotoInd + "</MotoInd></Transaction></GVPSRequest>";

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

                lblResult1.Text = responseFromServer;

            }
            catch (Exception ex)
            {
                lblResult1.Text = ex.Message;
            }

        }

    }
}
