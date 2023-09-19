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
    public partial class _DPay : System.Web.UI.Page
    {
        protected void Page_Load(object sender, EventArgs e)
        {
            if (!Page.IsPostBack)
            {
                string strMode = "PROD";
                string strApiVersion = "v0.01";
                string strTerminalProvUserID = "PROVAUT";
                string strType = "sales";
                string strAmount = "100"; //İşlem Tutarı 1.00 TL için 100 gönderilmeli
                string strCurrencyCode = "949";
                string strInstallmentCount = ""; //Taksit Sayısı. Boş gönderilirse taksit yapılmaz
                string strTerminalUserID = "xxxxxx";
                string strOrderID = "deneme";  //her işlemde farklı bir değer gönderilmeli 
                string strCustomeripaddress = Request.UserHostAddress; //Kullanıcının IP adresini alır
                string strcustomeremailaddress = "eticaret@garanti.com.tr";
                string strTerminalID = "XXXXXXXX"; //TerminalID yazılmalı.
                string _strTerminalID = "0" + strTerminalID;
                string strTerminalMerchantID = "XXXXXXXX";
                string strStoreKey = "XXXXXXXX"; //3D Secure şifresi
                string strProvisionPassword = "XXXXXXXX"; //TerminalProvUserID şifresi
                string strSuccessURL = "https://<sunucu_adresi>/3DPayResults.aspx";
                string strErrorURL = "https://<sunucu_adresi>/3DPayResults.aspx";
                string SecurityData = GetSHA1(strProvisionPassword + _strTerminalID).ToUpper();
                string HashData = GetSHA1(strTerminalID + strOrderID + strAmount + strSuccessURL + strErrorURL + strType + strInstallmentCount + strStoreKey + SecurityData).ToUpper();

                mode.Value = strMode;
                apiversion.Value = strApiVersion;
                terminalprovuserid.Value = strTerminalProvUserID;
                terminaluserid.Value = strTerminalUserID;
                terminalmerchantid.Value = strTerminalMerchantID;
                txntype.Value = strType;
                txnamount.Value = strAmount;
                txncurrencycode.Value = strCurrencyCode;
                txninstallmentcount.Value = strInstallmentCount;
                customeremailaddress.Value = strcustomeremailaddress;
                customeripaddress.Value = strCustomeripaddress;
                orderid.Value = strOrderID;
                terminalid.Value = strTerminalID;
                successurl.Value = strSuccessURL;
                errorurl.Value = strErrorURL;
                secure3dhash.Value = HashData;
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
    }
}