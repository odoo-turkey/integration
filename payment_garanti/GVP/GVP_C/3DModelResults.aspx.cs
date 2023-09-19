using System;
using System.Net;
using System.Text;
using System.IO;
using System.Xml;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Security.Cryptography;

namespace $safeprojectname$
{
    public partial class _DModelResults : System.Web.UI.Page
    {
        protected void Page_Load(object sender, System.EventArgs e)
        {

            if (!Page.IsPostBack)
            {
                string strMode = Request.Form.Get("mode");
                string strApiVersion = Request.Form.Get("apiversion");
                string strTerminalProvUserID = Request.Form.Get("terminalprovuserid");
                string strType = Request.Form.Get("txntype");
                string strAmount = Request.Form.Get("txnamount");
                string strCurrencyCode = Request.Form.Get("txncurrencycode");
                string strInstallmentCount = Request.Form.Get("txninstallmentcount");
                string strTerminalUserID = Request.Form.Get("terminaluserid");
                string strOrderID = Request.Form.Get("oid");
                string strCustomeripaddress = Request.Form.Get("customeripaddress");
                string strcustomeremailaddress = Request.Form.Get("customeremailaddress");
                string strTerminalID = Request.Form.Get("clientid");
                string _strTerminalID = "0" + strTerminalID;
                string strTerminalMerchantID = Request.Form.Get("terminalmerchantid");
                string strStoreKey = "XXXXXXXX";
                //HASH doğrulaması için 3D Secure şifreniz
                string strProvisionPassword = "XXXXXXXX";
                //HASH doğrulaması için TerminalProvUserID şifresini tekrar yazıyoruz
                string strSuccessURL = Request.Form.Get("successurl");
                string strErrorURL = Request.Form.Get("errorurl");
                string strCardholderPresentCode = "13";
                //3D Model işlemde bu değer 13 olmalı
                string strMotoInd = "N";
                string strNumber = "";
                //Kart bilgilerinin boş gitmesi gerekiyor
                string strExpireDate = "";
                //Kart bilgilerinin boş gitmesi gerekiyor
                string strCVV2 = "";
                //Kart bilgilerinin boş gitmesi gerekiyor
                string strAuthenticationCode = Server.UrlEncode(Request.Form.Get("cavv"));
                string strSecurityLevel = Server.UrlEncode(Request.Form.Get("eci"));
                string strTxnID = Server.UrlEncode(Request.Form.Get("xid"));
                string strMD = Server.UrlEncode(Request.Form.Get("md"));
                string strMDStatus = Request.Form.Get("mdstatus");
                string strMDStatusText = Request.Form.Get("mderrormessage");
                string strHostAddress = "https://sanalposprov.garanti.com.tr/VPServlet";
                //Provizyon için xml'in post edileceği adres
                string SecurityData = GetSHA1(strProvisionPassword + _strTerminalID).ToUpper();
                string HashData = GetSHA1(strOrderID + strTerminalID + strAmount + SecurityData).ToUpper();
                //Daha kısıtlı bilgileri HASH ediyoruz.

                //strMDStatus.Equals(1)
                //"Tam Doğrulama"
                //strMDStatus.Equals(2)
                //"Kart Sahibi veya bankası sisteme kayıtlı değil"
                //strMDStatus.Equals(3)
                //"Kartın bankası sisteme kayıtlı değil"
                //strMDStatus.Equals(4)
                //"Doğrulama denemesi, kart sahibi sisteme daha sonra kayıt olmayı seçmiş"
                //strMDStatus.Equals(5)
                //"Doğrulama yapılamıyor"
                //strMDStatus.Equals(6)
                //"3-D Secure Hatası"
                //strMDStatus.Equals(7)
                //"Sistem Hatası"
                //strMDStatus.Equals(8)
                //"Bilinmeyen Kart No"
                //strMDStatus.Equals(0)
                //"Doğrulama Başarısız, 3-D Secure imzası geçersiz."

                //Hashdata kontrolü için bankadan dönen secure3dhash değeri alınıyor.
                string strHashData = Request.Form.Get("secure3dhash");
                string ValidateHashData = GetSHA1(strTerminalID + strOrderID + strAmount + strSuccessURL + strErrorURL + strType + strInstallmentCount + strStoreKey + SecurityData).ToUpper();

                //İlk gönderilen ve bankadan dönen HASH değeri yeni üretilenle eşleşiyorsa;

                if (strHashData == ValidateHashData)
                {
                    lblResult1.Text = "Sayısal Imza Geçerli";

                    //Tam Doğrulama, Kart Sahibi veya bankası sisteme kayıtlı değil, Kartın bankası sisteme kayıtlı değil
                    //Doğrulama denemesi, kart sahibi sisteme daha sonra kayıt olmayı seçmiş responselarını alan
                    //işlemler için Provizyon almaya çalışıyoruz

                    if (strMDStatus == "1" | strMDStatus == "2" | strMDStatus == "3" | strMDStatus == "4")
                    {
                        //Provizyona Post edilecek XML Şablonu
                        string strXML = null;
                        strXML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + "<GVPSRequest>" + "<Mode>" + strMode + "</Mode>" + "<Version>" + strApiVersion + "</Version>" + "<ChannelCode></ChannelCode>" + "<Terminal><ProvUserID>" + strTerminalProvUserID + "</ProvUserID><HashData>" + HashData + "</HashData><UserID>" + strTerminalUserID + "</UserID><ID>" + strTerminalID + "</ID><MerchantID>" + strTerminalMerchantID + "</MerchantID></Terminal>" + "<Customer><IPAddress>" + strCustomeripaddress + "</IPAddress><EmailAddress>" + strcustomeremailaddress + "</EmailAddress></Customer>" + "<Card><Number></Number><ExpireDate></ExpireDate><CVV2></CVV2></Card>" + "<Order><OrderID>" + strOrderID + "</OrderID><GroupID></GroupID><AddressList><Address><Type>B</Type><Name></Name><LastName></LastName><Company></Company><Text></Text><District></District><City></City><PostalCode></PostalCode><Country></Country><PhoneNumber></PhoneNumber></Address></AddressList></Order>" + "<Transaction>" + "<Type>" + strType + "</Type><InstallmentCnt>" + strInstallmentCount + "</InstallmentCnt><Amount>" + strAmount + "</Amount><CurrencyCode>" + strCurrencyCode + "</CurrencyCode><CardholderPresentCode>" + strCardholderPresentCode + "</CardholderPresentCode><MotoInd>" + strMotoInd + "</MotoInd>" + "<Secure3D><AuthenticationCode>" + strAuthenticationCode + "</AuthenticationCode><SecurityLevel>" + strSecurityLevel + "</SecurityLevel><TxnID>" + strTxnID + "</TxnID><Md>" + strMD + "</Md></Secure3D>" + "</Transaction>" + "</GVPSRequest>";

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

                            //00 ReasonCode döndüğünde işlem başarılıdır. Müşteriye başarılı veya başarısız şeklinde göstermeniz tavsiye edilir. (Fraud riski)
                            if (responseFromServer.Contains("<ReasonCode>00</ReasonCode>"))
                            {
                                lblResult2.Text = strMDStatusText;
                                lblResult3.Text = "İşlem Başarılı";
                            }
                            else
                            {
                                lblResult2.Text = strMDStatusText;
                                lblResult3.Text = "İşlem Başarısız";
                            }

                        }
                        catch (Exception ex)
                        {
                            lblResult2.Text = strMDStatusText;
                            lblResult3.Text = ex.Message;
                        }

                    }
                    else
                    {
                        lblResult2.Text = strMDStatusText;
                        lblResult3.Text = "İşlem Başarısız";

                    }

                }
                else
                {
                    lblResult1.Text = "Güvenlik Uyarısı. Sayısal Imza Geçerli Degil";
                    lblResult2.Text = strMDStatusText;
                    lblResult3.Text = " İşlem Başarısız";
                }

                //Dönen değerlerin detayını almak isterseniz alttaki kod bloğunu kullanabilirsiniz.
                //IEnumerator f = Request.Form.GetEnumerator();
                //while (f.MoveNext())
                //{
                //    string xkey = (string)f.Current;
                //    string xval = Request.Form.Get(xkey);
                //    lblResult2.Text = lblResult2.Text + (xkey + " : " + xval);
                //}

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